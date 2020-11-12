from random import randint
from Game.Player import Player
from Game.State import print_state
from numeric_dungeon_plays import DecisionYes, DecisionNo, Answer, Question, Activate


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
                

class NDPlayerAgent1(Player):
    def __init__(self):
        pass
    
    def get_play(self, state, node):
        if node == "move":
            return DecisionNo()
    
        if node == "pvp_battle_ask":
            return Question(randint(1, 100))
        
        if node in ["pvp_battle_answer", "pve_battle"]:
            return Answer(randint(1, 100))