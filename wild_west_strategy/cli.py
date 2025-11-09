"""Command line launcher for the Wild West strategy game."""
from __future__ import annotations

from typing import Callable, Dict

from .game import GameState, new_game
from .ui import render_status_panel, render_world_map


ActionHandler = Callable[[GameState], None]


def prompt_choice(prompt: str, options: Dict[str, str]) -> str:
    while True:
        print(prompt)
        for key, description in options.items():
            print(f"  [{key}] {description}")
        choice = input("> ").strip().lower()
        if choice in options:
            return choice
        print("Please choose a valid option.")


def action_view_state(state: GameState) -> None:
    print(state.describe_state())


def action_view_map(state: GameState) -> None:
    print(render_world_map(state))


def action_collect_income(state: GameState) -> None:
    income = state.collect_income()
    print(f"Collected ${income} in taxes and trade.")


def action_recruit(state: GameState) -> None:
    faction = state.current_faction()
    print("Available settlements:")
    settlements = list(faction.territories.keys())
    for idx, settlement in enumerate(settlements, start=1):
        print(f"  {idx}. {settlement}")
    selection = int(input("Select settlement: ")) - 1
    settlement_name = settlements[selection]
    recruits = state.available_recruits()
    print("Available recruits:")
    keys = list(recruits.keys())
    for idx, key in enumerate(keys, start=1):
        print(f"  {idx}. {recruits[key].describe()}")
    template = keys[int(input("Select unit type: ")) - 1]
    quantity = int(input("Quantity: "))
    state.recruit(settlement_name, template, quantity)
    print(f"Recruited {quantity} units of {recruits[template].name}.")


def action_build(state: GameState) -> None:
    faction = state.current_faction()
    settlements = list(faction.territories.values())
    if not settlements:
        print("You do not control any settlements to develop.")
        return
    print("Develop which settlement?")
    for idx, territory in enumerate(settlements, start=1):
        print(f"  {idx}. {territory.name}")
    selected = int(input("Select settlement: ")) - 1
    territory = settlements[selected]
    structures = state.available_structures()
    keys = list(structures.keys())
    print("Available structures:")
    for idx, key in enumerate(keys, start=1):
        blueprint = structures[key]
        current_level = territory.settlement.structures.get(key, 0)
        print(
            f"  {idx}. {blueprint.name} (Lv.{current_level}) - Cost ${blueprint.cost}: {blueprint.description}"
        )
    selection = int(input("Build which structure: ")) - 1
    chosen_key = keys[selection]
    level = state.build_structure(territory.name, chosen_key)
    blueprint = structures[chosen_key]
    print(f"{territory.name} upgraded the {blueprint.name} to level {level}.")


def action_attack(state: GameState) -> None:
    faction = state.current_faction()
    territories = list(faction.territories.values())
    for idx, territory in enumerate(territories, start=1):
        print(f"  {idx}. {territory.name}")
    attacker = territories[int(input("Attack from: ")) - 1]
    neighbors = attacker.neighbors
    print("Targets:")
    for idx, neighbor in enumerate(neighbors, start=1):
        print(f"  {idx}. {neighbor}")
    target_name = neighbors[int(input("Attack which territory: ")) - 1]
    report = state.attack(attacker.name, target_name)
    if report.attacker_won:
        print(f"Victory! Lost {report.attacker_losses} units.")
    else:
        print(f"Defeat. Lost {report.attacker_losses} units.")


def action_end_turn(state: GameState) -> None:
    state.end_turn()
    print("Turn ended.")


def action_quit(state: GameState) -> None:
    state.game_over = True
    state.victor = state.victor or "Retired"
    state.log_event("You chose to retire from the campaign.")
    print("You ride off into the sunset. Thanks for playing!")


def main() -> None:
    state = new_game()
    actions: Dict[str, tuple[str, ActionHandler]] = {
        "v": ("View detailed report", action_view_state),
        "m": ("View frontier map", action_view_map),
        "c": ("Collect income", action_collect_income),
        "r": ("Recruit units", action_recruit),
        "b": ("Develop settlement", action_build),
        "a": ("Attack neighboring territory", action_attack),
        "e": ("End turn", action_end_turn),
        "q": ("Quit", action_quit),
    }
    print("Welcome to Frontier Dominion! Lead the Frontier League to victory.")
    while not state.game_over:
        print()
        print(render_status_panel(state))
        print()
        choice = prompt_choice("Choose an action:", {key: desc for key, (desc, _) in actions.items()})
        _, handler = actions[choice]
        try:
            handler(state)
        except Exception as exc:  # pragma: no cover - user input errors
            print(f"Action failed: {exc}")
        if state.game_over:
            break
    print()
    print(render_status_panel(state))
    print()
    print(render_world_map(state))
    print("Frontier Dominion concluded. Share your legend with the townsfolk!")


if __name__ == "__main__":
    main()
