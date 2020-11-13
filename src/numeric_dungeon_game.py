from itertools import groupby, filterfalse
from random import randint, choice, shuffle, uniform
from Game.Game import Game, GameDescriptor, GameNode
from Game.State import create_game_state, print_state
from numeric_dungeon_states import NDTableState, NDPlayerState
from numeric_dungeon_domain import Monster, DungeonMaster, DungeonMap, MasterKey, EnergyDrink
from numeric_dungeon_plays import DecisionYes
from numeric_dungeon_player import NDPlayer, NDPlayerAgent


MAX_FAIL_MOVE = 3

num_dg_game = GameDescriptor("move", 
                             [
                                 GameNode("move", default = "prepare_battles"), 
                                 GameNode("activate_treasure", default = "prepare_battles"),
                                 GameNode("dungeon_master_flip", default = "end_turn"),
                                 GameNode("dungeon_master_move", default = "end_turn"),
                                 GameNode("prepare_battles", default = "start_battle"),
                                 GameNode("start_battle"),
                                 GameNode("pve_battle_init", default = "pve_battle"),
                                 GameNode("pve_battle", default = "end_turn"),
                                 GameNode("pvp_battle_ask", default = "pvp_battle_answer"),
                                 GameNode("pvp_battle_answer", default = "end_turn"),
                                 GameNode("end_turn", default = "move")
                             ]) 


@num_dg_game.action("move", True)
def move_player(state, play):
    board = state.table_state.board 
    t_state = state.table_state
    actual_player_index = t_state.actual_player
    actual_player = state.players_state[actual_player_index]
   
    n_row, n_col = len(board), len(board[0])
    
    row, col = randint(0, 5) % n_row, randint(0, 5) % n_col
    roll_count = 1
    cell = t_state[(row, col)]
    while roll_count < MAX_FAIL_MOVE:
        if len(list(filterfalse(lambda m : m is actual_player, cell.habitants))) > 0: 
            break
        row, col = randint(0, 5) % n_row, randint(0, 5) % n_col
        cell = t_state[(row, col)]
        roll_count += 1
    
    if roll_count is MAX_FAIL_MOVE and len(list(filterfalse(lambda m : m is actual_player, cell.habitants))) is 0:
        t_state.last_move_failed = True

    t_state.move(actual_player, (row, col))
    
    return state


@num_dg_game.goto("move", "activate_treasure", True)
def activate_treasure_condition(state, play):
    return isinstance(play, DecisionYes)

@num_dg_game.goto("move", "dungeon_master_flip")
def flip_condition(state):
    return state.table_state.last_move_failed and not state.table_state.dungeon_master.founded

@num_dg_game.goto("move", "dungeon_master_move")
def move_dm_condition(state):
    return state.table_state.last_move_failed

@num_dg_game.action("activate_treasure", True)
def activate_treasure(state, play):
    actual_player_index = state.table_state.actual_player
    actual_player = state.players_state[actual_player_index]

    for index in sorted(play.indexes, reverse=True):
        treasure = actual_player.treasures[index]
        state = treasure.reduce(state)
        actual_player.remove_treasure(treasure)

    return state

@num_dg_game.goto("activate_treasure", "dungeon_master_flip")
def activate_flip_condition(state):
    return state.table_state.last_move_failed and not state.table_state.dungeon_master.founded

@num_dg_game.goto("activate_treasure", "dungeon_master_move")
def activate_dm_condition(state):
    return state.table_state.last_move_failed

@num_dg_game.action("dungeon_master_flip")
def flip_dungeon_master(state):
    state.table_state.dungeon_master.flip() 
    return state

@num_dg_game.action("dungeon_master_move")
def move_dungeon_master(state):
    board = state.table_state.board
    n_row, n_col = len(board), len(board[0])
    dungeon_master = state.table_state.dungeon_master
    if not dungeon_master.is_alive():
        return state
    
    bfs_queue = [ dungeon_master.position ]
    players_founded = []
    next_lvl = []
    visited = [ dungeon_master.position ]
    while bfs_queue or next_lvl:
        try:
            cell = bfs_queue.pop()
        except IndexError:
            if players_founded:
                break
            bfs_queue.extend(next_lvl)
            next_lvl = []
            cell = bfs_queue.pop()
        finally:
            neigs = filterfalse(lambda p : state.table_state[p].have_monster(), get_neigs(cell, n_row - 1, n_col - 1))
            neigs = list(filterfalse(lambda p : p in visited, neigs))
            next_lvl.extend(neigs)
            visited.extend(neigs)
            if state.table_state[cell].have_player():
                players_founded.append(cell)

    if not players_founded:
        return state


    dest = choice(players_founded)
    state.table_state.move(dungeon_master, dest)

    return state

@num_dg_game.goto("dungeon_master_move", "prepare_battles")
def dm_move_battle_condition(state):
    t_state = state.table_state
    if not state.table_state.dungeon_master.is_alive():
        return False
    return t_state[t_state.dungeon_master.position].have_player()

@num_dg_game.action("prepare_battles")
def prepare_battles(state):
    t_state = state.table_state
    if t_state.last_move_failed:
        dm = t_state.dungeon_master
        t_state.targets = [ dm ]
        t_state.attacker = next(filter(lambda h : isinstance(h, NDPlayerState), t_state[dm.position].habitants))
    else:
        p_state = state.players_state
        actual_player_index = t_state.actual_player
        actual_player = p_state[actual_player_index]
        t_state.attacker = actual_player
        t_state.targets = list(filter(lambda h : h != actual_player ,t_state[actual_player.position].habitants))
    return state



@num_dg_game.action("start_battle")
def start_battle(state):
    t_state = state.table_state
    t_state.target = t_state.targets.pop()
    return state

@num_dg_game.goto("start_battle", "pve_battle_init")
def start_battle_pve__battle_init_condition(state):
    return isinstance(state.table_state.target, (Monster, DungeonMaster))

@num_dg_game.goto("start_battle", "pvp_battle_ask")
def start_battle__pvp_battle_condition(state):
    return isinstance(state.table_state.target, NDPlayerState) 


@num_dg_game.action("pve_battle_init")
def pve_battle_init(state):
    state.table_state.target.begin_attack()
    return state

@num_dg_game.action("pve_battle")
def pve_battle(state):
    t_state = state.table_state
    t_state.question = t_state.target.get_question()
    return state

@num_dg_game.action("pve_battle", True)
def pve_battle_response(state, play):
    t_state = state.table_state
    t_state.target.attack()
    if t_state.question <= play.answer:
        hit(t_state.attacker, t_state.target)
    else:
        hit(t_state.target, t_state.attacker)
    #t_state.target
    return state

@num_dg_game.goto("pve_battle", "pve_battle")
def pve_battle__pve_battle(state):
    t_state = state.table_state
    return all([ t_state.target.in_attack, t_state.target.is_alive(), t_state.attacker.is_alive() ])

@num_dg_game.goto("pve_battle", "start_battle")
def pve_battle__start_battle(state):
    return len(state.table_state.targets) != 0

@num_dg_game.action("pvp_battle_ask", True)
def pvp_battle_ask(state, play):
    state.table_state.question = play.question
    return state

@num_dg_game.action("pvp_battle_answer", True)
def pvp_battle_response(state, play):
    t_state = state.table_state
    if t_state.question <= play.answer:
        hit(t_state.attacker, t_state.target)
    else:
        hit(t_state.target, t_state.attacker)
    return state

@num_dg_game.goto("pvp_battle_answer", "pvp_battle_ask")
def pvp_battle__pvp_battle(state):
    t_state = state.table_state
    return t_state.attacker.is_alive() and t_state.target.is_alive()

@num_dg_game.goto("pvp_battle_answer", "start_battle")
def pvp_battle_answer__start_battle(state):    
    return len(state.table_state.targets) != 0

@num_dg_game.action("end_turn")
def shrink_board(state):
    #Remove empty rows
    state.table_state.board = list(filterfalse(lambda r : all(map(lambda c: c.is_empty(), r)) , state.table_state.board))

    board = state.table_state.board
    n_col = len(board[0])
    #Remove empty columns
    n_row = len(board)
    for c in range(n_col)[::-1]:
        remove_col = True
        for r in range(n_row):
            if not board[r][c].is_empty():
                remove_col = False
                break
        if remove_col:
            for r in range(n_row):
                board[r].pop(c)
    
    #update positions
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            cell.clean()
            for hab in cell.habitants:
                hab.move(i, j)
    
    return state

@num_dg_game.action("end_turn")
def end_turn(state):
    t_state = state.table_state
    t_state.last_move_failed = False
    t_state.attacker = None
    t_state.target = None
    t_state.question = None

    return state

@num_dg_game.action("end_turn")
def change_turn(state):
    n_players = len(state.players_state)
    for p in state.players_state:
        if p.is_alive():
            p.turns_alive += 1
    state.table_state.total_turns += 1
    actual_player = (state.table_state.actual_player + 1) % n_players
    players = state.players_state
    
    while not players[actual_player].is_alive():
        actual_player = (actual_player + 1) % n_players
    
    state.table_state.actual_player = actual_player

    return state


def hit(attacker, target):
    target.damage() 
    if not target.hp:
        for treasure in target.treasures[::-1]:
            attacker.add_treasure(treasure)
            target.remove_treasure(treasure)

def get_neigs(pos, max_row, max_col):
    dir_array = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    valid_pos = lambda pos : pos[0] >= 0 and pos[0] <= max_row and pos[1] >= 0 and pos[1] <= max_col 
    neigs = [ (pos[0] + x[0], pos[1] + x[1]) for x in dir_array if valid_pos((pos[0] + x[0], pos[1] + x[1])) ]
    return neigs
    

@num_dg_game.who_plays()
def who_plays(state, node):
    t_state = state.table_state
    p_state = state.players_state
    if node == "pvp_battle_ask":
        return p_state.index(t_state.target)
    if t_state.attacker != None:
        return p_state.index(t_state.attacker)
    return t_state.actual_player


@num_dg_game.end()
def end_condition(state):
    for player in state.players_state:
        if player.have_win_requirements():
            return True
    return all(map(lambda p : not p.is_alive(), state.players_state))
        
#if __name__ == '__main__':
#    cards = [Monster(0, 0, uniform(0, 1)) for _ in range(35)] + [DungeonMaster(0, 0, uniform(0.3, 1))]
#    choice(cards[:35]).add_treasure(DungeonMap())
#    for _ in range(2):
#        choice(cards[:35]).add_treasure(EnergyDrink())
#    shuffle(cards)
#    for i, card in enumerate(cards):
#        card.move(i//6, i%6)
#    board = NMTableState(6, cards)
#    p1 = NDPlayerAgent(uniform(0.2, 1))
#    p2 = NDPlayerAgent(uniform(0.2, 1))  
#    g = num_dg_game.get_game_instance(create_game_state(board, [NMPlayerState("p1", 4 ), NMPlayerState("p2", 4)]),
#                                     [p1, p2])
#    for s in g:
#        print_state(s)
#        input()
