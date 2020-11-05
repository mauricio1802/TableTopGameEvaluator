from .State import State 
from .Mechanics import SystemMechanic, PlayerMechanic, InvalidMechanicError 
from .Player import Play

class NotPossibleAdvanceError(Exception): 
    pass 

class FlowNode:
    def __init__(self, name:str = ""):
        self.transitions = []
        self.mechanic = None
        self.name = name

    def add_transition(self, flow_node , condition):
        self.transitions.append((flow_node, condition))
    
    def set_mechanic(self, mechanic):
        self.mechanic = mechanic

    def reduce(self, state, players):
        if issubclass(self.mechanic, SystemMechanic):
            return (self.mechanic.reduce(state), None)
        elif issubclass(self.mechanic, PlayerMechanic):
            player = players[self.mechanic.who_plays(state)]
            valid_play = False
            while not valid_play:
                play = player.play(state, self.mechanic)
                valid_play = self.mechanic.is_valid(state, play)
            return (self.mechanic.reduce(state, play), play)
        else:
            raise InvalidMechanicError(f"The mechanic must be subclass of {SystemMechanic} or {PlayerMechanic}")

    def go(self, state: State, player_decisions):
        for node, condition in self.transitions:
            if condition(state, player_decisions):
                return node
        raise NotPossibleAdvanceError(f"Can advance from {self}")
    
    def __repr__(self):
        return self.name if self.name != "" else super().__repr__()
        