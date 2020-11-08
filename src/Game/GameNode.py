from .State import State
from .Action import Action

class InvalidActionError(Exception):
    pass

class NotPossibleAdvanceError(Exception):
    pass

class GameNode:
    def __init__(self, name = "", system_actions = []):
        self.name = name
        self.system_actions = system_actions
        self.transitions = []
    
    def add_transition(self, game_node, condition):
        self.transitions.append((game_node, condition))
    
    def go(self, state, action):
        if not action.is_valid(state):
            raise InvalidActionError(f"{action} is an illegal action for {state}")
        new_state = action.reduce(state)
        for act in self.system_actions:
            new_state = act.reduce(new_state)

        for node, cond in self.transitions:
            if cond(new_state, action):
                return (new_state, node)
        raise NotPossibleAdvanceError("There is not possible advance") 
