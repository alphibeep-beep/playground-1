from wild_west_strategy.entities import Army, Unit, default_templates


def test_default_templates_contains_expected_units():
    templates = default_templates()
    assert {"militia", "cavalry", "artillery"}.issubset(templates.keys())


def test_army_strength_accounts_for_health():
    templates = default_templates()
    militia = Unit(template=templates["militia"], health=50)
    cavalry = Unit(template=templates["cavalry"], health=100)
    army = Army(name="Test", units=[militia, cavalry])
    assert army.strength() > cavalry.attack + cavalry.defense  # additional militia contribution
    militia.health = 0
    army.remove_dead()
    assert len(army.units) == 1
