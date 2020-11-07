from .State import State, create_game_state
from copy import deepcopy

class Game:
    def __init__(self, flow_graph, state, players, end_condition):
        self.state_history = [ state ]
        self.flow_graph = flow_graph
        self.players = players
        self.end_condition = end_condition
        self.end_result = [ 0 for _ in range(len(players))]
    
    def __iter__(self):
        return self
    
    def __next__(self):
        end_result = self.end_condition(self.current_state)
        if end_result is not None:
            self.end_result = end_result
            raise StopIteration
        new_state, player_decision = self.flow_graph.reduce(deepcopy(self.current_state), self.players)
        self.state_history.append(new_state)
        self.flow_graph = self.flow_graph.go(self.current_state, player_decision)
        return new_state
        
    @property
    def current_state(self) -> State:
        return self.state_history[-1]
    
    

