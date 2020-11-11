from collections import namedtuple

GameState = namedtuple('State', ['table_state', 'players_state'])

class State:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def get_visible_state(self):
        raise NotImplementedError


class TableState(State):
    def get_visible_state(self):
        return self

class PlayerState(State):
    pass

def create_game_state(table : TableState, players : [PlayerState]) -> GameState:
    return GameState(table, players)
        
def get_visible_state(player : int, state : GameState) -> GameState:
    table = state.table_state.get_visible_state()
    players = [st if i == player else st.get_visible_state for i, st in enumerate(state.players_state)]
    return create_game_state(table, players)

def print_state(state):
    print(state.table_state)
    for p in state.players_state:
        print(p)