import numpy as np
from random import normalvariate, uniform, choice, sample, shuffle
from Game.State import create_game_state, print_state
from numeric_dungeon_player import NDPlayerAgent
from numeric_dungeon_domain import Monster, DungeonMaster, DungeonMap, EnergyDrink
from numeric_dungeon_states import NMPlayerState, NMTableState
from numeric_dungeon_game import num_dg_game, who_plays, end_condition

def simulate(n_players, n_board, players_life, items, knowledge_generator, diff_generator, dm_diff):
    cards = [Monster(0, 0, next(diff_generator)) for _ in range(n_board ** 2 - 1)]
    cards += [DungeonMaster(0, 0, dm_diff)]
    choice(cards[:-1]).add_treasure(DungeonMap())
    for n, item in items:
        for m in sample(cards[:-1], n):
            m.add_treasure(item())
    shuffle(cards)
    for i, card in enumerate(cards):
        card.move(i//n_board, i%n_board)
    
    board = NMTableState(n_board, cards)
    players_state = [ NMPlayerState(i, players_life) for i in range(n_players)]
    players = [ NDPlayerAgent(next(knowledge_generator)) for _ in range(n_players) ]
    sim = num_dg_game.get_game_instance(create_game_state(board, players_state), players, who_plays, end_condition)
    
    for _ in sim:
        #print_state(s)
        pass
    return (sim.actual_state, players)


def knowledge_gen():
    while True:
        yield normalvariate(0.5, 1)

def knowledge_gen2(x, y):
    while True:
        yield normalvariate(x, y)

def diff_gen():
    while  True:
        yield uniform(0, 1)

def diff_gen2(x, y):
    while True:
        yield normalvariate(x, y)


if __name__ == "__main__":
    sims = [ simulate(3, 6, 4, [(30, EnergyDrink)],knowledge_gen(), diff_gen(), uniform(0.3, 1)) for _ in range(100) ]
    possible_plays_per_game = [[p.decisions_count for p in s[1]] for s in sims ]

    possible_plays_per_player = []
    for p in possible_plays_per_game:
        possible_plays_per_player += p
    possible_plays = []
    for p in possible_plays_per_player:
        possible_plays += p
    
    b = np.mean(possible_plays)
    sims = [ simulate(3, 6, 4, [(3, EnergyDrink)],knowledge_gen2(0.5, 1/b), diff_gen2(0.3, 1/b), uniform(0.3, 1)) for _ in range(100) ]
    sim_entertaiment = []
    for sim in sims:
        player_incert = []
        player_duration = []
        for player in sim[1]:
            player_incert.append(np.mean(player.decisions_count) * (1 - player.knowledge))
        for player in sim[0].players_state:
            player_duration.append(player.turns_alive)
        e_dur = np.mean(player_duration)
        players_entertaiment = [i*e_dur for i in player_incert]
        sim_entertaiment.append(np.mean(players_entertaiment))
    print(np.mean(sim_entertaiment))

