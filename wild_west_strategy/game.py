"""Game state management for the Wild West strategy game."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .battle import BattleReport, resolve_battle
from .entities import Army, Settlement, UnitTemplate, default_templates
from .world import Faction, Territory, World, create_default_world


@dataclass
class GameConfig:
    max_turns: int = 20
    starting_templates: Dict[str, UnitTemplate] = field(default_factory=default_templates)


@dataclass
class GameState:
    world: World
    player_faction: str
    turn: int = 1
    config: GameConfig = field(default_factory=GameConfig)

    def current_faction(self) -> Faction:
        return self.world.faction(self.player_faction)

    def available_recruits(self) -> Dict[str, UnitTemplate]:
        return self.config.starting_templates

    def recruit(self, settlement_name: str, template_key: str, quantity: int = 1) -> int:
        templates = self.available_recruits()
        if template_key not in templates:
            raise KeyError(f"Unknown unit template: {template_key}")
        faction = self.current_faction()
        if settlement_name not in faction.territories:
            raise ValueError("Cannot recruit from a settlement you do not control")
        template = templates[template_key]
        total_cost = template.cost * quantity
        if faction.treasury < total_cost:
            raise ValueError("Insufficient funds for recruitment")
        faction.treasury -= total_cost
        faction.territories[settlement_name].settlement.recruit(template, quantity)
        return total_cost

    def collect_income(self) -> int:
        faction = self.current_faction()
        income = faction.income()
        faction.treasury += income
        return income

    def end_turn(self) -> None:
        faction = self.current_faction()
        faction.pay_upkeep()
        faction.reinforce_garrisons()
        self.turn += 1

    def attack(self, attacking_territory: str, defending_territory: str) -> BattleReport:
        faction = self.current_faction()
        if attacking_territory not in faction.territories:
            raise ValueError("You may only attack from your own territories")
        attacker_territory = faction.territories[attacking_territory]
        defender_territory = self.world.territory(defending_territory)
        if defending_territory not in attacker_territory.neighbors:
            raise ValueError("Territories must be adjacent to attack")
        attacker_army = attacker_territory.settlement.garrison
        defender_army = defender_territory.settlement.garrison
        report = resolve_battle(attacker_army, defender_army)
        if report.attacker_won:
            loser_faction = self.world.faction(defender_territory.controlling_faction)
            loser_faction.remove_territory(defending_territory)
            faction.add_territory(defender_territory)
        return report

    def describe_state(self) -> str:
        faction = self.current_faction()
        territories: List[str] = []
        for territory in faction.territories.values():
            settlement = territory.settlement
            garrison = settlement.garrison
            territories.append(
                f"- {territory.name}: pop {settlement.population}, prosperity {settlement.prosperity}, "
                f"garrison {len(garrison.units)} units"
            )
        return (
            f"Turn {self.turn}\n"
            f"Faction: {faction.name}\n"
            f"Treasury: ${faction.treasury}\n"
            "Territories:\n" + "\n".join(territories)
        )


def new_game(player_faction: str = "Frontier League") -> GameState:
    world = create_default_world()
    return GameState(world=world, player_faction=player_faction)
