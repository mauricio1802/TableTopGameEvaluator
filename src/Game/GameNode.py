from .State import State
from .Action import Action

class InvalidActionError(Exception):
    pass

class NotPossibleAdvanceError(Exception):
    pass

class GameNode:
    def __init__(self, name = "", prev_system_actions = [], aft_system_actions = []):
        self.name = name
        self.prev_system_actions = prev_system_actions
        self.aft_system_actions = aft_system_actions
        self.transitions = []
    
    def add_transition(self, game_node, condition):
        self.transitions.append((game_node, condition))
    
    def go(self, state, action):
        if not action.is_valid(state):
            raise InvalidActionError(f"{action} is an illegal action for {state}")
        new_state = action.reduce(state)
        for act in self.aft_system_actions:
            new_state = act.reduce(new_state)

        for node, cond in self.transitions:
            if cond(new_state, action):
                for act in self.prev_system_actions:
                    new_state = act.reduce(new_state)
                return (new_state, node)
        raise NotPossibleAdvanceError("There is not possible advance") 
