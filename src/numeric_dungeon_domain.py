from numeric_dungeon_states import NMPlayerState

MONSTERS_HP = 1
DUNGEON_MASTER_HP = 3

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
    
    def have_player(self):
        for hab in self.__habitants:
            if isinstance(hab, NMPlayerState):
                return True
        return False

    def have_monster(self):
        for hab in self.__habitants:
            if isinstance(hab, Monster):
                return True
        return False
    
    @property
    def habitants(self):
        return self.__habitants

class Unit:
    def __init__(self, row, col, hp = MONSTERS_HP, treasures = []):
        self._position = (row, col)
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

    def damage(self, ap = 1):
        self._hp -= ap
    
    def is_alive(self):
        return self.hp > 0

    @property
    def hp(self):
        return self._hp
    
    @property
    def position(self):
        return self._position
    
    
class Monster(Unit):
    def __init__(self, row, col):
        super().__init__(row, col)
        self.__attack_remaining = 0
    
    def begin_attack(self):
        self.__attack_remaining = 1
    
    def attack(self):
        self.__attack_remaining -= 1
    
    @property
    def in_attack(self):
        self.__attack_remaining > 0

class DungeonMaster(Monster):
    def __init__(self, row, col):
        super().__init__(row, col)
        self._hp = DUNGEON_MASTER_HP
        self.add_treasure(MasterKey())
        self.__founded = False
        self.__attack_remaining = 0
        

    def flip(self):
        self.__founded = True

    def move(self, row, col):
        self._position = (row, col)
    
    def begin_attack(self):
        self.__attack_remaining = self._hp
    
    def attack(self):
        self.__attack_remaining -= 1

    @property
    def founded(self):
        return self.__founded
    
    @property
    def in_attack(self):
        return self.__attack_remaining > 0
    
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
