from itertools import groupby, filterfalse
from random import randint, choice, shuffle
from Game.Game import Game, GameDescriptor, GameNode
from Game.State import create_game_state, print_state
from numeric_dungeon_states import NMTableState, NMPlayerState
from numeric_dungeon_domain import Monster, DungeonMaster, DungeonMap, MasterKey
from numeric_dungeon_plays import DecisionYes
from numeric_dungeon_player import NDPlayer


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
                                 GameNode("pvp_battle", default = "end_turn"),
                                 GameNode("end_turn", default = "move")
                             ]) 


@num_dg_game.action("move", True)
def move_player(state, play):
    board = state.table_state.board 
    t_state = state.table_state
    actual_player_index = t_state.actual_player
    actual_player = state.players_state[actual_player_index]
    
    n_row, n_col = len(board), len(board[0])
    fail_moves = 1
    
    row, col = randint(0, 5) % n_row, randint(0, 5) % n_col

    while t_state[(row, col)].is_empty() and fail_moves < MAX_FAIL_MOVE:
        row = randint(0, 5) % n_row
        col = randint(0, 5) % n_col
        fail_moves += 1
    
    if fail_moves is MAX_FAIL_MOVE:
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
    if actual_player.have_treasure(play.treasure):
        return play.treasure.reduce(state)
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
    
    bfs_queue = [ dungeon_master.position ]
    players_founded = []
    next_lvl = []
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
            next_lvl.extend(neigs)
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
    return t_state[t_state.dungeon_master.position].have_player()

@num_dg_game.action("prepare_battles")
def prepare_battles(state):
    t_state = state.table_state
    if t_state.last_move_failed:
        dm = t_state.dungeon_master
        t_state.targets = [ dm ]
        t_state.attacker = next(filter(lambda h : isinstance(h, NMPlayerState), t_state[dm.position].habitants))
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

@num_dg_game.goto("start_battle", "pvp_battle")
def start_battle__pvp_battle_condition(state):
    return isinstance(state.table_state.target, NMPlayerState) 


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
    if t_state.question[play.index]:
        hit(t_state.attacker, t_state.target)
    else:
        hit(t_state.target, t_state.attacker)
    t_state.target
    return state

@num_dg_game.goto("pve_battle", "pve_battle")
def pve_battle__pve_battle(state):
    t_state = state.table_state
    return all([ t_state.target.in_attack, t_state.target.is_alive(), t_state.attacker.is_alive() ])

@num_dg_game.action("pvp_battle")
def pvp_battle_ask(state, play):
    state.table_state.question = play.question

@num_dg_game.action("pvp_battle")
def pvp_battle_response(state, play):
    t_state = state.table_state
    if t_state.question[play.index]:
        hit(t_state.attacker, t_state.target)
    else:
        hit(t_state.target, t_state.attacker)
    return state

@num_dg_game.goto("pvp_battle", "pvp_battle")
def pvp_battle__pvp_battle(state):
    t_state = state.table_state
    return t_state.attacker.is_alive() and t_state.target.is_alive()

@num_dg_game.action("end_turn")
def clean_cell(state):
    pos = None
    s_state = state.table_state
    if state.table_state.last_move_failed:
        pos = s_state.dungeon_master.position
    else:
        pos = state.players_state[s_state.actual_player].position
    
    cell = s_state[pos]
    cell.clean()

    return state

@num_dg_game.action("end_turn")
def shrink_board(state):
    board = state.table_state.board
    n_col = len(board[0])
    #Remove empty rows
    state.table_state.board = list(filterfalse(lambda r : all(map(lambda c: c.is_empty(), r)) , board))

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
    actual_player = (state.table_state.actual_player + 1) % n_players
    players = state.players_state
    
    while not players[actual_player].is_alive():
        actual_player = (actual_player + 1) % n_players
    
    state.table_state.actual_player = actual_player

    return state


def hit(attacker, target):
    target.damage() 
    if not target.hp:
        for treasure in target.get_treasures():
            attacker.add_treasure(treasure)

def get_neigs(pos, max_row, max_col):
    dir_array = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    valid_pos = lambda pos : pos[0] >= 0 and pos[0] <= max_row and pos[1] >= 0 and pos[1] <= max_col 
    neigs = [ (pos[0] + x[0], pos[1], + x[1]) for x in dir_array if valid_pos((pos[0] + x[0], pos[1], + x[1])) ]
    return neigs
    
def who_plays(state):
    t_state = state.table_state
    p_state = state.players_state
    if t_state.attacker != None:
        return p_state.index(t_state.attacker)
    return t_state.actual_player

def end_condition(state):
    return all(map(lambda p : not p.is_alive(), state.players_state))
        
if __name__ == '__main__':
    cards = [Monster(0, 0) for _ in range(35)] + [DungeonMaster(0, 0)]
    choice(cards[:35]).add_treasure(DungeonMap)
    shuffle(cards)
    for i, card in enumerate(cards):
        card.move(i//6, i%6)
    board = NMTableState(6, cards)
    p1 = NDPlayer()     
    p2 = NDPlayer()  
    g = num_dg_game.get_game_instance(create_game_state(board, [NMPlayerState("p1", 4), NMPlayerState("p2", 4)]),
                                     [p1, p2], who_plays, end_condition)
    for s in g:
        print_state(s)
        input()
    #g = num_dg_game.get_game_instance