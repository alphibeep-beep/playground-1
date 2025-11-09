"""Core entities for the Wild West strategy game."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List


class UnitClass(Enum):
    """Broad categorisation of unit roles."""

    INFANTRY = "infantry"
    CAVALRY = "cavalry"
    ARTILLERY = "artillery"


@dataclass(frozen=True)
class UnitTemplate:
    """Definition of a recruitable unit."""

    name: str
    unit_class: UnitClass
    attack: int
    defense: int
    cost: int
    upkeep: int

    def describe(self) -> str:
        return (
            f"{self.name} ({self.unit_class.value.title()}) - "
            f"Atk {self.attack} / Def {self.defense}, Cost {self.cost}, Upkeep {self.upkeep}"
        )


@dataclass
class Unit:
    """A single unit on the battlefield."""

    template: UnitTemplate
    health: int = 100

    @property
    def attack(self) -> int:
        return self.template.attack * self.health // 100

    @property
    def defense(self) -> int:
        return self.template.defense * self.health // 100

    def is_alive(self) -> bool:
        return self.health > 0


@dataclass
class Army:
    """Collection of combat units."""

    name: str
    units: List[Unit] = field(default_factory=list)
    supplies: int = 0

    def strength(self) -> int:
        """Return combined combat strength of the army."""

        return sum(unit.attack + unit.defense for unit in self.units if unit.is_alive())

    def upkeep(self) -> int:
        return sum(unit.template.upkeep for unit in self.units if unit.is_alive())

    def add_unit(self, unit: Unit) -> None:
        self.units.append(unit)

    def remove_dead(self) -> None:
        self.units = [unit for unit in self.units if unit.is_alive()]

    def consume_supplies(self) -> None:
        self.supplies = max(0, self.supplies - len(self.units))

    def has_units(self) -> bool:
        return any(unit.is_alive() for unit in self.units)


@dataclass
class Settlement:
    """A settlement the player can manage."""

    name: str
    population: int
    prosperity: int
    defenses: int
    garrison: Army = field(default_factory=lambda: Army("Town Guard"))
    structures: Dict[str, int] = field(default_factory=dict)

    def income(self) -> int:
        base = self.population // 100 + self.prosperity
        bonus = sum(level * 5 for level in self.structures.values())
        return base + bonus

    def improve_structure(self, structure: str) -> int:
        current = self.structures.get(structure, 0) + 1
        self.structures[structure] = current
        self.prosperity += 1
        return current

    def recruit(self, template: UnitTemplate, quantity: int = 1) -> List[Unit]:
        recruits = [Unit(template=template) for _ in range(quantity)]
        for recruit in recruits:
            self.garrison.add_unit(recruit)
        return recruits


def default_templates() -> Dict[str, UnitTemplate]:
    """Return the default unit templates for the game."""

    return {
        "militia": UnitTemplate(
            name="Frontier Militia",
            unit_class=UnitClass.INFANTRY,
            attack=12,
            defense=10,
            cost=40,
            upkeep=3,
        ),
        "cavalry": UnitTemplate(
            name="Trailblazer Cavalry",
            unit_class=UnitClass.CAVALRY,
            attack=18,
            defense=12,
            cost=70,
            upkeep=5,
        ),
        "artillery": UnitTemplate(
            name="Prairie Artillery",
            unit_class=UnitClass.ARTILLERY,
            attack=25,
            defense=8,
            cost=120,
            upkeep=8,
        ),
    }


def army_from_templates(name: str, template_names: Iterable[str]) -> Army:
    templates = default_templates()
    army = Army(name=name)
    for tpl_name in template_names:
        if tpl_name not in templates:
            raise KeyError(f"Unknown unit template: {tpl_name}")
        army.add_unit(Unit(template=templates[tpl_name]))
    return army
