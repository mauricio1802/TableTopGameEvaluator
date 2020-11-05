from Game.State import TableState, State, create_game_state
from Game.FlowGraph import FlowNode
from Game.Mechanics import SystemMechanic, PlayerMechanic
from Game.Player import Player, Play
from Game.Game import Game

class TTTTableState(TableState):
    def __init__(self):
        self.board = [ -1 for _ in range(9) ]
        self.player_in_turn = 0
    
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






    
if __name__ == '__main__':
    play = FlowNode("Play")
    change = FlowNode("ChangeTurn")
    play.set_mechanic(WhereToPlay)
    change.set_mechanic(ChangeTurn)
    play.add_transition(change, lambda x, y : True)
    change.add_transition(play, lambda x, y : True)
    player1 = TicTacToePlayer("1", 0)
    player2 = TicTacToePlayer("2", 1)
    
    game = Game(play, create_game_state(TTTTableState(), []), [player1, player2])
    for s in game:
        print(s)