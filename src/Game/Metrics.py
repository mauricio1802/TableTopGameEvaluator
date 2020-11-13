
def calculate_metric(game, generate_initial_state, generate_players, n_sims, metric_func):
    results = []

    for _ in range(n_sims):
        initial_state = generate_initial_state()
        players = generate_players()
        game_instance = game.get_game_instance(initial_state, players)
        history = []
        for s in game_instance:
            history.append(s)
        results.append((history, players))
    
    return metric_func(results)


