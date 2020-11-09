from .State import State

class Action:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError
    
    def reduce(self, state):
        raise NotImplementedError
    
    def is_valid(self, state):
        return True