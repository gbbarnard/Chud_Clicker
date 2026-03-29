from dataclasses import dataclass, field
import random
import math

# -----------------------------
# Building definitions
# -----------------------------
BUILDINGS = {
    "Reddit Bots": {
        "name": "Reddit Bots",
        "base_cost": 15,
        "base_cps": 0.5,
        "cost_growth": 1.15,
        "cps_growth": 1.15,
    },
    "Gaming Pc": {
        "name": "Gaming PC",
        "base_cost": 250,
        "base_cps": 2.0,
        "cost_growth": 1.5,
        "cps_growth": 1.12,
    },
    "Waifu's": {
        "name": "Waifu's",
        "base_cost": 5000,
        "base_cps": 8.0,
        "cost_growth": 1.75,
        "cps_growth": 1.10,
    },
    "Fast Food": {
        "name": "Fast Food",
        "base_cost": 67676,
        "base_cps": 8.0,
        "cost_growth": 2.0,
        "cps_growth": 1.08,
    },
}
# -----------------------------
# Upgrade definitions
# -----------------------------
UPGRADES = {
    "redit bots": {
        "name": "Karma Farm",
        "base_cost": 50,
        "cost_growth": 1.15,
        "cps_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "building_multiplier",
        "target": "Reddit Bots",
        "required_building": "Reddit Bots",
        "value": 2.0,
    },
    "Gaming PC": {
        "name": "Overclock",
        "base_cost": 200,
        "cost_growth": 1.15,
        "cps_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "building_multiplier",
        "target": "Gaming Pc",
        "required_building": "Gaming Pc",
        "value": 2.0,
    },
    "Cardboard Cutout": {
        "name": "Cardboard Cutout",
        "base_cost": 500,
        "cost_growth": 1.15,
        "cps_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "building_multiplier",
        "target": "Waifu's",
        "required_building": "Waifu's",
        "value": 2.0,
    },
    "Fast Food": {
        "name": "Chicken Nuggys",
        "base_cost": 2500,
        "cost_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "building_multiplier",
        "target": "Fast Food",
        "required_building": "Fast Food",
        "value": 1.5,
    },
    "global_boost": {
        "name": "All the Man Needs",
        "base_cost": 6969,
        "cost_growth": 1.15,
        "cps_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "global_multiplier",
        "value": 1.5,
    },
    "Mtn Dew": {
        "name": "MTN Dew",
        "base_cost": 1500,
        "cost_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "click_multiplier",
        "value": 1.5,
    },
    "Mini Game": {
        "name": "Gamer lean",
        "base_cost": 3000,
        "cost_growth": 1.15,
        "cost_growth_steps": [
            {"level": 15, "growth": 1.5},
            {"level": 25, "growth": 1.75},
            {"level": 50, "growth": 2.0},
            {"level": 75, "growth": 2.25},
            {"level": 100, "growth": 2.5},
        ],
        "type": "mini_game_multiplier",
        "value": 1.5,
    },
}

# -----------------------------
# Game state
# -----------------------------
@dataclass
class GameState:
    chuds: float = 0.0
    base_click_power: float = 1.0
    buildings_owned: dict = field(default_factory=lambda: {building_id: 0 for building_id in BUILDINGS})
    upgrades_owned: dict = field(default_factory=lambda: {upgrade_id: 0 for upgrade_id in UPGRADES})
    total_cps: float = 0.0
    music_muted: bool = False


# -----------------------------
# Upgrade helpers
# -----------------------------
def get_upgrade_required_building(upgrade_id: str) -> str | None:
    upgrade = UPGRADES[upgrade_id]
    return upgrade.get("required_building") or upgrade.get("target")


def is_upgrade_unlocked(state: GameState, upgrade_id: str) -> bool:
    required_building = get_upgrade_required_building(upgrade_id)
    if required_building is None:
        return True
    return state.buildings_owned.get(required_building, 0) > 0


# -----------------------------
# Multiplier helpers
# -----------------------------
def get_click_value(state: GameState) -> float:
    click_value = state.base_click_power

    for upgrade_id, amount_owned in state.upgrades_owned.items():
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "click_multiplier":
            for _ in range(amount_owned):
                click_value *= upgrade["value"]

    return click_value


def get_building_upgrade_level(state: GameState, building_id: str) -> int:
    level = 0

    for upgrade_id, amount_owned in state.upgrades_owned.items():
        upgrade = UPGRADES[upgrade_id]
        if (
            upgrade.get("type") == "building_multiplier"
            and upgrade.get("target") == building_id
        ):
            level += amount_owned

    return level


def get_building_multiplier(state: GameState, building_id: str) -> float:
    """
    Every 5 upgrade levels gives one multiplier step.
    Example:
    level 0-4  -> x1
    level 5-9  -> xvalue
    level 10-14 -> xvalue^2
    """
    multiplier = 1.0

    for upgrade_id, amount_owned in state.upgrades_owned.items():
        upgrade = UPGRADES[upgrade_id]
        if (
            upgrade.get("type") == "building_multiplier"
            and upgrade.get("target") == building_id
        ):
            milestone_count = amount_owned // 5
            multiplier *= upgrade.get("value", 1.0) ** milestone_count

    return multiplier

def get_building_effective_base_cps(state: GameState, building_id: str) -> float:
    """
    Each upgrade level increases the building's base CPS
    using that building's cps_growth.
    """
    building = BUILDINGS[building_id]
    base_cps = building["base_cps"]
    cps_growth = building.get("cps_growth", 1.0)

    upgrade_level = get_building_upgrade_level(state, building_id)

    return base_cps * (cps_growth ** upgrade_level)
def get_global_multiplier(state: GameState) -> float:
    multiplier = 1.0

    for upgrade_id, amount_owned in state.upgrades_owned.items():
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "global_multiplier":
            for _ in range(amount_owned):
                multiplier *= upgrade["value"]

    return multiplier


def get_minigame_multiplier(state: GameState) -> float:
    multiplier = 1.0

    for upgrade_id, amount_owned in state.upgrades_owned.items():
        upgrade = UPGRADES[upgrade_id]
        if upgrade["type"] == "mini_game_multiplier":
            for _ in range(amount_owned):
                multiplier *= upgrade["value"]

    return multiplier


# -----------------------------
# CPS calculation
# -----------------------------
def calculate_total_cps(state: GameState) -> float:
    total = 0.0

    for building_id, amount_owned in state.buildings_owned.items():
        if amount_owned <= 0:
            continue

        effective_base_cps = get_building_effective_base_cps(state, building_id)
        building_multiplier = get_building_multiplier(state, building_id)

        building_cps = amount_owned * effective_base_cps * building_multiplier
        total += building_cps

    total *= get_global_multiplier(state)
    return total

def refresh_cps(state: GameState):
    state.total_cps = calculate_total_cps(state)


# -----------------------------
# Number formatting
# -----------------------------
def format_chud_amount(val: float) -> str:
    """Formats large numbers into human-readable units."""
    units = [
        "thousand",
        "million",
        "billion",
        "trillion",
        "quadrillion",
        "quintillion",
        "sextillion",
        "Septillion",
        "Octillion",
        "Nonillion",
        "Decillion"
    ]

    if val < 1000:
        return f"{val:.1f}"

    k = 0
    temp = val / 1000.0

    while temp >= 1000 and k < len(units) - 1:
        temp /= 1000.0
        k += 1

    if temp >= 1000 and k == len(units) - 1:
        return f"{temp / 1000.0:.1f} sheesh"

    return f"{temp:.1f} {units[k]}"


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
# Cost scaling helpers
# -----------------------------
def get_current_growth_rate(item_data: dict, amount_owned: int) -> float:
    growth = item_data["cost_growth"]# 
    growth_steps = sorted(item_data.get("cost_growth_steps", []), key=lambda step: step["level"])

    for step in growth_steps:
        if amount_owned >= step["level"]:
            growth = step["growth"]
        else:
            break

    return growth


def get_scaled_cost(base_cost: int, item_data: dict, amount_owned: int) -> int:
    cost = float(base_cost)

    for owned_count in range(amount_owned):
        cost *= get_current_growth_rate(item_data, owned_count)

    return math.ceil(cost)


# -----------------------------
# Buying buildings
# -----------------------------
def get_building_cost(building_id: str, amount_owned: int) -> int:
    building = BUILDINGS[building_id]
    return get_scaled_cost(building["base_cost"], building, amount_owned)


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
def get_upgrade_cost(upgrade_id: str, amount_owned: int) -> int:
    upgrade = UPGRADES[upgrade_id]
    return get_scaled_cost(upgrade["base_cost"], upgrade, amount_owned)


def buy_upgrade(state: GameState, upgrade_id: str) -> bool:
    if not is_upgrade_unlocked(state, upgrade_id):
        return False

    amount_owned = state.upgrades_owned[upgrade_id]
    cost = get_upgrade_cost(upgrade_id, amount_owned)

    if state.chuds >= cost:
        state.chuds -= cost
        state.upgrades_owned[upgrade_id] += 1
        refresh_cps(state)
        return True

    return False


# -----------------------------
# Coin Bet Logic
# -----------------------------
COIN_OPTIONS = [1, 3, 5, 7]
COST_MULTIPLIERS = {1: 0.05, 3: 0.15, 5: 0.25, 7: 0.45}


def process_coin_bet(state: GameState, num_coins: int, bet_side: str, bet_range: str) -> str:
    """Processes the coin flip and updates state.chuds. Returns a result string."""
    cost = max(1, int(state.chuds * COST_MULTIPLIERS.get(num_coins, 0.05)))

    if state.chuds < cost or state.chuds <= 0:
        return "Not enough CHUDs!"

    results = [random.choice(["Heads", "Tails"]) for _ in range(num_coins)]
    side_count = results.count(bet_side)

    half = num_coins / 2
    is_win = False

    if bet_range == "Over" and side_count > half:
        is_win = True
    elif bet_range == "Under" and side_count <= half:
        is_win = True

    mini_game_multiplier = get_minigame_multiplier(state)

    if is_win:
        reward = int(cost * (1.5 + (num_coins * 0.2)) * mini_game_multiplier)
        state.chuds += reward
        return f"WIN! +{reward} ({side_count} {bet_side})"
    else:
        state.chuds -= cost
        return f"LOST! -{cost} ({side_count} {bet_side})"


# -----------------------------
# Speed Clicker Logic
# -----------------------------
SPEED_CLICK_COOLDOWN = 90  # seconds
SPEED_CLICK_REWARD = 30
SPEED_CLICK_ENTRY_PERCENT = 0.35


def get_speed_click_cost(state: GameState) -> int:
    """Calculates entry cost based on 35% of current CHUDs."""
    return int(state.chuds * SPEED_CLICK_ENTRY_PERCENT)


def process_speed_click_hit(state: GameState):
    """Adds points for a successful hit."""
    reward = max(10, int(state.total_cps * 5 * get_minigame_multiplier(state)))
    state.chuds += reward


def start_speed_click_session(state: GameState) -> bool:
    """Deducts the entry cost if affordable."""
    cost = get_speed_click_cost(state)
    if state.chuds >= cost and state.chuds > 0:
        state.chuds -= cost
        return True
    return False
# -----------------------------
# Minigame Unlock Gates
# -----------------------------
def can_play_minigame(state: GameState, minigame_type: str) -> bool:
    """
    Returns True to allow immediate access to minigames.
    You can also change this to 'return sum(state.buildings_owned.values()) > 0'
    if you want them to buy at least one building first.
    """
    return True

def clear_minigame_gates(state: GameState, minigame_type: str):
    """
    Required by menus.py to prevent NameError. 
    Logic removed as requested.
    """
    pass