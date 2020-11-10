from itertools import filterfalse, groupby
from Game.State import TableState, PlayerState
from numeric_dungeon_domain import Unit, DungeonMaster, Cell


class NMTableState(TableState):
    def __init__(self, n, cards):
        self.board = [ Cell() for _ in range(n * n) ]
        self.dungeon_master = None
        for index, card in enumerate(cards):
            if isinstance(card, DungeonMaster):
                self.dungeon_master = card
            self.board[index].add_habitant(card)
        self.board = [ [ c[1] for c in row[1] ] for row in groupby(enumerate(self.board), lambda x : x[0] // n) ]
        self.actual_player = 0
        self.last_move_failed = False
        self.question = None
        self.attacker = None
        self.targets = []
        self.target = None

    
    def __getitem__(self, pos):
        n_row = len(self.board)
        return self.board[ pos[0] * n_row + pos[1] ]
    
    def __setitem__(self, pos, cell):
        n_col = len(self.board[0])
        self.board[ pos[0] * n_col + pos[1] ]

    def move(self, unit, dest):
        row, col = unit.position
        self[(row, col)].remove_habitant(unit)
        unit.move(dest[0], dest[1])
        self[dest[0], dest[1]].add_habitant(unit)
    

class NMPlayerState(Unit, PlayerState):
    def __init__(self, name, hp, treasures = []):
        Unit.__init__(self, -1, -1, hp, treasures)
        self.__name = name
    
    def in_cell(self):
        return self._position != (-1, -1) 
    
    def move(self, row, col):
        self._position = (row, col)
