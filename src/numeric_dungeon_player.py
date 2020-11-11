from Game.Player import Player
from Game.State import print_state
from numeric_dungeon_plays import DecisionYes, DecisionNo, Answer


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
                return DecisionNo() 
        if node == "pve_battle":
            return Answer(int(input("Answer question:\n")))     
    