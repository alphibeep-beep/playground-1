"""World map and factions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .entities import Army, Settlement


@dataclass
class Territory:
    name: str
    settlement: Settlement
    neighbors: List[str]
    controlling_faction: str


@dataclass
class Faction:
    name: str
    treasury: int
    territories: Dict[str, Territory] = field(default_factory=dict)
    armies: Dict[str, Army] = field(default_factory=dict)

    def income(self) -> int:
        return sum(territory.settlement.income() for territory in self.territories.values())

    def pay_upkeep(self) -> None:
        upkeep_cost = sum(army.upkeep() for army in self.armies.values())
        self.treasury = max(0, self.treasury - upkeep_cost)

    def reinforce_garrisons(self) -> None:
        for territory in self.territories.values():
            territory.settlement.garrison.remove_dead()

    def add_territory(self, territory: Territory) -> None:
        self.territories[territory.name] = territory
        territory.controlling_faction = self.name

    def remove_territory(self, territory_name: str) -> Optional[Territory]:
        return self.territories.pop(territory_name, None)


@dataclass
class World:
    territories: Dict[str, Territory]
    factions: Dict[str, Faction]

    def territory(self, name: str) -> Territory:
        return self.territories[name]

    def faction(self, name: str) -> Faction:
        return self.factions[name]

    def connected(self, start: str, end: str) -> bool:
        visited = set()
        stack = [start]
        while stack:
            current = stack.pop()
            if current == end:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(self.territories[current].neighbors)
        return False

    def move_army(self, faction_name: str, army_name: str, destination: str) -> None:
        faction = self.faction(faction_name)
        if army_name not in faction.armies:
            raise ValueError(f"Faction {faction_name} has no army named {army_name}")
        army = faction.armies[army_name]
        for territory in faction.territories.values():
            if army in territory.settlement.garrison.units:
                raise ValueError("Army is part of a garrison and cannot move independently")
        # movement is abstracted; we simply note the army's current location via dictionary
        for territory in self.territories.values():
            if territory.name == destination:
                if destination not in faction.territories:
                    raise ValueError("Armies may only move within controlled territory")
                # track by storing mapping in armies dict
                break
        faction.armies[army_name] = army


def create_default_world() -> World:
    """Create a compact default scenario for demonstration and testing."""

    dry_gulch = Territory(
        name="Dry Gulch",
        settlement=Settlement(name="Dry Gulch", population=1200, prosperity=3, defenses=5),
        neighbors=["Copper Ridge"],
        controlling_faction="Frontier League",
    )
    copper_ridge = Territory(
        name="Copper Ridge",
        settlement=Settlement(name="Copper Ridge", population=900, prosperity=2, defenses=4),
        neighbors=["Dry Gulch", "Riverbend"],
        controlling_faction="Frontier League",
    )
    riverbend = Territory(
        name="Riverbend",
        settlement=Settlement(name="Riverbend", population=1500, prosperity=4, defenses=6),
        neighbors=["Copper Ridge"],
        controlling_faction="Desert Union",
    )

    frontier_league = Faction(name="Frontier League", treasury=500)
    desert_union = Faction(name="Desert Union", treasury=450)

    frontier_league.add_territory(dry_gulch)
    frontier_league.add_territory(copper_ridge)
    desert_union.add_territory(riverbend)

    return World(
        territories={t.name: t for t in [dry_gulch, copper_ridge, riverbend]},
        factions={f.name: f for f in [frontier_league, desert_union]},
    )
