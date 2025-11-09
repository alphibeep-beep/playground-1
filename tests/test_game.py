from wild_west_strategy.game import GameState, new_game


def test_collect_income_increases_treasury():
    state = new_game()
    faction = state.current_faction()
    initial = faction.treasury
    income = state.collect_income()
    assert faction.treasury == initial + income


def test_recruit_spends_treasury_and_adds_units():
    state = new_game()
    faction = state.current_faction()
    territory = next(iter(faction.territories.values()))
    initial_treasury = faction.treasury
    cost = state.recruit(territory.name, "militia", quantity=2)
    assert faction.treasury == initial_treasury - cost
    assert len(territory.settlement.garrison.units) >= 2
