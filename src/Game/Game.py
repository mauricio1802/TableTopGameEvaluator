from .State import State, create_game_state
from copy import deepcopy

class Game:
    def __init__(self, flow_graph, state, players):
        self.state_history = [ state ]
        self.flow_graph = flow_graph
        self.players = players
    
    def __iter__(self):
        return self
    
    def __next__(self):
        new_state, player_decision = self.flow_graph.reduce(deepcopy(self.current_state), self.players)
        self.state_history.append(new_state)
        self.flow_graph = self.flow_graph.go(self.current_state, player_decision)
        return new_state
        
    @property
    def current_state(self) -> State:
        return self.state_history[-1]
    
    
    

