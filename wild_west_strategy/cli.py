"""Simple command line interface for the Wild West strategy game."""
from __future__ import annotations

from typing import Callable, Dict

from .game import GameState, new_game


ActionHandler = Callable[[GameState], None]


def prompt_choice(prompt: str, options: Dict[str, str]) -> str:
    print(prompt)
    for key, description in options.items():
        print(f"  [{key}] {description}")
    choice = input("> ").strip().lower()
    if choice not in options:
        raise ValueError("Invalid option selected")
    return choice


def action_view_state(state: GameState) -> None:
    print(state.describe_state())


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


def main() -> None:
    state = new_game()
    actions: Dict[str, tuple[str, ActionHandler]] = {
        "v": ("View state", action_view_state),
        "c": ("Collect income", action_collect_income),
        "r": ("Recruit units", action_recruit),
        "a": ("Attack neighboring territory", action_attack),
        "e": ("End turn", action_end_turn),
        "q": ("Quit", lambda _: exit()),
    }
    print("Welcome to Frontier Dominion! A Wild West grand strategy prototype.")
    while state.turn <= state.config.max_turns:
        print()
        choice = prompt_choice("Choose an action:", {key: desc for key, (desc, _) in actions.items()})
        _, handler = actions[choice]
        try:
            handler(state)
        except Exception as exc:  # pragma: no cover - user input errors
            print(f"Action failed: {exc}")


if __name__ == "__main__":
    main()
