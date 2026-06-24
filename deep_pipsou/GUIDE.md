# Guide de développement — Deep Pipsou
### Un programme qui apprend à jouer aux échecs par lui-même

---

## Sommaire

1. [Vision d'ensemble](#1-vision-densemble)
2. [Prérequis et installation](#2-prérequis-et-installation)
3. [Interface avec chess.py](#3-interface-avec-chesspy)
4. [Représentation de l'état du jeu](#4-représentation-de-létat-du-jeu)
5. [Le réseau de neurones](#5-le-réseau-de-neurones)
6. [Le joueur de base : l'agent aléatoire](#6-le-joueur-de-base--lagent-aléatoire)
7. [La boucle de self-play](#7-la-boucle-de-self-play)
8. [L'entraînement du réseau](#8-lentraînement-du-réseau)
9. [MCTS — Monte Carlo Tree Search](#9-mcts--monte-carlo-tree-search)
10. [Export et import du modèle](#10-export-et-import-du-modèle)
11. [Interface de jeu externe](#11-interface-de-jeu-externe)
12. [Structure des fichiers à créer](#12-structure-des-fichiers-à-créer)
13. [Feuille de route — étapes concrètes](#13-feuille-de-route--étapes-concrètes)

---

## 1. Vision d'ensemble

### Ce que Deep Pipsou va faire

Deep Pipsou est un agent RL (*Reinforcement Learning*) qui apprend à jouer aux échecs exclusivement par **self-play** : il joue contre lui-même des milliers de parties, et chaque résultat (victoire, défaite, nulle) lui sert de signal d'apprentissage. Aucune connaissance humaine n'est injectée — ni ouvertures, ni valeurs de pièces programmatiques, ni règles heuristiques. Seul chess.py lui dit ce qui est légal.

Cette approche s'appelle **AlphaZero** (DeepMind, 2017). Nous allons en coder une version simplifiée mais fonctionnelle.

### L'idée centrale

```
┌─────────────────────────────────────────────────────────┐
│                    BOUCLE D'ENTRAÎNEMENT                │
│                                                         │
│  ┌──────────┐    parties    ┌──────────────────────┐    │
│  │ Modèle   │ ──────────── ▶│    Self-play         │    │
│  │ courant  │               │ (Deep Pipsou vs lui) │    │
│  └──────────┘               └──────────┬───────────┘    │
│       ▲                                │                 │
│       │   mise à jour                  │ trajectoires    │
│       │   des poids                    │ (état, coup,    │
│  ┌────┴─────┐                          │  résultat)      │
│  │ Training │ ◀────────────────────────┘                 │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘
```

Chaque "trajectoire" est une séquence de triplets `(état du plateau, coup joué, résultat final)`. Le réseau apprend à mieux évaluer les positions et à choisir de meilleurs coups à chaque itération.

### Les deux têtes du réseau

Le réseau de neurones a **deux sorties** :

- **La tête de valeur** (*value head*) : un scalaire entre -1 et +1 qui estime la probabilité de gagner depuis cet état.
- **La tête de politique** (*policy head*) : une distribution de probabilités sur tous les coups possibles. Le réseau estime quels coups sont les plus prometteurs.

---

## 2. Prérequis et installation

### Librairies Python nécessaires

```
numpy       — déjà utilisé par chess.py
torch       — réseau de neurones (PyTorch)
```

Installation :
```bash
pip install torch numpy
```

PyTorch est choisi pour sa flexibilité. Il permet de déboguer facilement et d'inspecter les gradients.

---

## 3. Interface avec chess.py

Avant de toucher au RL, il faut maîtriser l'interface existante. Voici ce que Deep Pipsou utilisera.

### 3.1 Créer une partie

```python
import sys
sys.path.insert(0, "../pieces_board")
from chess import board, rules

game = board()
current_board = game.create_board()  # plateau initial (numpy 8x8)
```

### 3.2 Obtenir tous les coups légaux depuis un état

chess.py ne fournit pas de méthode `get_all_legal_moves()` directement. Il faut la construire. C'est la **première chose à coder** dans Deep Pipsou.

```python
def get_legal_moves(game: board, current_board) -> list[tuple]:
    """
    Renvoie la liste de tous les coups légaux pour le joueur dont c'est le tour.
    Chaque coup est un tuple ('Pe2', 'e4') tel qu'attendu par move_piece().
    """
    legal = []
    current_player = game.turn  # "white" ou "black"
    is_white = (current_player == "white")

    for row in range(8):
        for col in range(8):
            piece = current_board[row, col]
            if piece == " ":
                continue
            if piece.isupper() != is_white:
                continue

            origin_sq = _index_to_algebraic(row, col)  # "e2", "a1", etc.
            piece_obj = game._get_piece_object(piece)
            candidate_dests = piece_obj.possible_moves(origin_sq, current_board, game.last_move)

            for dest in candidate_dests:
                move = (piece + origin_sq, dest)
                try:
                    r = rules(move, game.last_move, current_board)
                    if r.check_all():
                        legal.append(move)
                except:
                    pass

    return legal
```

> **Note** : `_index_to_algebraic` et `_get_piece_object` sont déjà dans chess.py. Il faudra les importer ou les réutiliser.

### 3.3 Jouer un coup

```python
new_board = game.move_piece(current_board, ("Pe2", "e4"))
# game.turn bascule automatiquement via last_move
```

### 3.4 Détecter la fin de partie

```python
game_over, message, winner = game.check_game_end(current_board)
# winner : "white", "black", ou "draw"
```

### 3.5 Le signal de récompense

On définit la récompense finale depuis le point de vue d'un joueur :
- Victoire → **+1**
- Défaite → **-1**
- Nulle → **0**

---

## 4. Représentation de l'état du jeu

Le réseau de neurones ne comprend pas les chaînes de caractères. Il faut **encoder le plateau** en tenseur numérique.

### 4.1 Encodage par plans binaires (standard AlphaZero)

On représente le plateau comme un tenseur de forme `(12, 8, 8)` :
- 12 plans, un par type de pièce (6 pièces × 2 couleurs)
- Chaque plan est une matrice 8×8 de 0/1 : 1 si la pièce est présente sur la case, 0 sinon.

```
Plan 0  → Pions blancs   (P)
Plan 1  → Tours blanches (R)
Plan 2  → Cavaliers blancs (N)
Plan 3  → Fous blancs   (B)
Plan 4  → Dames blanches (Q)
Plan 5  → Rois blancs   (K)
Plan 6  → Pions noirs   (p)
Plan 7  → Tours noires  (r)
Plan 8  → Cavaliers noirs (n)
Plan 9  → Fous noirs    (b)
Plan 10 → Dames noires  (q)
Plan 11 → Rois noirs    (k)
```

```python
import numpy as np
import torch

PIECE_TO_PLANE = {
    'P': 0, 'R': 1, 'N': 2, 'B': 3, 'Q': 4, 'K': 5,
    'p': 6, 'r': 7, 'n': 8, 'b': 9, 'q': 10, 'k': 11,
}

def encode_board(current_board: np.ndarray) -> torch.Tensor:
    """Encode un plateau 8x8 en tenseur (12, 8, 8)."""
    planes = np.zeros((12, 8, 8), dtype=np.float32)
    for row in range(8):
        for col in range(8):
            piece = current_board[row, col]
            if piece != " ":
                plane_idx = PIECE_TO_PLANE[piece]
                planes[plane_idx, row, col] = 1.0
    return torch.tensor(planes)
```

### 4.2 Encodage des coups (espace d'actions)

Un coup est défini par une case de départ et une case d'arrivée : 64 × 64 = **4096 actions possibles**.

La plupart sont illégales, mais on masque les illégales au moment du choix. L'avantage : l'espace d'actions est fixe, ce qui simplifie le réseau.

```python
def move_to_index(move: tuple) -> int:
    """Convertit un coup ('Pe2', 'e4') en entier [0, 4095]."""
    from_sq = move[0][-2:]  # 'e2'
    to_sq = move[1][-2:]    # 'e4'
    from_idx = (ord(from_sq[0]) - ord('a')) + (int(from_sq[1]) - 1) * 8
    to_idx   = (ord(to_sq[0])  - ord('a')) + (int(to_sq[1])  - 1) * 8
    return from_idx * 64 + to_idx

def index_to_move_squares(idx: int) -> tuple[str, str]:
    """Inverse : entier → (case_départ, case_arrivée)."""
    from_idx = idx // 64
    to_idx   = idx % 64
    from_sq = chr(ord('a') + from_idx % 8) + str(from_idx // 8 + 1)
    to_sq   = chr(ord('a') + to_idx % 8)   + str(to_idx // 8 + 1)
    return from_sq, to_sq
```

---

## 5. Le réseau de neurones

### 5.1 Architecture

On utilise un **réseau convolutif** (CNN), adapté aux grilles spatiales. L'architecture proposée est délibérément simple pour commencer :

```
Entrée : (batch, 12, 8, 8)
    │
    ▼
┌─────────────────────┐
│  Bloc convolutif x4  │  Conv2d(12→64, 3×3) + BN + ReLU (répété 4 fois)
└─────────────────────┘
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
┌──────────────┐                  ┌──────────────┐
│  Tête Policy │                  │  Tête Value  │
│  Conv(64→2)  │                  │  Conv(64→1)  │
│  + flatten   │                  │  + Linear    │
│  + Linear    │                  │  + tanh      │
│  → 4096      │                  │  → scalaire  │
│  (logits)    │                  │  ∈ [-1, 1]   │
└──────────────┘                  └──────────────┘
```

### 5.2 Code PyTorch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    """Bloc résiduel : sortie = f(x) + x."""
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn1   = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.bn2   = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        return F.relu(x + residual)


class DeepPipsouNet(nn.Module):
    """
    Réseau principal de Deep Pipsou.
    Entrée  : tenseur (batch, 12, 8, 8) — plateau encodé
    Sorties : (policy_logits, value)
        - policy_logits : (batch, 4096) — scores bruts pour chaque coup possible
        - value         : (batch, 1)    — évaluation de la position ∈ [-1, 1]
    """
    def __init__(self, num_channels: int = 64, num_res_blocks: int = 4):
        super().__init__()

        # Couche d'entrée
        self.input_conv = nn.Sequential(
            nn.Conv2d(12, num_channels, 3, padding=1),
            nn.BatchNorm2d(num_channels),
            nn.ReLU(),
        )

        # Corps résiduel
        self.res_blocks = nn.Sequential(
            *[ResidualBlock(num_channels) for _ in range(num_res_blocks)]
        )

        # Tête de politique
        self.policy_conv = nn.Conv2d(num_channels, 2, 1)
        self.policy_bn   = nn.BatchNorm2d(2)
        self.policy_fc   = nn.Linear(2 * 8 * 8, 4096)

        # Tête de valeur
        self.value_conv  = nn.Conv2d(num_channels, 1, 1)
        self.value_bn    = nn.BatchNorm2d(1)
        self.value_fc1   = nn.Linear(8 * 8, 64)
        self.value_fc2   = nn.Linear(64, 1)

    def forward(self, x):
        x = self.input_conv(x)
        x = self.res_blocks(x)

        # Politique
        p = F.relu(self.policy_bn(self.policy_conv(x)))
        p = p.view(p.size(0), -1)
        policy_logits = self.policy_fc(p)

        # Valeur
        v = F.relu(self.value_bn(self.value_conv(x)))
        v = v.view(v.size(0), -1)
        v = F.relu(self.value_fc1(v))
        value = torch.tanh(self.value_fc2(v))

        return policy_logits, value
```

**Pourquoi des blocs résiduels ?**
Les connexions résiduelles (`x + f(x)`) évitent le problème de disparition du gradient lors de l'entraînement sur de nombreuses couches. AlphaZero utilise 19 à 39 de ces blocs ; on commence avec 4.

---

## 6. Le joueur de base : l'agent aléatoire

Avant d'entraîner quoi que ce soit, il faut un **agent aléatoire** fonctionnel. Il sert de :
1. Adversaire initial pour tester l'infrastructure
2. Référence de performance minimale (un agent entraîné doit le battre)

```python
import random

class RandomAgent:
    def select_move(self, legal_moves: list) -> tuple:
        """Choisit un coup aléatoire parmi les coups légaux."""
        return random.choice(legal_moves)
```

Tester l'infrastructure complète avec deux `RandomAgent` avant d'implémenter quoi que ce soit d'autre.

---

## 7. La boucle de self-play

C'est le cœur du système. Elle génère les données d'entraînement.

### 7.1 Déroulement d'une partie

```
État initial
     │
     ▼
┌────────────────────────────────────────────────────┐
│  TANT QUE la partie n'est pas terminée :           │
│                                                    │
│  1. Encoder l'état courant → tenseur               │
│  2. Appeler le réseau → (policy_logits, value)     │
│  3. Appliquer le masque des coups légaux           │
│  4. Utiliser MCTS (ou directement la policy)       │
│     pour choisir un coup                           │
│  5. Enregistrer (state_tensor, move_idx, ?)        │
│  6. Jouer le coup → nouvel état                    │
└────────────────────────────────────────────────────┘
     │
     ▼
Fin de partie → résultat : +1, -1 ou 0
     │
     ▼
Remplir rétrospectivement la récompense de chaque
triplet enregistré selon la couleur du joueur
```

### 7.2 Code de la boucle de self-play

```python
def play_one_game(model: DeepPipsouNet, device) -> list[dict]:
    """
    Joue une partie en self-play.
    Retourne une liste de dicts {"state", "move_idx", "reward"}.
    """
    game = board()
    current_board = game.create_board()
    history = []  # (encoded_state, move_index, couleur_joueur)

    while True:
        game_over, _, winner = game.check_game_end(current_board)
        if game_over:
            break

        legal_moves = get_legal_moves(game, current_board)
        if not legal_moves:
            break

        # Encoder l'état
        state_tensor = encode_board(current_board).unsqueeze(0).to(device)

        # Obtenir les logits de la policy
        with torch.no_grad():
            policy_logits, _ = model(state_tensor)

        # Masque : mettre -inf sur les coups illégaux
        mask = torch.full((4096,), float('-inf'))
        for move in legal_moves:
            mask[move_to_index(move)] = 0.0
        masked_logits = policy_logits.squeeze(0) + mask.to(device)
        probs = torch.softmax(masked_logits, dim=0).cpu().numpy()

        # Choisir un coup (avec un peu d'exploration : sampling)
        chosen_idx = int(np.random.choice(4096, p=probs))

        # Retrouver le coup correspondant dans legal_moves
        # (on vérifie que l'index correspond bien à un coup légal)
        chosen_move = None
        for move in legal_moves:
            if move_to_index(move) == chosen_idx:
                chosen_move = move
                break
        if chosen_move is None:
            chosen_move = random.choice(legal_moves)  # fallback

        history.append({
            "state": state_tensor.squeeze(0).cpu(),
            "move_idx": move_to_index(chosen_move),
            "player": game.turn,  # "white" ou "black"
        })

        current_board = game.move_piece(current_board, chosen_move)

    # Attribuer les récompenses rétrospectivement
    reward_map = {"white": 0.0, "black": 0.0, "draw": 0.0}
    if winner == "white":
        reward_map = {"white": 1.0, "black": -1.0}
    elif winner == "black":
        reward_map = {"white": -1.0, "black": 1.0}

    training_samples = []
    for record in history:
        training_samples.append({
            "state":    record["state"],
            "move_idx": record["move_idx"],
            "reward":   reward_map[record["player"]],
        })

    return training_samples
```

### 7.3 Génération d'un lot de parties

```python
def generate_training_data(model, device, num_games: int = 100) -> list:
    all_samples = []
    for i in range(num_games):
        samples = play_one_game(model, device)
        all_samples.extend(samples)
        if (i + 1) % 10 == 0:
            print(f"  Parties générées : {i+1}/{num_games}")
    return all_samples
```

---

## 8. L'entraînement du réseau

### 8.1 Les deux fonctions de perte

Le réseau apprend deux choses simultanément :

**Perte de valeur** : MSE entre la valeur prédite et la récompense réelle
```
L_value = (v_prédit - reward)²
```

**Perte de politique** : cross-entropy entre la distribution prédite et le coup réellement joué
```
L_policy = -log(prob[coup_joué])
```

La perte totale :
```
L = L_value + L_policy
```

### 8.2 La boucle d'entraînement

```python
from torch.utils.data import DataLoader, Dataset

class ChessDataset(Dataset):
    def __init__(self, samples: list):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return s["state"], s["move_idx"], torch.tensor(s["reward"], dtype=torch.float32)


def train_one_epoch(model, optimizer, dataset, device, batch_size=256):
    model.train()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    total_loss = 0.0

    for states, move_idxs, rewards in loader:
        states   = states.to(device)
        rewards  = rewards.to(device).unsqueeze(1)
        move_idxs = move_idxs.to(device)

        policy_logits, values = model(states)

        # Perte de valeur
        loss_value = F.mse_loss(values, rewards)

        # Perte de politique (cross-entropy sur le coup joué)
        loss_policy = F.cross_entropy(policy_logits, move_idxs)

        loss = loss_value + loss_policy

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(states)

    return total_loss / len(dataset)
```

### 8.3 La grande boucle d'entraînement

```python
def train_deep_pipsou(
    num_iterations: int = 50,
    games_per_iter: int = 100,
    epochs_per_iter: int = 5,
    lr: float = 1e-3,
    save_path: str = "deep_pipsou_model.pt"
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DeepPipsouNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for iteration in range(1, num_iterations + 1):
        print(f"\n=== Itération {iteration}/{num_iterations} ===")

        # Phase 1 : générer des parties
        print("  Génération des parties...")
        samples = generate_training_data(model, device, num_games=games_per_iter)
        print(f"  {len(samples)} positions collectées.")

        # Phase 2 : entraîner le réseau
        dataset = ChessDataset(samples)
        for epoch in range(1, epochs_per_iter + 1):
            loss = train_one_epoch(model, optimizer, dataset, device)
            print(f"  Epoch {epoch}/{epochs_per_iter} — Loss : {loss:.4f}")

        # Sauvegarder le modèle à chaque itération
        torch.save(model.state_dict(), save_path)
        print(f"  Modèle sauvegardé : {save_path}")
```

---

## 9. MCTS — Monte Carlo Tree Search

Le MCTS est la technique qui permet à Deep Pipsou de "réfléchir" plusieurs coups à l'avance. Sans lui, le réseau joue en aveugle (un coup à la fois). Avec MCTS, il explore un arbre de positions avant de choisir.

### 9.1 L'idée

Pour chaque coup à choisir, on effectue **N simulations** :

```
┌──────────────────────────────────────────────────────┐
│  Pour chaque simulation :                            │
│                                                      │
│  1. SELECTION    : descendre dans l'arbre en          │
│     choisissant le nœud avec le meilleur score UCB   │
│                                                      │
│  2. EXPANSION    : si le nœud n'a pas encore été     │
│     exploré, l'évaluer avec le réseau de neurones    │
│                                                      │
│  3. BACKUP       : remonter la valeur obtenue         │
│     dans tous les nœuds traversés                    │
└──────────────────────────────────────────────────────┘

Après N simulations : choisir le coup le plus visité.
```

### 9.2 La formule UCB (Upper Confidence Bound)

Pour chaque nœud enfant `a`, on calcule :

```
UCB(a) = Q(a) + c_puct × P(a) × √(N_parent) / (1 + N(a))
```

- `Q(a)` : valeur moyenne estimée pour ce coup
- `P(a)` : probabilité initiale donnée par la *policy head* du réseau
- `N(a)` : nombre de fois où ce coup a été exploré
- `c_puct` : constante d'exploration (typiquement 1.0 à 4.0)

### 9.3 Implémentation du nœud MCTS

```python
class MCTSNode:
    def __init__(self, game_state, parent=None, move=None, prior=0.0):
        self.game_state = game_state  # copie du board numpy
        self.parent     = parent
        self.move       = move        # coup qui a mené à ce nœud
        self.prior      = prior       # P(a) donné par la policy
        
        self.children   = {}          # move → MCTSNode
        self.visit_count = 0          # N(a)
        self.value_sum   = 0.0        # somme des valeurs pour calculer Q

    @property
    def q_value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count

    def ucb_score(self, c_puct=1.5):
        if self.parent is None:
            return float('inf')
        return self.q_value + c_puct * self.prior * (
            self.parent.visit_count ** 0.5 / (1 + self.visit_count)
        )

    def is_leaf(self):
        return len(self.children) == 0
```

### 9.4 Fonction de recherche MCTS

```python
def mcts_search(root_game, root_board, model, device, num_simulations=100):
    """
    Effectue num_simulations simulations MCTS depuis la position courante.
    Retourne la distribution de probabilités sur les coups.
    """
    root = MCTSNode(game_state=root_board)

    for _ in range(num_simulations):
        node = root
        game_copy = board()  # copie de l'état du jeu
        game_copy.last_move = list(root_game.last_move)
        game_copy.turn = root_game.turn
        current_board = np.copy(root_board)

        # 1. SELECTION : descendre jusqu'à une feuille
        while not node.is_leaf():
            best_child = max(node.children.values(), key=lambda n: n.ucb_score())
            game_copy.move_piece(current_board, best_child.move)
            current_board = np.copy(current_board)  # mise à jour
            node = best_child

        # 2. EXPANSION + EVALUATION
        game_over, _, winner = game_copy.check_game_end(current_board)
        if game_over:
            value = 1.0 if winner == game_copy.turn else (-1.0 if winner != "draw" else 0.0)
        else:
            state_tensor = encode_board(current_board).unsqueeze(0).to(device)
            with torch.no_grad():
                policy_logits, value_tensor = model(state_tensor)
            value = value_tensor.item()

            legal_moves = get_legal_moves(game_copy, current_board)
            probs = torch.softmax(policy_logits.squeeze(0), dim=0).cpu().numpy()
            for move in legal_moves:
                idx = move_to_index(move)
                node.children[idx] = MCTSNode(
                    game_state=current_board,
                    parent=node,
                    move=move,
                    prior=float(probs[idx]),
                )

        # 3. BACKUP : remonter la valeur
        while node is not None:
            node.visit_count += 1
            node.value_sum   += value
            value = -value  # alternance des joueurs
            node = node.parent

    # Construire la distribution finale (proportionnelle aux visites)
    move_counts = {idx: child.visit_count for idx, child in root.children.items()}
    total = sum(move_counts.values())
    move_probs = {idx: count / total for idx, count in move_counts.items()}
    return move_probs
```

### 9.5 Intégrer MCTS dans le self-play

Remplacer la sélection directe par policy dans `play_one_game` par :

```python
move_probs = mcts_search(game, current_board, model, device, num_simulations=100)
chosen_idx = max(move_probs, key=move_probs.get)
```

> **Conseil** : commencer **sans MCTS** (pure policy), vérifier que le système apprend quelque chose, puis ajouter MCTS pour améliorer la qualité du jeu.

---

## 10. Export et import du modèle

### 10.1 Sauvegarder

```python
def save_model(model: DeepPipsouNet, path: str):
    torch.save({
        "model_state_dict": model.state_dict(),
        "architecture": {
            "num_channels": 64,
            "num_res_blocks": 4,
        }
    }, path)
    print(f"Modèle sauvegardé : {path}")
```

### 10.2 Charger

```python
def load_model(path: str, device) -> DeepPipsouNet:
    checkpoint = torch.load(path, map_location=device)
    arch = checkpoint["architecture"]
    model = DeepPipsouNet(
        num_channels=arch["num_channels"],
        num_res_blocks=arch["num_res_blocks"]
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print(f"Modèle chargé : {path}")
    return model
```

Le fichier `.pt` est le "cerveau" exportable. Il suffit de le partager pour transporter l'agent.

---

## 11. Interface de jeu externe

L'objectif final : donner à Deep Pipsou une couleur et une séquence de coups, et lui demander de répondre.

### 11.1 Reconstituer un plateau depuis une séquence de coups

```python
def board_from_moves(move_list: list[tuple]) -> tuple:
    """
    Rejoue une séquence de coups depuis la position initiale.
    Retourne (game, current_board).
    move_list : liste de tuples ex. [('Pe2','e4'), ('pe7','e5'), ...]
    """
    game = board()
    current_board = game.create_board()
    for move in move_list:
        current_board = game.move_piece(current_board, move)
    return game, current_board
```

### 11.2 L'agent Deep Pipsou en mode "jeu"

```python
class DeepPipsouPlayer:
    def __init__(self, model_path: str, color: str, use_mcts: bool = True, num_simulations: int = 200):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = load_model(model_path, self.device)
        self.color  = color  # "white" ou "black"
        self.use_mcts = use_mcts
        self.num_simulations = num_simulations

    def respond(self, move_history: list[tuple]) -> tuple:
        """
        Prend l'historique des coups joués et retourne le prochain coup de Deep Pipsou.
        
        Exemple d'usage :
            player = DeepPipsouPlayer("deep_pipsou_model.pt", color="black")
            response = player.respond([('Pe2', 'e4'), ('pe7', 'e5')])
            # → ('Ng8', 'f6')  par exemple
        """
        game, current_board = board_from_moves(move_history)

        # Vérifier que c'est bien le tour de Deep Pipsou
        if game.turn != self.color:
            raise ValueError(f"Ce n'est pas le tour de {self.color}.")

        legal_moves = get_legal_moves(game, current_board)
        if not legal_moves:
            raise ValueError("Aucun coup légal disponible.")

        if self.use_mcts:
            move_probs = mcts_search(game, current_board, self.model, self.device, self.num_simulations)
            chosen_idx = max(move_probs, key=move_probs.get)
            for move in legal_moves:
                if move_to_index(move) == chosen_idx:
                    return move
            return random.choice(legal_moves)  # fallback
        else:
            state_tensor = encode_board(current_board).unsqueeze(0).to(self.device)
            with torch.no_grad():
                policy_logits, _ = self.model(state_tensor)
            mask = torch.full((4096,), float('-inf'))
            for move in legal_moves:
                mask[move_to_index(move)] = 0.0
            masked_logits = policy_logits.squeeze(0) + mask.to(self.device)
            chosen_idx = int(masked_logits.argmax().item())
            for move in legal_moves:
                if move_to_index(move) == chosen_idx:
                    return move
            return random.choice(legal_moves)
```

### 11.3 Exemple d'utilisation en ligne de commande

```python
if __name__ == "__main__":
    # Deep Pipsou joue les Noirs, répond après 1.e4
    player = DeepPipsouPlayer(
        model_path="deep_pipsou_model.pt",
        color="black",
        use_mcts=True,
        num_simulations=200
    )
    move_history = [("Pe2", "e4")]
    response = player.respond(move_history)
    print(f"Deep Pipsou joue : {response}")
```

---

## 12. Structure des fichiers à créer

```
deep_pipsou/
│
├── GUIDE.md                  ← ce fichier
│
├── chess_interface.py        ← Étape 3 : get_legal_moves(), board_from_moves()
├── encoding.py               ← Étape 4 : encode_board(), move_to_index()
├── model.py                  ← Étape 5 : DeepPipsouNet, ResidualBlock
├── agents.py                 ← Étape 6 : RandomAgent, DeepPipsouPlayer
├── self_play.py              ← Étape 7 : play_one_game(), generate_training_data()
├── training.py               ← Étape 8 : ChessDataset, train_one_epoch(), train_deep_pipsou()
├── mcts.py                   ← Étape 9 : MCTSNode, mcts_search()
├── persistence.py            ← Étape 10 : save_model(), load_model()
│
├── train.py                  ← Script principal pour lancer l'entraînement
└── play.py                   ← Script principal pour jouer contre Deep Pipsou
│
└── checkpoints/              ← Dossier des modèles sauvegardés (.pt)
```

> **Convention** : chaque fichier importe chess.py via `sys.path.insert(0, "../pieces_board")`.

---

## 13. Feuille de route — étapes concrètes

Voici l'ordre recommandé pour coder Deep Pipsou, du plus simple au plus complexe.

### Étape 1 — Poser l'infrastructure (chess_interface.py)
- Coder `get_legal_moves()`
- Tester : générer des coups légaux depuis la position initiale et les afficher
- Vérifier qu'il y a bien 20 coups au premier coup des Blancs

### Étape 2 — Vérifier le moteur de partie
- Coder deux `RandomAgent` qui jouent l'un contre l'autre
- Lancer 10 parties complètes et afficher les résultats (victoire blancs / noirs / nulle)
- Cette étape valide que `check_game_end()`, `move_piece()` et `get_legal_moves()` fonctionnent ensemble

### Étape 3 — Encoder le plateau
- Coder `encode_board()` et `move_to_index()`
- Test unitaire : encoder le plateau initial, vérifier que les plans 0-5 et 6-11 correspondent aux bonnes pièces

### Étape 4 — Construire le réseau
- Coder `DeepPipsouNet`
- Test : passer un tenseur aléatoire `(1, 12, 8, 8)`, vérifier que les sorties ont la bonne forme `(1, 4096)` et `(1, 1)`

### Étape 5 — Premier self-play sans MCTS
- Coder `play_one_game()` avec la policy directe (sans MCTS)
- Générer 10 parties, afficher le nombre de positions par partie

### Étape 6 — Premier entraînement
- Coder `train_one_epoch()` et lancer quelques itérations
- Surveiller la loss : elle doit diminuer
- L'agent ne joue pas encore mieux, mais le pipeline fonctionne

### Étape 7 — Évaluation du progrès
- Écrire une fonction `evaluate()` qui fait jouer Deep Pipsou contre `RandomAgent` sur N parties
- Mesurer le taux de victoire. Après quelques centaines de parties d'entraînement, Deep Pipsou doit commencer à battre l'aléatoire.

### Étape 8 — Ajouter MCTS
- Coder `MCTSNode` et `mcts_search()`
- Remplacer la sélection directe par MCTS dans `play_one_game()`
- Comparer les résultats d'évaluation avec et sans MCTS

### Étape 9 — Export / interface de jeu
- Coder `save_model()` / `load_model()` et `DeepPipsouPlayer.respond()`
- Tester : donner une séquence de coups et afficher la réponse de Deep Pipsou

### Étape 10 — Entraînement long
- Lancer `train_deep_pipsou()` avec 50+ itérations et 200+ parties par itération
- Surveiller l'évolution du taux de victoire contre l'aléatoire
- Sauvegarder régulièrement les checkpoints

---

## Annexe A — Conversions de notation utiles

| Notation chess.py | Description |
|---|---|
| `("Pe2", "e4")` | Pion blanc de e2 vers e4 |
| `("pe7", "e5")` | Pion noir de e7 vers e5 |
| `("Ke1", "g1")` | Roi blanc roque côté roi |
| `("Ng1", "f3")` | Cavalier blanc de g1 vers f3 |

Les majuscules = blancs, les minuscules = noirs. Le premier caractère du premier élément du tuple est toujours la pièce ; les 2 caractères suivants sont la case de départ. Le deuxième élément est toujours la case d'arrivée (sans préfixe de pièce).

---

## Annexe B — Paramètres d'entraînement recommandés pour démarrer

| Paramètre | Valeur initiale | Commentaire |
|---|---|---|
| `num_channels` | 64 | Largeur du réseau |
| `num_res_blocks` | 4 | Profondeur du réseau |
| `learning_rate` | 1e-3 | Adam optimizer |
| `batch_size` | 256 | |
| `games_per_iter` | 100 | Parties par itération |
| `epochs_per_iter` | 5 | Epochs d'entraînement par itération |
| `num_simulations` (MCTS) | 100 | Simulations par coup |
| `c_puct` | 1.5 | Exploration MCTS |

Augmenter `num_channels` et `num_res_blocks` pour un réseau plus fort, au prix d'un entraînement plus lent.
