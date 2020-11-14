from random import uniform, normalvariate, choice, sample
from Game.Player import Player
from Game.State import print_state
from numeric_dungeon_plays import DecisionYes, DecisionNo, Answer, Question, Activate
from numeric_dungeon_domain import DungeonMap, MasterKey, EnergyDrink


class NDPlayer(Player):
    def __init__(self):
        pass
    
    def get_play(self, state, node):
        print(f"NODE: {node}")
        print_state(state)
        if node == "move":
            if input("Wants, to activate: \n") == "yes":
                return DecisionYes()
            else:
                row = int(input("R\n"))
                col = int(input("C\n"))
                d = DecisionNo()
                d.pos = (row, col)
                return d
        
        if node == "activate_treasure":
            player_index = state.table_state.actual_player
            player = state.players_state[player_index]
            print(player)
            index = int(input("Insert treasure to activate:\n"))
            return Activate(index)
        
        if node == "pvp_battle_ask":
            question = int(input("Insert question:\n"))    
            return Question(question)

        if node in ["pvp_battle_answer", "pve_battle"]:
            return Answer(int(input("Answer question:\n")))     
                

class NDPlayerAgent(Player):
    def __init__(self, knowledge):
        self.knowledge = knowledge
        self.to_activate = []
        self.decisions_count = []
    
    def get_play(self, state, node):
        if node == "move":
            actual_index = state.table_state.actual_player
            actual_player = state.players_state[actual_index]
            treasures = actual_player.player._treasures
            possibles = list(filter(lambda t : activate_decision(state, t), treasures))
            possibles = list(map(lambda t : treasures.index(t), possibles))
            self.decisions_count.append(2 ** len(possibles))
            activate = sample(possibles, choice(range(0,len(possibles)+1)))
            self.to_activate = activate
            if not activate:
                return DecisionNo()
            return DecisionYes()
        
        if node == "activate_treasure":
            return Activate(self.to_activate)

        if node == "pvp_battle_ask":
            return Question(normalvariate(self.knowledge, self.knowledge/2))
        
        if node in ["pvp_battle_answer", "pve_battle"]:
            return Answer(normalvariate(self.knowledge, self.knowledge/2))


def activate_decision(state, treasure):
    if isinstance(treasure, (DungeonMap, MasterKey)):
        return False
    return choice([True, False])