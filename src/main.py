from math import sqrt
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


def calculate_entertaiment2(sims_results):
    last_states = [sim[0][-1] for sim in sims_results]

    simulations_entertaiment = []

    for sim in sims_results:
        last_states = sim[0][-1]
        players_states = last_states.players_state
        players_uncertainty = []
        players_duration = []
        players_e_decisions = []
        
        for player in sim[1]:
            players_e_decisions.append(mean(player.decisions_count))
            player_uncertainty = mean(player.decisions_count) * (1 - player.knowledge)
            players_uncertainty.append(player_uncertainty)
        
        for player in players_states:
            players_duration.append(player.turns_alive)
        
        e_duration = mean(players_duration)
        #sim_entertaiment = mean([ uncert * e_duration for uncert in players_uncertainty ])
        s = [ 1/(
                    (abs(players_duration[i]/players_e_decisions[i] - players_uncertainty[i]) 
                    * (1 + abs(e_duration - players_duration[i]))) 
                ) for i in range(len(players_states))]
        simulations_entertaiment.append(mean(s))
    
    return mean(simulations_entertaiment)
            

def calculate_entertaiment1(sims_result):
    simulations_results = []

    for sim in sims_result:
        players_complexity = []
        players_uncertainty = []
        turns_duration = []
        players_entertaiment = []
        players_turns_alive = [len(p.decisions_count) for p in sim[1]]

        for i in range(len(sim[1])):
            total_plays = sum(sim[1][i].decisions_count)
            questions_answered = sim[0][-1].players_state[i].questions_answered
            players_complexity.append(total_plays + ( 1 - sim[1][i].knowledge ) * (questions_answered * players_turns_alive[i]))
            players_uncertainty.append(mean(sim[1][i].decisions_count) * ( 1 - sim[1][i].knowledge ))

        for i in range(max(players_turns_alive)):
            plays_in_turn = []
            for j in range(len(sim[1])):
                try:
                    plays_in_turn.append(sim[1][j].decisions_count[i])
                except:
                    pass
            turns_duration.append(mean(plays_in_turn) * len(plays_in_turn))

        e_turn_duration = mean(turns_duration)
        game_duration = max(players_turns_alive) * e_turn_duration
        participation = []
        for player_turns_alive in players_turns_alive:
            participation.append(e_turn_duration * player_turns_alive)
        
        players_participation = []
        players_hope = []
        for i in range(len(sim[1])):
            player_participation = participation[i] / game_duration
            players_participation.append(player_participation)
            player_hope = players_uncertainty[i] / players_complexity[i]
            players_hope.append(player_hope)
            players_entertaiment.append( player_hope * player_participation )

        simulations_results.append((mean(players_participation), mean(players_hope), mean(players_complexity), mean(players_uncertainty), mean(players_entertaiment))) 

    
    results = []
    for i in range(5):
        metric = [x[i] for x in simulations_results]
        results.append(mean(metric))
    return results





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
        for n, item in [(35, EnergyDrink)]:
            for _ in range(n)
                choice(cards[:35]).add_treasure(item())
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
    print("E(b): ",b)

    state_generator = create_generate_initial_state_function(6, 3, diff_gen2(0.5, sqrt(1/b)))
    players_generator = create_players_generator(3, knowledge_gen(0.2, sqrt(1/b)))
    results = calculate_metric(num_dg_game, state_generator, players_generator, 100, calculate_entertaiment1) 
    print("Participacion: ",results[0])
    print("Esperanza: ", results[1])
    print("Complejidad: ", results[2])
    print("Incertidumbre: ", results[3])
    print("Entretenimiento ", results[4])