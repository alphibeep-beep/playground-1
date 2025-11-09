# Frontier Dominion Prototype

This repository contains Frontier Dominion, a Wild West grand strategy experience. You
will guide the Frontier League as it expands across a living frontier filled with rival
factions, colourful towns, and tactical skirmishes.

## Features

- Expanded campaign map with six handcrafted territories and three competing factions
- Upgradable settlements, unit recruitment, and treasury management
- Tactical battle simulator with detailed combat reports
- Dynamic AI opponents who collect income, recruit troops, and launch invasions
- Command-line interface featuring an illustrated ASCII world map and event log
- Automated test suite covering the core mechanics

## Getting Started

Create a virtual environment and install the dependencies (only `pytest` is required for
running the test suite).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # optional if you create one
```

Run the command-line experience:

```bash
python -m wild_west_strategy.cli
```

## Playing Frontier Dominion

1. **Survey the frontier.** Every turn begins with a status panel summarising your
   treasury, settlements, and the latest headlines. Use the `m` action to view the ASCII
   world map highlighting who controls each territory.
2. **Build your economy.** Collect income (`c`) to fill the treasury, then invest in
   structures (`b`) to raise prosperity and increase long-term revenue.
3. **Raise an army.** Recruit militia, cavalry, or artillery (`r`) from any controlled
   town. Strong garrisons are essential before marching on a rival.
4. **Seize the initiative.** Launch attacks (`a`) against adjacent enemy territories and
   break their lines. Victory transfers control of the settlement and establishes a fresh
   garrison to hold it.
5. **End the turn.** When you are ready, end the turn (`e`). Rival factions will respond
   by gathering taxes, reinforcing, and potentially counterattacking.

The campaign concludes in one of three ways:

- You conquer every rival territory (instant victory).
- You lose every settlement (defeat).
- The turn limit (25) is reached; whichever side controls the most territory wins.

Use `v` at any time for a detailed breakdown of your realm, `m` for the strategic map,
and `q` if you wish to retire early.

Run tests with:

```bash
pytest
```
