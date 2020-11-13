from itertools import chain
from random import normalvariate, choice, sample, shuffle, uniform
from numpy import mean
from Game.State import create_game_state
from Game.Metrics import calculate_metric
from numeric_dungeon_game import num_dg_game
from numeric_dungeon_domain import Monster, DungeonMaster, DungeonMap, MasterKey, EnergyDrink
from numeric_dungeon_states import NDPlayerState, NDTableState 
from numeric_dungeon_player import NDPlayerAgent


def calculate_b(sims_results):
   players_per_sim = [sim[1] for sim in sims_results]
   players = list(chain(*players_per_sim))
   decisions = [player.decisions_count for player in players]
   decisions = list(chain(*decisions))
   return mean(decisions) 


def calculate_entertaiment(sims_results):
    last_states = [sim[0][-1] for sim in sims_results]

    simulations_entertaiment = []

    for sim in sims_results:
        last_states = sim[0][-1]
        players_states = last_states.players_state
        players_uncertainty = []
        players_duration = []
        
        for player in sim[1]:
            player_uncertainty = mean(player.decisions_count) * (1 - player.knowledge)
            players_uncertainty.append(player_uncertainty)
        
        for player in players_states:
            players_duration.append(player.turns_alive)
        
        e_duration = mean(players_duration)
        sim_entertaiment = mean([ uncert * e_duration for uncert in players_uncertainty ])
        simulations_entertaiment.append(sim_entertaiment)
    
    return mean(simulations_entertaiment)
            
            



def knowledge_gen(x, y):
    while True:
        yield normalvariate(x, y)


def diff_gen1():
    while  True:
        yield uniform(0, 1)


def diff_gen2(x, y):
    while True:
        yield normalvariate(x, y)
    

def create_generate_initial_state_function(n_board, n_players, diff_gen):
    def f():
        cards = [Monster(0, 0, next(diff_gen)) for _ in range(n_board ** 2 - 1)]
        cards += [DungeonMaster(0, 0, uniform(0.3, 1))]
        choice(cards[:-1]).add_treasure(DungeonMap())
        for n, item in [(30, EnergyDrink)]:
            for m in sample(cards[:-1], n):
                m.add_treasure(item())
        shuffle(cards)

        for i, card in enumerate(cards):
            card.move(i//n_board, i%n_board)
        
        board = NDTableState(n_board, cards)
        players_state = [ NDPlayerState(i, 4) for i in range(n_players) ]
        
        return create_game_state(board, players_state)
    return f


def create_players_generator(n_players, knowledge_generator):
    def f():
        return [ NDPlayerAgent(next(knowledge_generator)) for _ in range(3) ]
    return f


if __name__ == '__main__':
    state_generator = create_generate_initial_state_function(6, 3, diff_gen1())
    players_generator = create_players_generator(3, knowledge_gen(0.5, 1))
    b = calculate_metric(num_dg_game, state_generator, players_generator, 100, calculate_b)
    print(b)

    state_generator = create_generate_initial_state_function(6, 3, diff_gen2(0.5, 1/b))
    players_generator = create_players_generator(3, knowledge_gen(0.5, 1/b))
    entertaiment = calculate_metric(num_dg_game, state_generator, players_generator, 100, calculate_entertaiment) 
    print(entertaiment)
            