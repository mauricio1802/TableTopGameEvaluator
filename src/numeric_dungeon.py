from itertools import groupby, filterfalse
from random import randint
from Game.State import TableState, PlayerState
from Game.Action import Action
from Game.GameNode import GameNode
from Game.Game import Game, GameSimulation
from Game.Player import Player

MONSTERS_HP = 1
DUNGEON_MASTER_HP = 3
MAX_FAIL_MOVE = 3


class Cell:
    def __init__(self):
        self.__habitants = []
    
    def add_habitant(self, habitant):
        self.__habitants.append(habitant)
    
    def remove_habitant(self, habitant):
        self.__habitants.remove(habitant)
    
    def clean(self):
        for hab in self.__habitants:
            if hab.hp is 0:
                self.remove_habitant(hab)    
    
    def habitants_number(self):
        return len(self.__habitants)

    def is_empty(self):
        return len(self.__habitants) == 0

class Unit:
    def __init__(self, hp = MONSTERS_HP, treasures = []):
        self._hp = hp
        self._treasures = treasures
    
    def add_treasure(self, treasure):
        self._treasures.append(treasure)
    
    def get_trasures(self):
        treasures = self._treasures
        self._treasures = []
        return treasures
    
    def have_treasure(self, treasure):
        return treasure in self._treasures
    
    def have_treasures(self):
        return len(self._treasures) != 0

    def damage(self):
        self._hp -= 1

    @property
    def hp(self):
        return self._hp
    
    
class Monster(Unit):
    def __init__(self):
        super().__init__()

class DungeonMaster(Monster):
    def __init__(self, row, col):
        super().__init__()
        self._hp = DUNGEON_MASTER_HP
        self.add_treasure(MasterKey())
        self.__founded = False
        self.__position = (row, col) 

    def flip(self):
        self.__founded = True

    def move(self, row, col):
        self.__position = (row, col)

    @property
    def founded(self):
        return self.__founded
    
    @property
    def position(self):
        return self.__position

class Treasure:
    def __init__(self):
        raise NotImplementedError
    
    def reduce(self, state):
        raise NotImplementedError

class MasterKey(Treasure):
    def __init__(self):
        pass

class DungeonMap(Treasure):
    def __init__(self):
        pass



class NMTableState(TableState):
    def __init__(self, n, cards):
        self.board = [ [ c[1] for c in row[1] ] for row in groupby(enumerate(cards), lambda x : x[0] // n) ]
        self.actual_player = 0
        self.last_move_failed = False

class NMPlayerState(Unit, PlayerState):
    def __init__(self, name, hp, treasures = []):
        Unit.__init__(self, hp, treasures)
        self.__name = name
        self.__position = None
    
    def in_cell(self):
        return self.__position is not None
    
    def move(self, row, col):
        self.__position = (row, col)

    @property
    def position(self):
        return self.__position
    

class ShrinkBoard(Action):
    def __init__(self):
        pass
    
    def reduce(self, state):
        board = state.table_state.board
        n_col = len(board[0])
        #Remove empty rows
        state.table_state.board = filterfalse(lambda r : all(map(lambda c: c.is_empty(), r)) , board)

        #Remove empty columns
        n_row = len(board)
        for c in range(n_col)[-1]:
            remove_col = True
            for r in range(n_row):
                if not board[r][c].is_empty():
                    remove_col = False
                    break
            if remove_col:
                for r in range(n_row):
                    board[r].pop(c)
        
        return state


class CleanActualCell(Action):
    def __init__(self):
        pass
    
    def reduce(self, state):
        board = state.table_state.board
        n_col = len(board[0])
        actual_player_index = state.table_state.actual_player
        actual_player = state.players_state[actual_player_index]
        actual_row, actual_col = actual_player.position
        cell = board[actual_row * n_col + actual_col]
        
        cell.clean()

        return state
    
class ChangeTurn(Action):
    def __init__(self):
        pass
    
    def reduce(self, state):
        n_players = len(state.players_state)
        actual_player = (state.table_state.actual_player + 1) % n_players
        players = state.players_state
        
        while players[actual_player].hp is 0:
            actual_player = (actual_player + 1) % n_players
        
        state.table_state.actual_player = actual_player

        return state

class MovePlayer(Action):
    def __init__(self):
        pass
    
    def reduce(self, state):
        board = state.table_state.board
        actual_player_index = state.table_state.actual_player
        actual_player = state.players_state[actual_player_index]
        actual_row, actual_col = actual_player.position

        n_row = len(board) 
        n_col = len(board[0])

        board[actual_row * n_col + actual_col].remove_habitant(actual_player)
        row = randint(0, 5) % n_row
        col = randint(0, 5) % n_col
        fail_moves = 1

        while board[row * n_row + col].is_empty() and fail_moves < MAX_FAIL_MOVE:
            row = randint(0, 5) % n_row
            col = randint(0, 5) % n_col
            fail_moves += 1

        actual_player.move(row, col)
        board[row * n_row + col].add_habitant(actual_player)

        return state


class DamageUnit(Action):
    def __init__(self, unit, target):
        self.target = target
        self.unit = unit

    def reduce(self, state):
        self.target.damage()
        if self.target.hp == 0:
            for treasure in self.target.get_trasures():
                self.unit.add_treasure(treasure)



class UseTreasure(Action):
    def __init__(self, treasure):
        self.treasure = treasure
    
    def reduce(self, state):
        return self.treasure.reduce(state)

    def is_valid(self, state):
        actual_player_index = state.table_state.actual_player
        actual_player = state.players_state[actual_player_index]
        return actual_player.have_treasure(self.treasure)

def battles(state, action):
    board = state.table_state.board
    n_col = len(board[0])
    actual_player_index = state.table_state.actual_player
    actual_player = state.players_state[actual_player_index]
    actual_row, actual_col = actual_player.position
    cell = board[actual_row * n_col + actual_col]

    if cell.habitants_number() > 1:
        return True
    return False

def have_treasures(state, action):
    actual_player_index = state.table_state.actual_player
    actual_player = state.players_state[actual_player_index]
    
    return actual_player.have_treasures()

def activate_treasure():
    pass

        
if __name__ == '__main__':
    preparePhase = GameNode("Prepare", aft_system_actions = [MovePlayer(), ShrinkBoard()])
    battlePhase = GameNode("Battle", aft_system_actions = [CleanActualCell()])
    wantsActivate = GameNode("WantsActivate")
    activateTreasure = GameNode("ActivateTreasure")
    endTurn = GameNode("EndTurn", aft_system_actions[ChangeTurn()])

    preparePhase.add_transition