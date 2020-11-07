from .State import State, create_game_state
from copy import deepcopy

class Game2:
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
    

class Game:
    def __init__(self, state, game_node):
        self.state = state
        self.game_node = game_node
    
    def play(self, action):
        new_state, new_node = self.game_node.go(self.state, action)
        return (new_state, new_node)

class GameSimulation:
    def __init__(self, game, players, end_condition, who_plays):
        self.players = players
        self.end_condition = end_condition
        self.who_plays = who_plays
        self.history = [ game ]
        self.end_results = [0 for _ in range(len(players))]
    
    @property
    def game(self):
        return self.history[-1]

    def __iter__(self):
        return self
    
    def __next__(self):
        end_results = self.end_condition(self.game.state)
        if end_results is not None:
            self.end_results = end_results
            raise StopIteration

        player = self.players[ self.who_plays(self.game.state) ]
        action = player.get_action(self.game.state)

        new_state, new_node = self.game.play(action)
        self.history.append(Game(new_state, new_node))
        
        return new_state

