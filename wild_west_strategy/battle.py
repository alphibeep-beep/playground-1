"""Battle resolution logic."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Tuple

from .entities import Army, Unit


@dataclass
class BattleReport:
    attacker_losses: int
    defender_losses: int
    attacker_won: bool
    rounds: int


def simulate_round(attacking_units: Iterable[Unit], defending_units: Iterable[Unit], rng: random.Random) -> Tuple[int, int]:
    attacker_damage = sum(max(0, unit.attack + rng.randint(-3, 3)) for unit in attacking_units)
    defender_damage = sum(max(0, unit.attack + rng.randint(-3, 3)) for unit in defending_units)
    return attacker_damage, defender_damage


def resolve_battle(attacker: Army, defender: Army, seed: int | None = None) -> BattleReport:
    """Resolve a battle between two armies.

    A deterministic seed can be provided for testing purposes.
    """

    rng = random.Random(seed)
    rounds = 0
    attacker_losses = 0
    defender_losses = 0

    while attacker.has_units() and defender.has_units() and rounds < 20:
        rounds += 1
        atk_damage, def_damage = simulate_round(attacker.units, defender.units, rng)
        defender_losses += apply_damage(defender, atk_damage)
        attacker_losses += apply_damage(attacker, def_damage)

    attacker_won = defender.has_units() is False and attacker.has_units()
    defender.remove_dead()
    attacker.remove_dead()
    return BattleReport(
        attacker_losses=attacker_losses,
        defender_losses=defender_losses,
        attacker_won=attacker_won,
        rounds=rounds,
    )


def apply_damage(army: Army, damage: int) -> int:
    losses = 0
    for unit in army.units:
        if not unit.is_alive():
            continue
        mitigated = max(0, damage - unit.defense)
        unit.health = max(0, unit.health - mitigated)
        if unit.health == 0:
            losses += 1
    return losses
