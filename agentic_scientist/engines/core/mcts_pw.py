from __future__ import annotations
import math
import random
from typing import Callable, Any, Dict, List, Tuple, Optional

class PWNode:
    __slots__ = ('state', 'parent', 'action', 'children', 'N', 'Q', 'untried')
    def __init__(self, state: Any, parent: Optional['PWNode'] = None, action: Any = None):
        self.state = state # Doit implémenter .is_terminal(), .get_legal_actions(), .apply(action)
        self.parent = parent
        self.action = action 
        self.children: Dict[Any, 'PWNode'] = {}
        self.N = 0 # Visites
        self.Q = 0.0 # Récompense cumulée
        self.untried = None # Initialisation paresseuse pour PW

    def is_fully_expanded(self, k: float, alpha: float) -> bool:
        if self.N == 0: return False
        return len(self.children) >= k * (self.N ** alpha)

    def ucb1(self, c: float = 1.414) -> float:
        if self.N == 0: return float('inf')
        return (self.Q / self.N) + c * math.sqrt(math.log(self.parent.N) / self.N)

def mcts_search(
    root_state: Any,
    budget: int = 1000,
    k: float = 2.0,
    alpha: float = 0.5,
    c: float = 1.414,
    rollout_policy: Callable[[Any], Any] = None
) -> Any:
    """
    PW-MCTS générique. root_state doit implémenter:
    - is_terminal() -> bool
    - get_legal_actions() -> List[Any]
    - apply(action) -> new_state
    - value() -> float (reward à maximiser)
    """
    root = PWNode(root_state)

    for _ in range(budget):
        node = root
        state = root_state

        # 1. SELECTION + PROGRESSIVE WIDENING
        while not state.is_terminal():
            if node.untried is None:
                node.untried = state.get_legal_actions()
                random.shuffle(node.untried)

            # PW: élargir seulement si N^alpha le permet
            if node.untried and not node.is_fully_expanded(k, alpha):
                action = node.untried.pop()
                next_state = state.apply(action)
                child = PWNode(next_state, parent=node, action=action)
                node.children[action] = child
                node = child
                state = next_state
                break
            else:
                if not node.children:
                    break
                # UCT si déjà élargi ou pas d'actions restantes
                node = max(node.children.values(), key=lambda n: n.ucb1(c))
                state = node.state

        # 2. ROLLOUT (Simulation)
        temp_state = state
        while not temp_state.is_terminal():
            if rollout_policy:
                temp_state = rollout_policy(temp_state)
            else:
                actions = temp_state.get_legal_actions()
                if not actions: break
                temp_state = temp_state.apply(random.choice(actions))

        # 3. BACKUP (Rétropropagation)
        reward = temp_state.value()
        while node:
            node.N += 1
            node.Q += reward
            node = node.parent

    if not root.children:
        return None
        
    return max(root.children.items(), key=lambda item: item[1].N)[0]
