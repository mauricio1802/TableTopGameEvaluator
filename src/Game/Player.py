from .State import State
from .Action import Action

class Player:
    def __init__(self, name = ""):
        raise NotImplementedError
    
    def get_action(self, state):
        raise NotImplementedError