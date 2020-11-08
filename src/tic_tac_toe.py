from Game.State import TableState, State, create_game_state
from Game.Action import Action 
from Game.GameNode import GameNode
from Game.Game import Game, GameSimulation
from Game.Player import Player

class TTTTableState(TableState):
    def __init__(self):
        self.board = [ -1 for _ in range(9) ]
        self.player_in_turn = 0
    

    def __repr__(self):
        char = {0:'O', 1:'X', -1:' '}
        s1 = f"{char[self.board[0]]} | {char[self.board[1]]} | {char[self.board[2]]}"
        s2 = "--|---|--"
        s3 = f"{char[self.board[3]]} | {char[self.board[4]]} | {char[self.board[5]]}"
        s4 = "--|---|--"
        s5 = f"{char[self.board[6]]} | {char[self.board[7]]} | {char[self.board[8]]}"
        return "\n".join(["\n",s1, s2, s3, s4, s5, "\n"])


class PlayO(Action):
    def __init__(self, row, col):
        self.row = row
        self.col = col
    
    def reduce(self, state):
        table_state = state.table_state
        table_state.board[self.row * 3 + self.col] = 0
        return create_game_state(table_state, [])
    
    def is_valid(self, state):
        table_state = state.table_state
        if table_state.player_in_turn != 0:
            return False
        if self.row < 0 or self.row > 2 or self.col < 0 or self.col > 2:
            return False
        if table_state.board[self.row * 3 + self.col] != -1:
            return False
        return True

class PlayX(Action):
    def __init__(self, row, col):
        self.row = row
        self.col = col
    
    def reduce(self, state):
        table_state = state.table_state
        table_state.board[self.row * 3 + self.col] = 1
        return create_game_state(table_state, [])
    
    def is_valid(self, state):
        table_state = state.table_state
        if table_state.player_in_turn != 1:
            return False
        if self.row < 0 or self.row > 2 or self.col < 0 or self.col > 2:
            return False
        if table_state.board[self.row * 3 + self.col] != -1:
            return False
        return True

class ChangeTurn(Action):
    def __init__(self):
        pass
    
    def is_valid(self, state):
        return True
    
    def reduce(self, state):
        state.table_state.player_in_turn = (state.table_state.player_in_turn + 1) % 2
        return state

class TTTHumanPlayer(Player):
    def __init__(self, name, player):
        self.name = name
        self.player = player
    
    def get_action(self, state):
        row = int(input("Insert row to play:\n"))
        col = int(input("Insert col to play:\n"))
        if self.player == 0:
            return PlayO(row, col)
        if self.player == 1:
            return PlayX(row, col)
        
    


def ttt_who_plays(state):
    return state.table_state.player_in_turn

def ttt_end_condition(state):
    board = state.table_state.board
    result = [-1, -1]
    for row in range(3):
        if (board[row * 3] == board[row * 3 + 1] == board[row * 3 + 2]) and board[row * 3] != -1:
            result[board[row * 3]] = 1
            return result
    for col in range(3):
        if (board[col] == board[col + 3] == board[col + 6]) and board[col] != -1:
            result[board[col]] = 1
            return result
    if (board[0] == board[4] == board[8]) and board[0] != -1:
        result[board[0]] = 1
        return result
    if (board[2] == board[4] == board[6]) and board[2] != -1:
        result[board[2]] = 1
        return result
    if board.count(-1) == 0:
        return [0, 0]
    return None


if __name__ == '__main__':
    playO = GameNode('playO', [ChangeTurn()])
    playX = GameNode('playX', [ChangeTurn()])
    playO.add_transition(playX, lambda x, y : True)
    playX.add_transition(playO, lambda x, y : True)
    ttt_game = Game(create_game_state(TTTTableState(), []), playO )
    game_sim = GameSimulation(ttt_game, [TTTHumanPlayer("O", 0), TTTHumanPlayer("X", 1)], ttt_end_condition, ttt_who_plays)
    for s in game_sim:
        pass
    game_states = [g.state for g in game_sim.history]
    for s in game_states:
        print(s)
