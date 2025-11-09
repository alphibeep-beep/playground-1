from wild_west_strategy.battle import resolve_battle
from wild_west_strategy.entities import army_from_templates


def test_battle_resolves_with_seed():
    attackers = army_from_templates("Attackers", ["militia", "cavalry"])
    defenders = army_from_templates("Defenders", ["militia"])
    report = resolve_battle(attackers, defenders, seed=42)
    assert report.attacker_won is True
    assert report.rounds <= 20
