"""Utility helpers for rendering game information."""
from __future__ import annotations

from typing import Iterable

from .game import GameState

FACTION_SYMBOLS = {
    "Frontier League": "★",
    "Desert Union": "♞",
    "Canyon Syndicate": "♠",
}


def _faction_symbol(faction_name: str, player_faction: str) -> str:
    if faction_name == player_faction:
        return "★"
    return FACTION_SYMBOLS.get(faction_name, "✦")


def territory_badge(state: GameState, territory_name: str) -> str:
    territory = state.world.territory(territory_name)
    symbol = _faction_symbol(territory.controlling_faction, state.player_faction)
    return f"{territory_name} {symbol} ({territory.controlling_faction})"


def render_world_map(state: GameState) -> str:
    """Render a stylised ASCII map of the frontier."""

    dg = territory_badge(state, "Dry Gulch")
    cr = territory_badge(state, "Copper Ridge")
    rb = territory_badge(state, "Riverbend")
    mv = territory_badge(state, "Mesa Verde")
    ss = territory_badge(state, "Silver Springs")
    lc = territory_badge(state, "Lost Canyon")

    lines = [
        f"{dg:<32}─── {cr:<32}─── {rb}",
        " " * 14 + "\\" + " " * 27 + "/",
        f"{'':>15}{mv:<32}─── {ss}",
        " " * 52 + "│",
        " " * 49 + lc,
        "",
        "Legend: ★ You | ♞ Desert Union | ♠ Canyon Syndicate | ✦ Other faction",
    ]
    return "\n".join(lines)


def render_status_panel(state: GameState, event_count: int = 5) -> str:
    """Return a formatted status overview for the current turn."""

    faction = state.current_faction()
    header = (
        f"=== Turn {state.turn}/{state.config.max_turns} | "
        f"Treasury: ${faction.treasury} | Prosperity: "
        f"{sum(t.settlement.prosperity for t in faction.territories.values())} ==="
    )

    territory_details = [
        f"{territory.name}: pop {territory.settlement.population}, "
        f"prosperity {territory.settlement.prosperity}, "
        f"garrison {len(territory.settlement.garrison.units)} units"
        for territory in sorted(faction.territories.values(), key=lambda terr: terr.name)
    ]

    standings = [
        f"{f.name}: territories {len(f.territories)}, treasury ${f.treasury}"
        for f in sorted(
            state.world.factions.values(),
            key=lambda fac: (-len(fac.territories), -fac.treasury, fac.name),
        )
    ]

    events: Iterable[str]
    if state.event_log:
        events = state.event_log[-event_count:]
    else:
        events = ["No major events yet."]

    panel = [
        header,
        "-- Territories --",
        *territory_details,
        "",
        "-- Factions --",
        *standings,
        "",
        "-- Recent Events --",
        *events,
    ]

    if state.game_over and state.victor:
        panel.append("")
        panel.append(f"Campaign Result: {state.victor}!")

    return "\n".join(panel)
