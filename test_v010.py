#!/usr/bin/env python3
"""
Test suite for v0.10.0 features: Weather and Abilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.creatures.generator import CreatureGenerator
from genemon.sprites.generator import SpriteGenerator
from genemon.battle.engine import Battle, Weather
from genemon.core.creature import Team, Creature

def test_abilities():
    """Test that all creatures have abilities."""
    print("Testing creature abilities...")

    generator = CreatureGenerator(seed=12345)
    creatures = generator.generate_all_creatures()

    abilities_count = 0
    for species in creatures:
        if species.ability:
            abilities_count += 1

    print(f"  ✓ {abilities_count}/151 creatures have abilities")
    assert abilities_count == 151, "All creatures should have abilities!"

    # Show some example abilities
    print("\nExample abilities:")
    for i in [0, 1, 2, 50, 100, 145]:
        species = creatures[i]
        if species.ability:
            print(f"  • {species.name}: {species.ability.name} - {species.ability.description}")

    print("✓ Ability generation successful!\n")


def test_weather_system():
    """Test weather system in battles."""
    print("Testing weather system...")

    # Create test creatures
    generator = CreatureGenerator(seed=12345)
    creatures = generator.generate_all_creatures()

    # Get Flame and Aqua creatures for weather testing
    flame_species = None
    aqua_species = None

    for species in creatures:
        if "Flame" in species.types and not flame_species:
            flame_species = species
        if "Aqua" in species.types and not aqua_species:
            aqua_species = species
        if flame_species and aqua_species:
            break

    # Create test teams
    flame_creature = Creature(species=flame_species, level=50)
    aqua_creature = Creature(species=aqua_species, level=50)

    player_team = Team()
    player_team.add_creature(flame_creature)

    opponent_team = Team()
    opponent_team.add_creature(aqua_creature)

    # Test battle with weather
    battle = Battle(player_team, opponent_team, is_wild=False, can_run=False)

    # Test weather setting
    print("  ✓ Battle created")

    # Test rain
    battle.set_weather(Weather.RAIN, turns=5)
    assert battle.weather == Weather.RAIN, "Weather should be RAIN"
    print("  ✓ Rain weather set")

    # Test sun
    battle.set_weather(Weather.SUN, turns=5)
    assert battle.weather == Weather.SUN, "Weather should be SUN"
    print("  ✓ Sunny weather set")

    # Test sandstorm
    battle.set_weather(Weather.SANDSTORM, turns=5)
    assert battle.weather == Weather.SANDSTORM, "Weather should be SANDSTORM"
    print("  ✓ Sandstorm weather set")

    # Test hail
    battle.set_weather(Weather.HAIL, turns=5)
    assert battle.weather == Weather.HAIL, "Weather should be HAIL"
    print("  ✓ Hail weather set")

    print("✓ Weather system successful!\n")


def test_weather_moves():
    """Test weather-changing moves exist in TM pool."""
    print("Testing weather moves...")

    from genemon.core.items import TM_MOVES

    weather_moves = ["Rain Dance", "Sunny Day", "Sandstorm", "Hail"]

    for move_name in weather_moves:
        assert move_name in TM_MOVES, f"{move_name} should be in TM moves"
        move = TM_MOVES[move_name]
        print(f"  ✓ {move_name} ({move.type}-type) available as TM")

    print("✓ Weather moves successful!\n")


def test_tm_count():
    """Test that we now have 55 TMs (51 + 4 weather)."""
    print("Testing TM count...")

    from genemon.core.items import ITEMS

    tm_count = sum(1 for item_id in ITEMS if item_id.startswith('tm'))
    print(f"  ✓ Total TMs: {tm_count}")
    assert tm_count == 55, f"Expected 55 TMs, got {tm_count}"

    print("✓ TM count successful!\n")


def main():
    """Run all v0.10.0 tests."""
    print("=" * 60)
    print("GENEMON v0.10.0 TEST SUITE")
    print("=" * 60)
    print()

    try:
        test_abilities()
        test_weather_system()
        test_weather_moves()
        test_tm_count()

        print("=" * 60)
        print("ALL v0.10.0 TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
