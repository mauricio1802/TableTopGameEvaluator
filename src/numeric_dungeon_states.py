from itertools import filterfalse, groupby
from Game.State import TableState, PlayerState
from numeric_dungeon_domain import Unit, DungeonMaster, Cell, Player


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
       # n_col = len(self.board[0])
       # print(self.board)
       # return self.board[ pos[0] * n_col + pos[1] ]
       return self.board[pos[0]][pos[1]]
    
    def __setitem__(self, pos, cell):
       # n_col = len(self.board[0])
       # self.board[ pos[0] * n_col + pos[1] ]
       self.board[pos[0]][pos[1]] = cell
    
    def __repr__(self):
        rows = []
        for row in self.board:
            rows.append("  ".join([str(c) for c in row]))
        return "\n".join(rows)


    def move(self, unit, dest):
        row, col = unit.position
        if row != -1 and col != -1:
            self[(row, col)].remove_habitant(unit)
        unit.move(dest[0], dest[1])
        self[dest[0], dest[1]].add_habitant(unit)
    

class NMPlayerState(PlayerState):
    def __init__(self, name, hp, treasures = None):
        treasures = treasures if treasures else []
        self.player = Player(name, hp, treasures)

    
    def add_treasure(self, treasure):
        self.player.add_treasure(treasure)
    
    def get_treasures(self):
        return self.player.get_treasures()
    
    def get_treasure(self, index = 0):
        return self.player.get_treasure(index)
    
    def use_treasure(self, treasure):
        return self.player.use_treasure(treasure)

    def have_treasure(self, treasure):
        return self.player.have_treasure(treasure)

    def have_treasures(self):
        return self.player.have_treasures()

    def damage(self, ap = 1):
        self.player.damage(ap)

    def is_alive(self):
        return self.player.is_alive()

    def move(self, row, col):
        self.player.move(row, col)

    def in_cell(self):
        return self.player.in_cell()
    
    def have_win_requirements(self):
        return self.player.have_win_requirements()
    
    def __repr__(self):
        return f"NAME: {self.name} in {self.position} with {self.hp}\n{self.player._treasures}"
    @property
    def hp(self):
        return self.player.hp

    @property
    def position(self):
        return self.player.position
    
    @property
    def name(self):
        return self.player.name