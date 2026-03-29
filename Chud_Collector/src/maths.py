from dataclasses import dataclass, field
import random
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
# -----------------------------
# Coin Bet Logic
# -----------------------------
COIN_OPTIONS = [1, 3, 5, 7]
COST_MULTIPLIERS = {1: 0.05, 3: 0.15, 5: 0.25, 7: 0.45}

# -----------------------------
# Coin Bet Logic
# -----------------------------
COIN_OPTIONS = [1, 3, 5, 7]
COST_MULTIPLIERS = {1: 0.05, 3: 0.15, 5: 0.25, 7: 0.45}

def process_coin_bet(state: GameState, num_coins: int, bet_side: str, bet_range: str) -> str:
    """Processes the coin flip and updates state.chuds. Returns a result string."""
    # Ensure cost is at least 1 if the player has points
    cost = max(1, int(state.chuds * COST_MULTIPLIERS.get(num_coins, 0.05)))
    
    if state.chuds < cost or state.chuds <= 0:
        return "Not enough CHUDs!"

    # Perform Flip
    results = [random.choice(["Heads", "Tails"]) for _ in range(num_coins)]
    side_count = results.count(bet_side)
    
    half = num_coins / 2
    is_win = False
    if bet_range == "Over" and side_count > half:
        is_win = True
    elif bet_range == "Under" and side_count <= half:
        is_win = True
        
    if is_win:
        # Exponential reward
        reward = int(cost * (math.pow(1.6, num_coins)))
        state.chuds += reward
        return f"WIN! +{reward} ({side_count} {bet_side})"
    else:
        state.chuds -= cost
        return f"LOST! -{cost} ({side_count} {bet_side})"
# -----------------------------
# Speed Clicker Logic
# -----------------------------
SPEED_CLICK_COOLDOWN = 10  # seconds
SPEED_CLICK_REWARD = 500   # CHUDs per hit
SPEED_CLICK_ENTRY_PERCENT = 0.35

def get_speed_click_cost(state: GameState) -> int:
    """Calculates entry cost based on 35% of current CHUDs."""
    return int(state.chuds * SPEED_CLICK_ENTRY_PERCENT)

def process_speed_click_hit(state: GameState):
    """Adds points for a successful hit."""
    state.chuds += SPEED_CLICK_REWARD

def start_speed_click_session(state: GameState) -> bool:
    """Deducts the entry cost if affordable."""
    cost = get_speed_click_cost(state)
    if state.chuds >= cost and state.chuds > 0:
        state.chuds -= cost
        return True
    return False