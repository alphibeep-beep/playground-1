"""Game state management for the Wild West strategy game."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .battle import BattleReport, resolve_battle
from .entities import (
    StructureBlueprint,
    UnitTemplate,
    default_structures,
    default_templates,
)
from .world import Faction, World, create_default_world


@dataclass
class GameConfig:
    max_turns: int = 25
    starting_templates: Dict[str, UnitTemplate] = field(default_factory=default_templates)
    structure_catalog: Dict[str, StructureBlueprint] = field(default_factory=default_structures)
    ai_recruitment_probability: float = 0.7
    ai_attack_probability: float = 0.4


@dataclass
class GameState:
    world: World
    player_faction: str
    turn: int = 1
    config: GameConfig = field(default_factory=GameConfig)
    event_log: List[str] = field(default_factory=list)
    game_over: bool = False
    victor: Optional[str] = None
    rng: random.Random = field(default_factory=random.Random)

    def current_faction(self) -> Faction:
        return self.world.faction(self.player_faction)

    def available_recruits(self) -> Dict[str, UnitTemplate]:
        return self.config.starting_templates

    def available_structures(self) -> Dict[str, StructureBlueprint]:
        return self.config.structure_catalog

    def log_event(self, message: str) -> None:
        self.event_log.append(message)
        if len(self.event_log) > 15:
            self.event_log.pop(0)

    def enemies(self) -> List[Faction]:
        return [f for name, f in self.world.factions.items() if name != self.player_faction]

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
        self.log_event(
            f"{faction.name} raised {quantity} unit{'s' if quantity != 1 else ''} of {template.name} in {settlement_name}."
        )
        return total_cost

    def collect_income(self) -> int:
        faction = self.current_faction()
        income = faction.income()
        faction.treasury += income
        self.log_event(f"{faction.name} collected ${income} in revenue.")
        return income

    def build_structure(self, settlement_name: str, structure_key: str) -> int:
        faction = self.current_faction()
        if settlement_name not in faction.territories:
            raise ValueError("Cannot develop a settlement you do not control")
        structures = self.available_structures()
        if structure_key not in structures:
            raise KeyError(f"Unknown structure: {structure_key}")
        blueprint = structures[structure_key]
        if faction.treasury < blueprint.cost:
            raise ValueError("Insufficient funds for construction")
        faction.treasury -= blueprint.cost
        level = faction.territories[settlement_name].settlement.improve_structure(
            structure_key, blueprint
        )
        self.log_event(
            f"{settlement_name} upgraded the {blueprint.name} to level {level}."
        )
        return level

    def end_turn(self) -> None:
        if self.game_over:
            return
        faction = self.current_faction()
        faction.pay_upkeep()
        faction.reinforce_garrisons()
        self.log_event(f"{faction.name} paid upkeep and reinforced garrisons.")
        self._run_ai_turns()
        self.turn += 1
        self._check_victory_conditions()

    def attack(self, attacking_territory: str, defending_territory: str) -> BattleReport:
        report = self._resolve_attack(self.player_faction, attacking_territory, defending_territory)
        if report.attacker_won:
            self.log_event(
                f"{self.player_faction} seized {defending_territory} after {report.rounds} rounds!"
            )
        else:
            self.log_event(
                f"The assault on {defending_territory} faltered after {report.rounds} rounds."
            )
        self._check_victory_conditions()
        return report

    def _resolve_attack(
        self, attacker_name: str, attacking_territory: str, defending_territory: str
    ) -> BattleReport:
        attacker_faction = self.world.faction(attacker_name)
        if attacking_territory not in attacker_faction.territories:
            raise ValueError("Cannot attack from a territory you do not control")
        attacker_territory = attacker_faction.territories[attacking_territory]
        defender_territory = self.world.territory(defending_territory)
        if defending_territory not in attacker_territory.neighbors:
            raise ValueError("Territories must be adjacent to attack")
        attacker_army = attacker_territory.settlement.garrison
        defender_army = defender_territory.settlement.garrison
        report = resolve_battle(attacker_army, defender_army)
        if report.attacker_won:
            loser_faction = self.world.faction(defender_territory.controlling_faction)
            loser_faction.remove_territory(defending_territory)
            attacker_faction.add_territory(defender_territory)
            defender_territory.settlement.garrison.units.clear()
            defender_territory.settlement.recruit(self.config.starting_templates["militia"], 1)
        return report

    def _run_ai_turns(self) -> None:
        if self.game_over:
            return
        for faction in self.enemies():
            self._ai_collect_income(faction)
            if faction.treasury <= 0 or not faction.territories:
                continue
            if self.rng.random() < self.config.ai_recruitment_probability:
                self._ai_recruit(faction)
            if self.rng.random() < self.config.ai_attack_probability:
                self._ai_attack(faction)

    def _ai_collect_income(self, faction: Faction) -> None:
        income = faction.income()
        if income:
            faction.treasury += income
            self.log_event(f"{faction.name} collected ${income} in taxes.")

    def _ai_recruit(self, faction: Faction) -> None:
        settlements = list(faction.territories.values())
        if not settlements:
            return
        settlement = max(settlements, key=lambda terr: terr.settlement.population)
        templates = list(self.available_recruits().values())
        if not templates:
            return
        template = self.rng.choice(templates)
        affordable = max(1, min(3, faction.treasury // template.cost))
        if affordable <= 0:
            return
        quantity = self.rng.randint(1, affordable)
        cost = template.cost * quantity
        if cost > faction.treasury:
            return
        faction.treasury -= cost
        settlement.settlement.recruit(template, quantity)
        self.log_event(
            f"{faction.name} recruited {quantity} {template.name} in {settlement.name}."
        )

    def _ai_attack(self, faction: Faction) -> None:
        potential_attacks: List[tuple[str, str]] = []
        for territory in sorted(faction.territories.values(), key=lambda terr: terr.name):
            if not territory.settlement.garrison.has_units():
                continue
            for neighbor in territory.neighbors:
                owner = self.world.territory(neighbor).controlling_faction
                if owner != faction.name:
                    potential_attacks.append((territory.name, neighbor))
        if not potential_attacks:
            return
        origin, target = self.rng.choice(potential_attacks)
        report = self._resolve_attack(faction.name, origin, target)
        if report.attacker_won:
            self.log_event(
                f"{faction.name} captured {target} after {report.rounds} rounds."
            )
        else:
            self.log_event(
                f"{faction.name}'s assault from {origin} on {target} was repelled."
            )

    def _check_victory_conditions(self) -> None:
        if self.game_over:
            return
        player = self.current_faction()
        enemy_territories = [
            territory
            for faction in self.enemies()
            for territory in faction.territories.values()
        ]
        if not player.territories:
            self.game_over = True
            self.victor = "Defeat"
            self.log_event("Your influence has collapsed across the frontier.")
            return
        if not enemy_territories:
            self.game_over = True
            self.victor = "Victory"
            self.log_event("All rival factions have been subdued. The frontier is yours!")
            return
        if self.turn > self.config.max_turns:
            self.game_over = True
            player_control = len(player.territories)
            enemy_control = sum(len(faction.territories) for faction in self.enemies())
            if player_control >= enemy_control:
                self.victor = "Victory"
                self.log_event(
                    "The campaign ends in triumph as your territories outnumber your rivals."
                )
            else:
                self.victor = "Defeat"
                self.log_event("Time has run out before you could unite the frontier.")

    def describe_state(self) -> str:
        faction = self.current_faction()
        territories: List[str] = []
        for territory in sorted(faction.territories.values(), key=lambda terr: terr.name):
            settlement = territory.settlement
            garrison = settlement.garrison
            structures = ", ".join(
                f"{name} Lv.{level}" for name, level in settlement.structures.items()
            )
            if not structures:
                structures = "No upgrades"
            territories.append(
                f"- {territory.name}: pop {settlement.population}, prosperity {settlement.prosperity}, "
                f"garrison {len(garrison.units)} units, structures [{structures}]"
            )
        standings = self._faction_standings()
        events = "\n".join(self.event_log[-5:]) if self.event_log else "No notable events yet."
        status = f"Turn {self.turn}/{self.config.max_turns} - Treasury ${faction.treasury}\n"
        status += "Your Territories:\n" + "\n".join(territories)
        status += "\n\nFaction Standings:\n" + standings
        status += "\n\nRecent Events:\n" + events
        if self.game_over and self.victor:
            status += f"\n\nOutcome: {self.victor}!"
        return status

    def _faction_standings(self) -> str:
        factions = list(self.world.factions.values())
        standings = sorted(
            (
                faction.name,
                len(faction.territories),
                faction.treasury,
            )
            for faction in factions
        )
        standings.sort(key=lambda item: (-item[1], -item[2], item[0]))
        lines = [
            f"{name}: {territories} territories, treasury ${treasury}" for name, territories, treasury in standings
        ]
        return "\n".join(lines)


def new_game(player_faction: str = "Frontier League") -> GameState:
    world = create_default_world()
    state = GameState(world=world, player_faction=player_faction)
    state.log_event("The Frontier League gathers its council to chart a path west.")
    return state
