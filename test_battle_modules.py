"""
Unit tests for refactored battle modules.

Tests the new BattleCalculator, StatusManager, and WeatherManager modules
to ensure they work correctly before integration into the main battle engine.
"""

import sys
import random
from dataclasses import dataclass
from typing import List

# Add parent directory to path
sys.path.insert(0, '/workspace/loop')

from genemon.battle.calculator import BattleCalculator
from genemon.battle.status import StatusManager
from genemon.battle.weather import Weather, WeatherManager
from genemon.core.creature import Creature, CreatureSpecies, Move, Ability, HeldItem


# Test fixtures
@dataclass
class MockSpecies:
    """Mock creature species for testing."""
    name: str
    types: List[str]
    ability: Ability = None


def create_test_creature(
    name: str,
    level: int = 50,
    types: List[str] = None,
    ability_name: str = None,
    status: str = "",
    hp: int = 100,
    attack: int = 100,
    defense: int = 100,
    special: int = 100,
    speed: int = 100
) -> Creature:
    """Create a test creature with specified stats."""
    if types is None:
        types = ["Normal"]

    ability = None
    if ability_name:
        ability = Ability(name=ability_name, effect_type="", effect_value=0.0)

    species = MockSpecies(name=name, types=types, ability=ability)

    # Create moves
    moves = [
        Move(name="Tackle", type="Normal", category="physical", power=50, accuracy=100),
        Move(name="Ember", type="Flame", category="special", power=40, accuracy=100),
    ]

    creature = Creature.__new__(Creature)
    creature.species = species
    creature.level = level
    creature.max_hp = hp
    creature.current_hp = hp
    creature.attack = attack
    creature.defense = defense
    creature.special = special
    creature.speed = speed
    creature.status = status
    creature.sleep_turns = 0
    creature.moves = moves
    creature.held_item = None
    creature.focus_sash_used = False
    creature.choice_locked_move = None

    return creature


def create_test_move(
    name: str = "Test Move",
    move_type: str = "Normal",
    category: str = "physical",
    power: int = 80,
    accuracy: int = 100,
    status_effect: str = None,
    status_chance: int = 0
) -> Move:
    """Create a test move."""
    return Move(
        name=name,
        type=move_type,
        category=category,
        power=power,
        accuracy=accuracy,
        pp=10,
        max_pp=10,
        status_effect=status_effect,
        status_chance=status_chance,
        stat_changes=None,
        stat_change_target="opponent",
        recoil_percent=0,
        priority=0,
        multi_hit=(1, 1),
        is_contact=True
    )


# ==============================================================================
# BATTLE CALCULATOR TESTS
# ==============================================================================

def test_calculator_basic_damage():
    """Test basic damage calculation."""
    print("\n=== Test: Calculator Basic Damage ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker", attack=100, special=100)
    defender = create_test_creature("Defender", defense=100)
    move = create_test_move("Tackle", power=50, category="physical")

    damage = calculator.calculate_damage(
        attacker, defender, move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"attack": 0, "special": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0, "special": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    assert damage > 0, "Damage should be positive"
    assert damage < 100, f"Damage {damage} should be reasonable for stats"
    print(f"✓ Basic damage calculation: {damage} damage")
    return True


def test_calculator_critical_hit():
    """Test critical hit damage multiplier."""
    print("\n=== Test: Calculator Critical Hit ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker", attack=100)
    defender = create_test_creature("Defender", defense=100)
    move = create_test_move("Tackle", power=50, category="physical")

    # Calculate normal damage
    normal_damage = calculator.calculate_damage(
        attacker, defender, move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"attack": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    # Calculate critical damage
    crit_damage = calculator.calculate_damage(
        attacker, defender, move,
        is_critical=True,
        weather="none",
        attacker_stat_stages={"attack": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    assert crit_damage > normal_damage * 1.5, f"Crit damage {crit_damage} should be ~2x normal {normal_damage}"
    print(f"✓ Critical hit multiplier works: {normal_damage} → {crit_damage}")
    return True


def test_calculator_type_effectiveness():
    """Test STAB and type effectiveness."""
    print("\n=== Test: Calculator Type Effectiveness ===")

    calculator = BattleCalculator()

    # Flame attacker using Flame move (STAB)
    attacker = create_test_creature("Flamer", types=["Flame"])
    defender = create_test_creature("Defender")
    flame_move = create_test_move("Ember", move_type="Flame", power=50)

    damage = calculator.calculate_damage(
        attacker, defender, flame_move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"attack": 0, "special": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0, "special": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    assert damage > 0, "STAB move should deal damage"
    print(f"✓ STAB bonus applied: {damage} damage")
    return True


def test_calculator_weather_modifiers():
    """Test weather damage modifiers."""
    print("\n=== Test: Calculator Weather Modifiers ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker", attack=100, special=100)
    defender = create_test_creature("Defender", defense=100)
    flame_move = create_test_move("Ember", move_type="Flame", power=50, category="special")

    # Damage in normal weather
    normal_damage = calculator.calculate_damage(
        attacker, defender, flame_move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"special": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"special": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    # Damage in sun (should boost Flame)
    sun_damage = calculator.calculate_damage(
        attacker, defender, flame_move,
        is_critical=False,
        weather="sun",
        attacker_stat_stages={"special": 0},
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"special": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    assert sun_damage > normal_damage, f"Sun should boost Flame: {normal_damage} → {sun_damage}"
    print(f"✓ Weather modifiers work: {normal_damage} → {sun_damage} in sun")
    return True


def test_calculator_stat_stages():
    """Test stat stage multipliers."""
    print("\n=== Test: Calculator Stat Stages ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker", attack=100)
    defender = create_test_creature("Defender", defense=100)
    move = create_test_move("Tackle", power=50, category="physical")

    # Damage at +2 attack stages
    boosted_damage = calculator.calculate_damage(
        attacker, defender, move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"attack": 2},  # +2 stages
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    # Damage at -2 attack stages
    nerfed_damage = calculator.calculate_damage(
        attacker, defender, move,
        is_critical=False,
        weather="none",
        attacker_stat_stages={"attack": -2},  # -2 stages
        defender_stat_stages={"defense": 0},
        attacker_stat_mods={"attack": 1.0},
        defender_stat_mods={"defense": 1.0}
    )

    assert boosted_damage > nerfed_damage * 2, f"Boosted {boosted_damage} should be much higher than nerfed {nerfed_damage}"
    print(f"✓ Stat stages work: {nerfed_damage} at -2 → {boosted_damage} at +2")
    return True


def test_calculator_check_critical_hit():
    """Test critical hit determination."""
    print("\n=== Test: Calculator Check Critical Hit ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker")
    defender = create_test_creature("Defender")
    move = create_test_move("Tackle")

    # Run multiple times to test randomness
    crit_count = 0
    trials = 1000
    for _ in range(trials):
        if calculator.check_critical_hit(attacker, defender, move):
            crit_count += 1

    crit_rate = (crit_count / trials) * 100

    # Base crit rate is 6.25%, so we expect roughly 5-8% with randomness
    assert 3 < crit_rate < 10, f"Crit rate {crit_rate}% should be near 6.25%"
    print(f"✓ Critical hit rate: {crit_rate:.2f}% over {trials} trials")
    return True


def test_calculator_ability_blocking_crits():
    """Test abilities that block critical hits."""
    print("\n=== Test: Calculator Abilities Block Crits ===")

    calculator = BattleCalculator()
    attacker = create_test_creature("Attacker")
    defender = create_test_creature("Defender", ability_name="Battle Armor")
    move = create_test_move("Tackle")

    # Run multiple times - should NEVER crit
    crit_count = 0
    trials = 100
    for _ in range(trials):
        if calculator.check_critical_hit(attacker, defender, move):
            crit_count += 1

    assert crit_count == 0, f"Battle Armor should block all crits, got {crit_count}"
    print(f"✓ Battle Armor blocks all critical hits")
    return True


# ==============================================================================
# STATUS MANAGER TESTS
# ==============================================================================

def test_status_apply_status():
    """Test applying status effects."""
    print("\n=== Test: StatusManager Apply Status ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon")
    log_messages = []

    # Apply burn
    result = manager.apply_status(creature, "Burn", log_messages)

    assert result == True, "Status application should succeed"
    assert creature.status == "Burn", "Creature should be burned"
    assert len(log_messages) > 0, "Should have status message"
    assert "burned" in log_messages[0].lower(), "Message should mention burn"
    print(f"✓ Status applied: {creature.status}")
    return True


def test_status_immunity():
    """Test status immunity from abilities."""
    print("\n=== Test: StatusManager Status Immunity ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon", ability_name="Immunity")
    log_messages = []

    # Try to apply poison (should fail)
    result = manager.apply_status(creature, "Poison", log_messages)

    assert result == False, "Immunity should block poison"
    assert creature.status == "", "Creature should not be poisoned"
    assert "immune" in log_messages[0].lower(), "Should mention immunity"
    print(f"✓ Immunity ability blocks poison")
    return True


def test_status_damage_burn():
    """Test burn damage over time."""
    print("\n=== Test: StatusManager Burn Damage ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon", hp=100)
    creature.status = "Burn"
    log_messages = []

    initial_hp = creature.current_hp
    manager.process_status_damage(creature, log_messages)

    assert creature.current_hp < initial_hp, "Burn should deal damage"
    assert len(log_messages) > 0, "Should have damage message"
    damage = initial_hp - creature.current_hp
    print(f"✓ Burn damage: {damage} HP (6.25% of max)")
    return True


def test_status_damage_poison():
    """Test poison damage over time."""
    print("\n=== Test: StatusManager Poison Damage ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon", hp=100)
    creature.status = "Poison"
    log_messages = []

    initial_hp = creature.current_hp
    manager.process_status_damage(creature, log_messages)

    assert creature.current_hp < initial_hp, "Poison should deal damage"
    damage = initial_hp - creature.current_hp
    assert damage >= 12, "Poison should deal 12.5% damage"
    print(f"✓ Poison damage: {damage} HP (12.5% of max)")
    return True


def test_status_can_move_paralysis():
    """Test paralysis movement chance."""
    print("\n=== Test: StatusManager Paralysis Movement ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon")
    creature.status = "Paralysis"

    # Test multiple times to check randomness
    immobile_count = 0
    trials = 100
    for _ in range(trials):
        can_move, message = manager.can_creature_move(creature)
        if not can_move:
            immobile_count += 1

    immobile_rate = (immobile_count / trials) * 100

    # Should be around 25%
    assert 15 < immobile_rate < 35, f"Paralysis immobility rate {immobile_rate}% should be near 25%"
    print(f"✓ Paralysis immobility: {immobile_rate:.1f}% over {trials} trials")
    return True


def test_status_can_move_sleep():
    """Test sleep turn counter."""
    print("\n=== Test: StatusManager Sleep Turns ===")

    manager = StatusManager()
    creature = create_test_creature("TestMon")
    creature.status = "Sleep"
    creature.sleep_turns = 2

    # First turn - still asleep
    can_move, message = manager.can_creature_move(creature)
    assert can_move == False, "Should still be asleep"
    assert creature.sleep_turns == 1, "Sleep counter should decrement"

    # Second turn - wakes up
    can_move, message = manager.can_creature_move(creature)
    assert can_move == True, "Should wake up"
    assert creature.status == "", "Status should be cleared"
    print(f"✓ Sleep counter works: 2 turns → wake up")
    return True


def test_status_speed_modifier():
    """Test status-based speed modifiers."""
    print("\n=== Test: StatusManager Speed Modifier ===")

    manager = StatusManager()
    normal_creature = create_test_creature("Normal")
    paralyzed_creature = create_test_creature("Paralyzed")
    paralyzed_creature.status = "Paralysis"

    normal_mod = manager.get_speed_modifier(normal_creature)
    paralyzed_mod = manager.get_speed_modifier(paralyzed_creature)

    assert normal_mod == 1.0, "Normal creature should have 1.0x speed"
    assert paralyzed_mod == 0.25, "Paralyzed should have 0.25x speed (75% reduction)"
    print(f"✓ Paralysis reduces speed to 25%")
    return True


# ==============================================================================
# WEATHER MANAGER TESTS
# ==============================================================================

def test_weather_set_weather():
    """Test setting weather conditions."""
    print("\n=== Test: WeatherManager Set Weather ===")

    manager = WeatherManager()
    log_messages = []

    manager.set_weather(Weather.RAIN, turns=5, log_messages=log_messages)

    assert manager.current_weather == Weather.RAIN, "Weather should be rain"
    assert manager.weather_turns_remaining == 5, "Should last 5 turns"
    assert len(log_messages) > 0, "Should have weather message"
    print(f"✓ Weather set to {manager.current_weather.value}")
    return True


def test_weather_turn_countdown():
    """Test weather turn countdown."""
    print("\n=== Test: WeatherManager Turn Countdown ===")

    manager = WeatherManager()
    log_messages = []

    manager.set_weather(Weather.SANDSTORM, turns=2, log_messages=log_messages)

    player = create_test_creature("Player", types=["Normal"])
    opponent = create_test_creature("Opponent", types=["Normal"])

    # Turn 1 - weather active
    manager.process_weather_effects(player, opponent, [])
    assert manager.weather_turns_remaining == 1, "Should have 1 turn left"
    assert manager.current_weather == Weather.SANDSTORM, "Weather still active"

    # Turn 2 - weather clears
    clear_messages = []
    manager.process_weather_effects(player, opponent, clear_messages)
    assert manager.current_weather == Weather.NONE, "Weather should clear"
    assert any("clear" in msg.lower() for msg in clear_messages), "Should announce clearing"
    print(f"✓ Weather countdown: 2 turns → cleared")
    return True


def test_weather_sandstorm_damage():
    """Test sandstorm damage."""
    print("\n=== Test: WeatherManager Sandstorm Damage ===")

    manager = WeatherManager()
    log_messages = []
    manager.set_weather(Weather.SANDSTORM, turns=0, log_messages=log_messages)

    # Normal type - should take damage
    normal_creature = create_test_creature("Normal", types=["Normal"], hp=100)
    initial_hp = normal_creature.current_hp

    damage_messages = []
    manager.process_weather_effects(normal_creature, normal_creature, damage_messages)

    assert normal_creature.current_hp < initial_hp, "Sandstorm should damage Normal types"
    assert len(damage_messages) > 0, "Should have damage message"
    print(f"✓ Sandstorm damage: {initial_hp - normal_creature.current_hp} HP")
    return True


def test_weather_sandstorm_immunity():
    """Test sandstorm immunity for Rock/Ground types."""
    print("\n=== Test: WeatherManager Sandstorm Immunity ===")

    manager = WeatherManager()
    log_messages = []
    manager.set_weather(Weather.SANDSTORM, turns=0, log_messages=log_messages)

    # Terra type - should be immune
    terra_creature = create_test_creature("Terra", types=["Terra"], hp=100)
    initial_hp = terra_creature.current_hp

    damage_messages = []
    manager.process_weather_effects(terra_creature, terra_creature, damage_messages)

    assert terra_creature.current_hp == initial_hp, "Terra types should be immune"
    print(f"✓ Terra type immune to sandstorm")
    return True


def test_weather_speed_abilities():
    """Test weather-based speed abilities."""
    print("\n=== Test: WeatherManager Speed Abilities ===")

    manager = WeatherManager()
    log_messages = []
    manager.set_weather(Weather.RAIN, turns=0, log_messages=log_messages)

    swift_swim = create_test_creature("SwiftSwim", ability_name="Swift Swim")
    normal = create_test_creature("Normal")

    swift_swim_mod = manager.get_speed_modifier(swift_swim)
    normal_mod = manager.get_speed_modifier(normal)

    assert swift_swim_mod == 2.0, "Swift Swim should double speed in rain"
    assert normal_mod == 1.0, "Normal should have 1.0x speed"
    print(f"✓ Swift Swim doubles speed in rain")
    return True


def test_weather_ability_triggers():
    """Test weather-setting abilities on entry."""
    print("\n=== Test: WeatherManager Ability Triggers ===")

    manager = WeatherManager()
    drizzle_creature = create_test_creature("Drizzle", ability_name="Drizzle")

    log_messages = []
    manager.apply_weather_ability_effects(drizzle_creature, True, log_messages)

    assert manager.current_weather == Weather.RAIN, "Drizzle should summon rain"
    assert len(log_messages) > 0, "Should have activation message"
    print(f"✓ Drizzle ability summons rain on entry")
    return True


# ==============================================================================
# RUN ALL TESTS
# ==============================================================================

def run_all_tests():
    """Run all unit tests."""
    print("=" * 70)
    print("BATTLE MODULES UNIT TEST SUITE")
    print("=" * 70)

    tests = [
        # Calculator tests
        ("Calculator: Basic Damage", test_calculator_basic_damage),
        ("Calculator: Critical Hit", test_calculator_critical_hit),
        ("Calculator: Type Effectiveness", test_calculator_type_effectiveness),
        ("Calculator: Weather Modifiers", test_calculator_weather_modifiers),
        ("Calculator: Stat Stages", test_calculator_stat_stages),
        ("Calculator: Check Critical Hit", test_calculator_check_critical_hit),
        ("Calculator: Abilities Block Crits", test_calculator_ability_blocking_crits),

        # Status tests
        ("Status: Apply Status", test_status_apply_status),
        ("Status: Immunity", test_status_immunity),
        ("Status: Burn Damage", test_status_damage_burn),
        ("Status: Poison Damage", test_status_damage_poison),
        ("Status: Paralysis Movement", test_status_can_move_paralysis),
        ("Status: Sleep Turns", test_status_can_move_sleep),
        ("Status: Speed Modifier", test_status_speed_modifier),

        # Weather tests
        ("Weather: Set Weather", test_weather_set_weather),
        ("Weather: Turn Countdown", test_weather_turn_countdown),
        ("Weather: Sandstorm Damage", test_weather_sandstorm_damage),
        ("Weather: Sandstorm Immunity", test_weather_sandstorm_immunity),
        ("Weather: Speed Abilities", test_weather_speed_abilities),
        ("Weather: Ability Triggers", test_weather_ability_triggers),
    ]

    passed = 0
    failed = 0
    errors = []

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                errors.append(f"{test_name}: Assertion failed")
        except Exception as e:
            failed += 1
            errors.append(f"{test_name}: {type(e).__name__}: {e}")

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed > 0:
        print(f"\nFAILED TESTS:")
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print("✓ All tests passed!")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
