#!/usr/bin/env python3
"""
Comprehensive test suite for creature ability system.
Tests all ability types and their effects in battles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Move, Team, Ability
from genemon.battle.engine import Battle, Weather
from genemon.creatures.types import TYPES


def create_test_creature(name: str, types: list, ability: Ability, level: int = 20, stats: dict = None) -> Creature:
    """Create a test creature with specific ability."""
    if stats is None:
        stats = {"hp": 60, "attack": 60, "defense": 60, "special": 60, "speed": 60}

    base_stats = CreatureStats(**stats)

    # Create a test move
    test_move = Move(
        name="Test Attack",
        type=types[0] if types else "Beast",
        power=50,
        accuracy=100,
        pp=20,
        max_pp=20,
        description="A test attack"
    )

    species = CreatureSpecies(
        id=1,
        name=name,
        types=types,
        base_stats=base_stats,
        moves=[test_move],
        ability=ability,
        flavor_text=f"A test creature with {ability.name}"
    )

    return Creature(species=species, level=level)


def test_weather_summoning_abilities():
    """Test abilities that summon weather on entry."""
    print("\nTesting weather-summoning abilities...")

    # Test Drought (summons sun)
    drought = Ability("Drought", "Summons sunny weather", "weather_sun")
    drought_creature = create_test_creature("Sunny", ["Flame"], drought)
    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"))

    player_team = Team()
    player_team.add_creature(drought_creature)

    opponent_team = Team()
    opponent_team.add_creature(normal_creature)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Check that weather was set to SUN
    if battle.weather == Weather.SUN:
        print("  ✓ Drought ability summoned sunny weather")
    else:
        print(f"  ✗ Drought failed: weather is {battle.weather}")
        return False

    # Test Drizzle (summons rain)
    drizzle = Ability("Drizzle", "Summons rain", "weather_rain")
    drizzle_creature = create_test_creature("Rainy", ["Aqua"], drizzle)

    player_team2 = Team()
    player_team2.add_creature(drizzle_creature)

    battle2 = Battle(player_team2, opponent_team, is_wild=True)

    if battle2.weather == Weather.RAIN:
        print("  ✓ Drizzle ability summoned rain")
    else:
        print(f"  ✗ Drizzle failed: weather is {battle2.weather}")
        return False

    # Test Sand Stream (summons sandstorm)
    sand_stream = Ability("Sand Stream", "Summons sandstorm", "weather_sandstorm")
    sand_creature = create_test_creature("Sandy", ["Terra"], sand_stream)

    player_team3 = Team()
    player_team3.add_creature(sand_creature)

    battle3 = Battle(player_team3, opponent_team, is_wild=True)

    if battle3.weather == Weather.SANDSTORM:
        print("  ✓ Sand Stream ability summoned sandstorm")
    else:
        print(f"  ✗ Sand Stream failed: weather is {battle3.weather}")
        return False

    return True


def test_intimidate_ability():
    """Test Intimidate ability lowers opponent's Attack."""
    print("\nTesting Intimidate ability...")

    intimidate = Ability("Intimidate", "Lowers opposing Attack", "lower_attack_entry")
    intimidate_creature = create_test_creature("Scary", ["Beast"], intimidate, stats={
        "hp": 60, "attack": 70, "defense": 60, "special": 60, "speed": 60
    })

    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"))

    player_team = Team()
    player_team.add_creature(intimidate_creature)

    opponent_team = Team()
    opponent_team.add_creature(normal_creature)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Check that opponent's attack stat modifier was lowered
    if battle.opponent_stat_mods["attack"] < 1.0:
        print(f"  ✓ Intimidate lowered opponent's Attack (modifier: {battle.opponent_stat_mods['attack']})")
        return True
    else:
        print(f"  ✗ Intimidate failed: opponent Attack modifier is {battle.opponent_stat_mods['attack']}")
        return False


def test_huge_power_ability():
    """Test Huge Power ability doubles Attack stat."""
    print("\nTesting Huge Power ability...")

    huge_power = Ability("Huge Power", "Doubles Attack", "double_attack")
    huge_power_creature = create_test_creature("Strong", ["Brawl"], huge_power, stats={
        "hp": 60, "attack": 50, "defense": 60, "special": 60, "speed": 60
    })

    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"))

    player_team = Team()
    player_team.add_creature(huge_power_creature)

    opponent_team = Team()
    opponent_team.add_creature(normal_creature)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Get attack modifier (should be 2.0)
    modifier = battle._get_ability_stat_modifier(huge_power_creature, True, "attack")

    if modifier == 2.0:
        print(f"  ✓ Huge Power doubles Attack (modifier: {modifier})")
        return True
    else:
        print(f"  ✗ Huge Power failed: modifier is {modifier}")
        return False


def test_weather_speed_abilities():
    """Test weather-dependent speed abilities (Swift Swim, Chlorophyll, etc.)."""
    print("\nTesting weather-dependent speed abilities...")

    # Test Swift Swim in rain
    swift_swim = Ability("Swift Swim", "Doubles Speed in rain", "speed_rain")
    swift_creature = create_test_creature("Fast", ["Aqua"], swift_swim, stats={
        "hp": 60, "attack": 60, "defense": 60, "special": 60, "speed": 50
    })

    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"))

    player_team = Team()
    player_team.add_creature(swift_creature)

    opponent_team = Team()
    opponent_team.add_creature(normal_creature)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Set weather to rain
    battle.set_weather(Weather.RAIN)

    # Get speed modifier (should be 2.0 in rain)
    modifier = battle._get_ability_stat_modifier(swift_creature, True, "speed")

    if modifier == 2.0:
        print(f"  ✓ Swift Swim doubles Speed in rain (modifier: {modifier})")
    else:
        print(f"  ✗ Swift Swim failed: modifier is {modifier}")
        return False

    # Test Chlorophyll in sun
    chlorophyll = Ability("Chlorophyll", "Doubles Speed in sun", "speed_sun")
    chloro_creature = create_test_creature("Leafy", ["Leaf"], chlorophyll, stats={
        "hp": 60, "attack": 60, "defense": 60, "special": 60, "speed": 50
    })

    player_team2 = Team()
    player_team2.add_creature(chloro_creature)

    battle2 = Battle(player_team2, opponent_team, is_wild=True)
    battle2.set_weather(Weather.SUN)

    modifier2 = battle2._get_ability_stat_modifier(chloro_creature, True, "speed")

    if modifier2 == 2.0:
        print(f"  ✓ Chlorophyll doubles Speed in sun (modifier: {modifier2})")
        return True
    else:
        print(f"  ✗ Chlorophyll failed: modifier is {modifier2}")
        return False


def test_thick_fat_ability():
    """Test Thick Fat ability reduces Flame and Frost damage."""
    print("\nTesting Thick Fat ability...")

    thick_fat = Ability("Thick Fat", "Reduces Flame/Frost damage", "resist_flame_frost")
    thick_fat_creature = create_test_creature("Chubby", ["Beast"], thick_fat, level=20, stats={
        "hp": 80, "attack": 50, "defense": 70, "special": 50, "speed": 40
    })

    # Create attacker with Flame move
    flame_move = Move("Flame Attack", "Flame", 50, 100, 20, 20, "Fire attack")
    attacker_species = CreatureSpecies(
        id=2, name="Flamer", types=["Flame"],
        base_stats=CreatureStats(60, 70, 60, 60, 60),
        moves=[flame_move],
        ability=Ability("None", "No effect", "none"),
        flavor_text="Flame attacker"
    )
    attacker = Creature(species=attacker_species, level=20)

    player_team = Team()
    player_team.add_creature(thick_fat_creature)

    opponent_team = Team()
    opponent_team.add_creature(attacker)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Calculate damage with Thick Fat
    damage = battle._calculate_damage(attacker, thick_fat_creature, flame_move)

    # Calculate damage without Thick Fat
    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"),
                                          level=20, stats={"hp": 80, "attack": 50, "defense": 70, "special": 50, "speed": 40})

    player_team2 = Team()
    player_team2.add_creature(normal_creature)

    battle2 = Battle(player_team2, opponent_team, is_wild=True)
    normal_damage = battle2._calculate_damage(attacker, normal_creature, flame_move)

    if damage < normal_damage:
        print(f"  ✓ Thick Fat reduced damage ({damage} vs {normal_damage} normal)")
        return True
    else:
        print(f"  ✗ Thick Fat failed: damage {damage} vs {normal_damage} normal")
        return False


def test_adaptability_ability():
    """Test Adaptability ability boosts STAB effectiveness."""
    print("\nTesting Adaptability ability...")

    adaptability = Ability("Adaptability", "Boosts STAB effectiveness", "boost_stab")
    adapt_creature = create_test_creature("Adapter", ["Aqua"], adaptability, level=20, stats={
        "hp": 60, "attack": 70, "defense": 60, "special": 60, "speed": 60
    })

    # Create Aqua-type move
    aqua_move = Move("Aqua Attack", "Aqua", 50, 100, 20, 20, "Water attack")
    adapt_creature.species.moves = [aqua_move]

    normal_creature = create_test_creature("Normal", ["Beast"],
                                          Ability("None", "No effect", "none"))

    player_team = Team()
    player_team.add_creature(adapt_creature)

    opponent_team = Team()
    opponent_team.add_creature(normal_creature)

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Calculate damage with Adaptability (should have 2.0x STAB instead of 1.5x)
    damage_with = battle._calculate_damage(adapt_creature, normal_creature, aqua_move)

    # Create creature without Adaptability for comparison
    normal_aqua = create_test_creature("NormalAqua", ["Aqua"],
                                       Ability("None", "No effect", "none"),
                                       level=20, stats={"hp": 60, "attack": 70, "defense": 60, "special": 60, "speed": 60})
    normal_aqua.species.moves = [aqua_move]

    player_team2 = Team()
    player_team2.add_creature(normal_aqua)

    battle2 = Battle(player_team2, opponent_team, is_wild=True)
    damage_without = battle2._calculate_damage(normal_aqua, normal_creature, aqua_move)

    if damage_with > damage_without:
        print(f"  ✓ Adaptability boosted STAB damage ({damage_with} vs {damage_without})")
        return True
    else:
        print(f"  ✗ Adaptability failed: damage {damage_with} vs {damage_without}")
        return False


def main():
    """Run all ability tests."""
    print("=" * 60)
    print("GENEMON ABILITY SYSTEM TEST SUITE")
    print("=" * 60)

    tests = [
        test_weather_summoning_abilities,
        test_intimidate_ability,
        test_huge_power_ability,
        test_weather_speed_abilities,
        test_thick_fat_ability,
        test_adaptability_ability,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
