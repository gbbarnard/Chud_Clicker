from dataclasses import dataclass, field
import math

# -----------------------------
# Building definitions
# -----------------------------
BUILDINGS = {
    "poster": {
        "name": "Poster",
        "base_cost": 15,
        "base_cps": 0.5,
        "cost_growth": 1.15
    },
    "bot": {
        "name": "Bot",
        "base_cost": 100,
        "base_cps": 2.0,
        "cost_growth": 1.15
    },
    "factory": {
        "name": "Factory",
        "base_cost": 1100,
        "base_cps": 8.0,
        "cost_growth": 1.15
    }
}

# -----------------------------
# Upgrade definitions
# -----------------------------
UPGRADES = {
    "double_click": {
        "name": "Better Clicking",
        "cost": 50,
        "type": "click_multiplier",
        "value": 2.0
    },
    "poster_double": {
        "name": "Poster Boost",
        "cost": 200,
        "type": "building_multiplier",
        "target": "poster",
        "value": 2.0
    },
    "bot_double": {
        "name": "Bot Boost",
        "cost": 500,
        "type": "building_multiplier",
        "target": "bot",
        "value": 2.0
    },
    "global_boost": {
        "name": "Global Boost",
        "cost": 1000,
        "type": "global_multiplier",
        "value": 1.5
    }
}

# -----------------------------
# Game state
# -----------------------------
@dataclass
class GameState:
    chuds: float = 0.0
    base_click_power: float = 1.0
    buildings_owned: dict = field(default_factory=lambda: {building_id: 0 for building_id in BUILDINGS})
    upgrades_owned: set = field(default_factory=set)
    total_cps: float = 0.0


# -----------------------------
# Multiplier helpers
# -----------------------------
def get_click_value(state: GameState) -> float:
    click_value = state.base_click_power

    for upgrade_id in state.upgrades_owned:
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "click_multiplier":
            click_value *= upgrade["value"]

    return click_value


def get_building_multiplier(state: GameState, building_id: str) -> float:
    multiplier = 1.0

    for upgrade_id in state.upgrades_owned:
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "building_multiplier" and upgrade["target"] == building_id:
            multiplier *= upgrade["value"]

    return multiplier


def get_global_multiplier(state: GameState) -> float:
    multiplier = 1.0

    for upgrade_id in state.upgrades_owned:
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "global_multiplier":
            multiplier *= upgrade["value"]

    return multiplier


# -----------------------------
# CPS calculation
# -----------------------------
def calculate_total_cps(state: GameState) -> float:
    total = 0.0

    for building_id, amount_owned in state.buildings_owned.items():
        building = BUILDINGS[building_id]
        building_cps = (
            amount_owned
            * building["base_cps"]
            * get_building_multiplier(state, building_id)
        )
        total += building_cps

    total *= get_global_multiplier(state)
    return total


def refresh_cps(state: GameState):
    state.total_cps = calculate_total_cps(state)


# -----------------------------
# Passive income update
# -----------------------------
def update_game(state: GameState, dt: float):
    state.chuds += state.total_cps * dt


# -----------------------------
# Clicking
# -----------------------------
def add_manual_click(state: GameState):
    state.chuds += get_click_value(state)


# -----------------------------
# Buying buildings
# -----------------------------
def get_building_cost(building_id: str, amount_owned: int) -> int:
    building = BUILDINGS[building_id]
    raw_cost = building["base_cost"] * (building["cost_growth"] ** amount_owned)
    return math.ceil(raw_cost)


def buy_building(state: GameState, building_id: str) -> bool:
    amount_owned = state.buildings_owned[building_id]
    cost = get_building_cost(building_id, amount_owned)

    if state.chuds >= cost:
        state.chuds -= cost
        state.buildings_owned[building_id] += 1
        refresh_cps(state)
        return True

    return False


# -----------------------------
# Buying upgrades
# -----------------------------
def buy_upgrade(state: GameState, upgrade_id: str) -> bool:
    if upgrade_id in state.upgrades_owned:
        return False

    upgrade = UPGRADES[upgrade_id]
    cost = upgrade["cost"]

    if state.chuds >= cost:
        state.chuds -= cost
        state.upgrades_owned.add(upgrade_id)
        refresh_cps(state)
        return True

    return False