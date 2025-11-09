from wild_west_strategy.game import GameState, new_game
from wild_west_strategy.ui import render_world_map


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


def test_build_structure_consumes_treasury_and_levels_up():
    state = new_game()
    faction = state.current_faction()
    territory = next(iter(faction.territories.values()))
    structures = state.available_structures()
    key, blueprint = next(iter(structures.items()))
    initial_level = territory.settlement.structures.get(key, 0)
    initial_treasury = faction.treasury
    state.build_structure(territory.name, key)
    assert territory.settlement.structures[key] == initial_level + 1
    assert faction.treasury == initial_treasury - blueprint.cost


def test_render_world_map_contains_territories():
    state = new_game()
    map_output = render_world_map(state)
    assert "Dry Gulch" in map_output
    assert "Riverbend" in map_output
