from Game.State import TableState, State, create_game_state
from Game.FlowGraph import FlowNode
from Game.Mechanics import SystemMechanic, PlayerMechanic
from Game.Player import Player, Play
from Game.Game import Game

class TTTTableState(TableState):
    def __init__(self):
        self.board = [ -1 for _ in range(9) ]
        self.player_in_turn = 0
    
    def __repr__(self):
        char = {0 : "O", 1 : "X", -1:" "}
        s1 = f"Player in turn: {self.player_in_turn}" 
        s2 = f"{char[self.board[0]]} | {char[self.board[1]]} | {char[self.board[2]]}"
        s3 = "--|---|--"
        s4 = f"{char[self.board[3]]} | {char[self.board[4]]} | {char[self.board[5]]}"
        s5 = "--|---|--"
        s6 = f"{char[self.board[6]]} | {char[self.board[7]]} | {char[self.board[8]]}"
        board = "\n".join([s1, s2, s3, s4, s5, s6])
        return board

class PutMark(Play):
    def __init__(self, row, col, mark):
        self.row = row
        self.col = col
        self.mark = mark

class TicTacToePlayer(Player):
    def __init__(self, name, mark):
        self.name = name
        self.mark = mark

    def play(self, state: State, mechanic: PlayerMechanic):
        print(state.table_state.board)
        row = int(input("Insert Row to play\n"))
        col = int(input("Insert Column to play\n"))
        return PutMark(row, col, self.mark)


class WhereToPlay(PlayerMechanic):
    @staticmethod
    def is_valid(state: State, play: PutMark) -> bool:
        table_state = state.table_state
        if play.mark != table_state.player_in_turn:
            return False
        if play.row < 0 or play.row > 2:
            return False
        if play.col < 0 or play.col > 2:
            return False
        if table_state.board[play.row * 3 + play.col] != -1:
            return False
        return True
    
    @staticmethod
    def reduce(state: State, play: PutMark) -> State:
        table_state = state.table_state
        table_state.board[play.row * 3 + play.col] = play.mark
        return create_game_state(table_state, [])

    @staticmethod
    def who_plays(state):
        return state.table_state.player_in_turn

class ChangeTurn(SystemMechanic):
    @staticmethod
    def reduce(state: State):
        table_state = state.table_state
        table_state.player_in_turn = (table_state.player_in_turn + 1) % 2
        return create_game_state(table_state, [])


def ttt_end_condition(state):
    board = state.table_state.board
    end_result = [-1, -1]
    for row in range(3):
        if board[3 * row + 0]  == board[3 * row + 1] == board[3 * row + 2]:
            if board[3 * row + 0] != -1:
                end_result[board[3 * row + 0]] = 1
                return end_result
    for col in range(3):
        if board[col] == board [3 + col] == board[6 + col]:
            if board[col] != -1:
                end_result[board[col]] = 1
                return end_result
    if board.count(-1) == 0:
        return [0, 0]
    return None

    
if __name__ == '__main__':
    play = FlowNode("Play")
    change = FlowNode("ChangeTurn")
    play.set_mechanic(WhereToPlay)
    change.set_mechanic(ChangeTurn)
    play.add_transition(change, lambda x, y : True)
    change.add_transition(play, lambda x, y : True)
    player1 = TicTacToePlayer("1", 0)
    player2 = TicTacToePlayer("2", 1)
    
    game = Game(play, create_game_state(TTTTableState(), []), [player1, player2], ttt_end_condition)
    for s in game:
        print(s)