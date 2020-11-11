from .State import State, create_game_state
from copy import deepcopy

DEFAULT_NODE_NAME = "NoPossiblePath"

class NoPossiblePathError(Exception):
    pass

class GameNode():
    def __init__(self, name, prev = [], after = [], default = DEFAULT_NODE_NAME):
        self.name = name
        self.prev = prev
        self.after = after
        self.default = default
        self.actions = []
    
    def add_action(self, action):
        self.actions.append(action)

NoPossiblePathNode = GameNode(DEFAULT_NODE_NAME)

def no_possible_path():
    raise NoPossiblePathError 

NoPossiblePathNode.add_action((no_possible_path, False))


class Game:
    def __init__(self, start, nodes, go_table, state, players, who_plays, end_condition):
        self.actual = start
        self.nodes = nodes
        self.go_table = go_table
        self.state_history = [ state ]
        self.players = players
        self.who_plays = who_plays
        self.end_condition = end_condition
        self.last_play = None
        self.end_result = None
    

    def __iter__(self):
        return self
    
    def __next__(self):
        actual = self.nodes[self.actual]
        print(f"NOW ON {self.actual}")
        #Execute previous actions
        for node in actual.prev:
            for require_play, act in self.nodes[node].actions:
                if require_play:
                    player = self.players[self.who_plays(deepcopy(self.actual_state))]
                    self.last_play = player.get_play(deepcopy(self.actual_state))
                    self.state_history.append(act(deepcopy(self.actual_state), self.last_play))
                else:
                    self.state_history.append(act(deepcopy(self.actual_state)))
        
        #Execute node actions
        for require_play, act in actual.actions:
            if require_play:
                player = self.players[self.who_plays(deepcopy(self.actual_state))]
                self.last_play = player.get_play(deepcopy(self.actual_state), self.actual)
                self.state_history.append(act(deepcopy(self.actual_state), self.last_play))
            else:
                self.state_history.append(act(deepcopy(self.actual_state)))

        #Execute after action
        for node in actual.after:
            for require_play, act in self.nodes[node].actions:
                if require_play:
                    player = self.players[self.who_plays(deepcopy(self.actual_state))]
                    self.last_play = player.get_play(deepcopy(self.actual_state))
                    self.state_history.append(act(deepcopy(self.actual_state), self.last_play))
                else:
                    self.state_history.append(act(deepcopy(self.actual_state)))
        
        #UpdateActual
        for require_play, to, cond in self.go_table[self.actual][::-1]:
            go = cond(self.actual_state, self.last_play) if require_play else cond(self.actual_state)
            if go:
                self.actual = to
                self.last_play = None
                break
        
        self.end_result = self.end_condition(deepcopy(self.actual_state))
        if self.end_result:
            raise StopIteration
        
        return self.actual_state




    @property
    def actual_state(self):
        return self.state_history[-1]

class GameDescriptor:
    def __init__(self, start_node, nodes):
        self.start = start_node
        self.nodes = { DEFAULT_NODE_NAME : NoPossiblePathNode }
        self.nodes.update({ node.name : node for node in nodes })
        self.go_table = { node.name : [(False, node.default, lambda _ : True)] for node in nodes } 
    
    def action(self, node, require_play = False):
        def f(fn):
            self.nodes[node].add_action((require_play, fn))
        return f
    
    def goto(self, node_from, node_to, require_play = False):
        def f(fn):
            self.go_table[node_from].append((require_play, node_to, fn))
        return f
    
    def get_game_instance(self, state, players, who_plays, end_condition):
        return Game(self.start, self.nodes, self.go_table, state, players, who_plays, end_condition) 