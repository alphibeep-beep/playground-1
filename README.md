# Frontier Dominion Prototype

This repository contains a small-scale Wild West grand strategy prototype. It focuses on
turn-based settlement management and small tactical battles inspired by large-scale
strategy games while using fully original content.

## Features

- Modular core with settlements, armies, and factions
- Simple battle simulator with deterministic seeds for testing
- World map and scenario definition featuring two rival factions
- Command-line interface offering basic management actions
- Automated test suite covering the core mechanics

## Getting Started

Create a virtual environment and install the dependencies (only `pytest` is required for
running the test suite).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # optional if you create one
```

Run the command-line prototype:

```bash
python -m wild_west_strategy.cli
```

Run tests with:

```bash
pytest
```
