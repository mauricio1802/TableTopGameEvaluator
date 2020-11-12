from random import randint

MONSTERS_HP = 1
DUNGEON_MASTER_HP = 3


class Cell:
    def __init__(self):
        self.__habitants = []
    
    def __repr__(self):
        cell = [' ', ' ', ' ', ' ']
        for i, hab in enumerate(self.__habitants):
            cell[i] = str(hab) if isinstance(hab, (Monster, DungeonMaster)) else "P"
        return "".join(cell)
    
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
    
    def have_player(self):
        for hab in self.__habitants:
            if not isinstance(hab, (Monster, DungeonMaster)):
                return True
        return False

    def have_monster(self):
        for hab in self.__habitants:
            if isinstance(hab, Monster):
                return True
        return False
    
    def __contains__(self, value):
        return value in self.__habitants
    
    @property
    def habitants(self):
        return self.__habitants

class Unit:
    def __init__(self, row, col, hp = MONSTERS_HP, treasures = None):
        self._position = (row, col)
        self._hp = hp
        self._treasures = treasures if treasures else []
    
    def add_treasure(self, treasure):
        self._treasures.append(treasure)
    
    def get_treasures(self):
        treasures = self._treasures
        self._treasures = []
        return treasures
    
    def get_treasure(self, index = 0):
        return self._treasures[index]
    
    def use_treasure(self, treasure):
        self._treasures.remove(treasure)
    
    def have_treasure(self, treasure):
        return treasure in self._treasures
    
    def have_treasures(self):
        return len(self._treasures) != 0

    def damage(self, ap = 1):
        self._hp -= ap
    
    def is_alive(self):
        return self.hp > 0
    
    def move(self, row, col):
        self._position = (row, col)

    @property
    def hp(self):
        return self._hp
    
    @property
    def position(self):
        return self._position
    
class Player(Unit):
    def __init__(self, name, hp, treasures = []):
        Unit.__init__(self, -1, -1, hp, treasures)
        self.__name = name
    
    def __repr__(self):
        return "P"

    def in_cell(self):
        return self._position != (-1, -1) 
    
    def have_win_requirements(self):
        found = False
        for t in self._treasures:
            if isinstance(t, (DungeonMap, MasterKey)):
                if found:
                    return found
                else:
                    found = True
            
    
    @property
    def name(self):
        return self.__name
    
class Monster(Unit):
    def __init__(self, row, col, dif):
        super().__init__(row, col)
        self.__attack_remaining = 0
        self.dif = dif
    
    def __repr__(self):
        return "M"
    
    def get_question(self):
        return self.dif

    def begin_attack(self):
        self.__attack_remaining = 1
    
    def attack(self):
        self.__attack_remaining -= 1
    
    @property
    def in_attack(self):
        self.__attack_remaining > 0

class DungeonMaster(Monster):
    def __init__(self, row, col, dif):
        super().__init__(row, col, dif)
        self._hp = DUNGEON_MASTER_HP
        self.add_treasure(MasterKey())
        self.__founded = False
        self.__attack_remaining = 0
        
    def __repr__(self):
        return "D"
    
    def flip(self):
        self.__founded = True

    def begin_attack(self):
        self.__attack_remaining = self._hp
    
    @property
    def founded(self):
        return self.__founded
    
    
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

class EnergyDrink(Treasure):
    def __init__(self):
        pass
    
    def reduce(self, state):
        actual_player_index = state.table_state.actual_player
        actual_player = state.players_state[actual_player_index]
        actual_player.damage(-2)
        return state

        
