"""
Game constants and configuration values.

This module contains all magic numbers and constant values used throughout the game.
Centralizing these values makes them easier to maintain, tune, and understand.
"""

# ============================================================
# CREATURE GENERATION CONSTANTS
# ============================================================

# Total number of unique creatures per save file
TOTAL_CREATURES = 151

# Legendary creature ID range (last 6 creatures)
LEGENDARY_START_ID = 146
LEGENDARY_END_ID = 151

# Name generation
NAME_MIN_SYLLABLES = 2
NAME_MAX_SYLLABLES = 3
NAME_MAX_ATTEMPTS = 100

# Base stat ranges for different creature tiers
STAT_RANGE_NORMAL = {
    'hp': (40, 80),
    'attack': (35, 75),
    'defense': (30, 70),
    'special': (30, 70),
    'speed': (30, 70)
}

STAT_RANGE_LEGENDARY = {
    'hp': (80, 120),
    'attack': (70, 110),
    'defense': (65, 105),
    'special': (70, 110),
    'speed': (70, 110)
}

# HP stat variation
HP_VARIATION_MIN = -5
HP_VARIATION_MAX = 15

# Move learning
MOVES_PER_CREATURE_MIN = 4
MOVES_PER_CREATURE_MAX = 6

# ============================================================
# BATTLE CONSTANTS
# ============================================================

# Critical hit system
CRIT_MULTIPLIER_NORMAL = 2.0  # Normal critical hit damage multiplier
CRIT_MULTIPLIER_SNIPER = 3.0  # Sniper ability critical hit multiplier
CRIT_BASE_CHANCE = 6.25  # Base crit chance in percentage (1/16)
CRIT_HIGH_CHANCE = 12.5  # High crit moves chance in percentage (1/8)
CRIT_STAGE_THRESHOLD = 2  # Crit stage required for guaranteed crits

# Accuracy
ACCURACY_MIN = 1
ACCURACY_MAX = 100

# Multi-hit moves
MULTI_HIT_MIN = 2
MULTI_HIT_MAX = 5
MULTI_HIT_SKILL_LINK = 5  # Always hits 5 times with Skill Link ability

# STAB (Same Type Attack Bonus)
STAB_MULTIPLIER = 1.5

# Weather damage multipliers
WEATHER_DAMAGE_MULTIPLIER = 1.5
WEATHER_DAMAGE_REDUCTION = 0.5

# ============================================================
# HELD ITEM CONSTANTS
# ============================================================

# Type-boosting items (e.g., Charcoal, Mystic Water)
TYPE_BOOST_MULTIPLIER = 1.2

# Power items
LIFE_ORB_MULTIPLIER = 1.3
LIFE_ORB_RECOIL = 0.10  # 10% of max HP as recoil

CHOICE_ITEM_MULTIPLIER = 1.5  # Choice Band/Specs/Scarf

MUSCLE_BAND_MULTIPLIER = 1.1
WISE_GLASSES_MULTIPLIER = 1.1

EXPERT_BELT_MULTIPLIER = 1.2  # For super-effective moves

# Recovery items
LEFTOVERS_HEAL = 0.0625  # 1/16 of max HP per turn
SHELL_BELL_HEAL = 0.125  # 1/8 of damage dealt

BLACK_SLUDGE_HEAL = 0.0625  # 1/16 for Poison types
BLACK_SLUDGE_DAMAGE = 0.125  # 1/8 for non-Poison types

# Critical hit items
SCOPE_LENS_CRIT_BOOST = 1
RAZOR_CLAW_CRIT_BOOST = 1

# Contact damage
ROCKY_HELMET_DAMAGE = 0.166  # 1/6 of attacker's max HP (16.6%)

# Survival items
FOCUS_BAND_CHANCE = 0.10  # 10% chance to survive with 1 HP
FOCUS_SASH_GUARANTEED = True  # Always works at full HP, one-time use

# Priority items
QUICK_CLAW_CHANCE = 0.20  # 20% chance to move first

# Speed items
CHOICE_SCARF_SPEED_MULT = 1.5
IRON_BALL_SPEED_MULT = 0.5

# ============================================================
# STATUS EFFECT CONSTANTS
# ============================================================

# Burn
BURN_ATTACK_REDUCTION = 0.5  # 50% attack reduction
BURN_DAMAGE_PER_TURN = 0.0625  # 1/16 of max HP per turn

# Poison
POISON_DAMAGE_PER_TURN = 0.125  # 1/8 of max HP per turn

# Paralysis
PARALYSIS_SPEED_REDUCTION = 0.25  # Speed reduced to 25% of original
PARALYSIS_IMMOBILIZE_CHANCE = 0.25  # 25% chance to not move

# Sleep
SLEEP_MIN_TURNS = 1
SLEEP_MAX_TURNS = 3
SLEEP_WAKE_TURN = 3  # Wake up after 3 turns

# Freeze
FREEZE_THAW_CHANCE = 0.20  # 20% chance to thaw each turn

# ============================================================
# ABILITY CONSTANTS
# ============================================================

# Ability multipliers
GUTS_ATTACK_MULTIPLIER = 1.5  # 1.5x attack when statused
MARVEL_SCALE_DEFENSE_MULTIPLIER = 1.5  # 1.5x defense when statused
HUSTLE_ATTACK_MULTIPLIER = 1.5  # 1.5x attack but 0.8x accuracy
HUSTLE_ACCURACY_MULTIPLIER = 0.8

# Weather abilities
WEATHER_TURNS_NORMAL = 5  # Weather lasts 5 turns normally
WEATHER_TURNS_EXTENDED = 8  # Weather lasts 8 turns with weather rock

# Speed abilities
SWIFT_SWIM_SPEED_MULT = 2.0  # 2x speed in rain
CHLOROPHYLL_SPEED_MULT = 2.0  # 2x speed in sun
SAND_RUSH_SPEED_MULT = 2.0  # 2x speed in sandstorm
SLUSH_RUSH_SPEED_MULT = 2.0  # 2x speed in hail

# Damage immunity
LEVITATE_GROUND_IMMUNE = True
WONDER_GUARD_RESIST_ONLY = True

# ============================================================
# EXPERIENCE AND LEVELING
# ============================================================

# Level cap
MAX_LEVEL = 100
MIN_LEVEL = 1

# Experience formula: (level + 1) ^ 3
EXP_FORMULA_EXPONENT = 3

# Experience gain multipliers
EXP_WILD_BASE = 50
EXP_TRAINER_MULTIPLIER = 1.5

# Evolution
EVOLUTION_MIN_LEVEL = 16  # Typical first evolution level
EVOLUTION_MAX_LEVEL = 36  # Typical second evolution level

# ============================================================
# TEAM AND PARTY CONSTANTS
# ============================================================

# Team size
TEAM_MAX_SIZE = 6

# Moves per creature
CREATURE_MAX_MOVES = 4

# ============================================================
# STAT STAGE CONSTANTS
# ============================================================

# Stat stage limits
STAT_STAGE_MIN = -6
STAT_STAGE_MAX = 6

# Stat stage multipliers (for each stage level)
STAT_STAGE_MULTIPLIERS = {
    -6: 0.25,  # -6 stages = 25% (1/4)
    -5: 0.28,  # -5 stages = 28% (2/7)
    -4: 0.33,  # -4 stages = 33% (1/3)
    -3: 0.40,  # -3 stages = 40% (2/5)
    -2: 0.50,  # -2 stages = 50% (1/2)
    -1: 0.66,  # -1 stage  = 66% (2/3)
    0:  1.00,  # 0 stages  = 100%
    1:  1.50,  # +1 stage  = 150%
    2:  2.00,  # +2 stages = 200%
    3:  2.50,  # +3 stages = 250%
    4:  3.00,  # +4 stages = 300%
    5:  3.50,  # +5 stages = 350%
    6:  4.00,  # +6 stages = 400%
}

# ============================================================
# ITEM CONSTANTS
# ============================================================

# Healing items
POTION_HEAL_AMOUNT = 20
SUPER_POTION_HEAL_AMOUNT = 50
HYPER_POTION_HEAL_AMOUNT = 120
MAX_POTION_HEAL_FULL = True  # Heals to full HP

# PP restoration
ETHER_PP_RESTORE = 10
MAX_ETHER_PP_RESTORE_FULL = True  # Restores to full PP

# Capture balls
POKEBALL_CATCH_RATE = 1.0
GREATBALL_CATCH_RATE = 1.5
ULTRABALL_CATCH_RATE = 2.0
MASTERBALL_CATCH_RATE = 255.0  # Always catches

# ============================================================
# MONEY AND ECONOMY
# ============================================================

# Starting money
STARTING_MONEY = 3000

# Trainer battle rewards
TRAINER_MONEY_BASE = 100
TRAINER_MONEY_PER_LEVEL = 20

# Gym leader rewards
GYM_LEADER_MONEY_MULTIPLIER = 3

# Shop price multipliers
SHOP_SELL_MULTIPLIER = 0.5  # Sell items for 50% of buy price

# ============================================================
# WORLD AND MAP CONSTANTS
# ============================================================

# Map grid size
MAP_DEFAULT_WIDTH = 10
MAP_DEFAULT_HEIGHT = 10

# Movement
PLAYER_STARTING_X = 5
PLAYER_STARTING_Y = 5

# Wild encounter rates
WILD_ENCOUNTER_RATE_GRASS = 0.15  # 15% per step in grass
WILD_ENCOUNTER_RATE_CAVE = 0.20  # 20% per step in caves
WILD_ENCOUNTER_RATE_WATER = 0.15  # 15% per step on water

# Trainer sight range
TRAINER_SIGHT_RANGE = 3  # Trainers can see 3 tiles ahead

# ============================================================
# UI CONSTANTS
# ============================================================

# Display
SCREEN_CLEAR_LINES = 50  # Number of newlines to "clear" screen

# Text formatting
HEADER_WIDTH = 60
MENU_INDENT = 2

# Animation delays (in seconds)
ANIMATION_DELAY_SHORT = 0.5
ANIMATION_DELAY_MEDIUM = 1.0
ANIMATION_DELAY_LONG = 2.0

# ============================================================
# SPRITE GENERATION CONSTANTS
# ============================================================

# Sprite dimensions
SPRITE_FRONT_SIZE = 56
SPRITE_BACK_SIZE = 56
SPRITE_MINI_SIZE = 16

# Sprite colors
SPRITE_MAX_COLORS = 8
SPRITE_MIN_COLORS = 3

# ============================================================
# SAVE SYSTEM CONSTANTS
# ============================================================

# Save file
SAVE_FILE_EXTENSION = ".json"
SAVE_FOLDER = "saves"

# Autosave
AUTOSAVE_ENABLED = False  # Manual save only by default
AUTOSAVE_INTERVAL_MINUTES = 5

# ============================================================
# GAME BALANCE CONSTANTS
# ============================================================

# Difficulty multipliers
TRAINER_LEVEL_VARIANCE = 2  # Random variance in trainer creature levels

# Gym leader team sizes
GYM_LEADER_TEAM_SIZE_MIN = 3
GYM_LEADER_TEAM_SIZE_MAX = 5

# Elite Four team size
ELITE_FOUR_TEAM_SIZE = 5

# Champion team size
CHAMPION_TEAM_SIZE = 6

# Wild creature level ranges by area
WILD_LEVEL_RANGE_EARLY = (2, 7)
WILD_LEVEL_RANGE_MID = (15, 25)
WILD_LEVEL_RANGE_LATE = (35, 45)
WILD_LEVEL_RANGE_POST_GAME = (50, 60)
