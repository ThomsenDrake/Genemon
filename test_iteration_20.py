#!/usr/bin/env python
"""
Test suite for Iteration 20 - Bug Fixes & Optimizations
Tests for critical bug fixes and performance improvements
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Move, Team, StatusEffect, Ability
from genemon.battle.engine import Battle, BattleAction
from genemon.core.held_items import get_held_items_catalog, get_held_item_by_name, create_held_items_catalog
from genemon.creatures.generator import CreatureGenerator

def test_battle_init_validation():
    """Test that battle initialization validates teams have active creatures."""
    print("\n=== Test: Battle Initialization Validation ===\n")

    # Create a basic move
    tackle = Move(
        name="Tackle", type="Beast", power=40, accuracy=100,
        pp=35, max_pp=35, description="A physical attack"
    )

    # Create species and creature
    species = CreatureSpecies(
        id=1,
        name="TestMon",
        types=["Beast"],
        base_stats=CreatureStats(50, 50, 50, 50, 50),
        moves=[tackle],
        flavor_text="A test creature"
    )

    creature = Creature(species=species, level=5, current_hp=0)

    # Test 1: Valid teams
    print("1. Testing battle with valid teams...")
    team1 = Team()
    team2 = Team()
    team1.add_creature(creature)

    # Create a second creature for team2
    creature2 = Creature(species=species, level=5, current_hp=0)
    team2.add_creature(creature2)

    try:
        battle = Battle(team1, team2)
        print("✓ Battle initialized successfully with valid teams")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Test 2: Empty player team
    print("\n2. Testing battle with empty player team...")
    empty_team = Team()
    try:
        battle = Battle(empty_team, team2)
        print("✗ Should have raised ValueError for empty player team")
        return False
    except ValueError as e:
        if "Player team has no active creatures" in str(e):
            print(f"✓ Correctly raised error: {e}")
        else:
            print(f"✗ Wrong error message: {e}")
            return False

    # Test 3: Empty opponent team
    print("\n3. Testing battle with empty opponent team...")
    try:
        battle = Battle(team1, empty_team)
        print("✗ Should have raised ValueError for empty opponent team")
        return False
    except ValueError as e:
        if "Opponent team has no active creatures" in str(e):
            print(f"✓ Correctly raised error: {e}")
        else:
            print(f"✗ Wrong error message: {e}")
            return False

    # Test 4: Team with only fainted creatures
    print("\n4. Testing battle with all fainted creatures...")
    fainted_team = Team()
    fainted_creature = Creature(species=species, level=5, current_hp=0)
    fainted_creature.take_damage(fainted_creature.max_hp)  # Faint it
    fainted_team.add_creature(fainted_creature)

    try:
        battle = Battle(fainted_team, team2)
        print("✗ Should have raised ValueError for team with only fainted creatures")
        return False
    except ValueError as e:
        if "Player team has no active creatures" in str(e):
            print(f"✓ Correctly raised error: {e}")
        else:
            print(f"✗ Wrong error message: {e}")
            return False

    print("\n✅ Battle Initialization Validation: ALL TESTS PASSED")
    return True


def test_held_items_catalog_caching():
    """Test that held items catalog is properly cached."""
    print("\n=== Test: Held Items Catalog Caching ===\n")

    print("1. Testing catalog caching...")

    # Get catalog twice
    catalog1 = get_held_items_catalog()
    catalog2 = get_held_items_catalog()

    # They should be the same object (cached)
    if catalog1 is catalog2:
        print("✓ Catalog is properly cached (same object returned)")
    else:
        print("✗ Catalog is not cached (different objects returned)")
        return False

    print("\n2. Testing catalog contents...")
    if len(catalog1) > 30:  # Should have 35+ items
        print(f"✓ Catalog has {len(catalog1)} items")
    else:
        print(f"✗ Catalog only has {len(catalog1)} items (expected 30+)")
        return False

    print("\n3. Testing get_held_item_by_name...")
    life_orb = get_held_item_by_name("Life Orb")
    if life_orb and life_orb.name == "Life Orb":
        print("✓ get_held_item_by_name works correctly")
    else:
        print("✗ get_held_item_by_name failed")
        return False

    print("\n4. Testing multiple calls don't recreate catalog...")
    # Call create_held_items_catalog directly to ensure it creates new dict
    new_catalog = create_held_items_catalog()
    cached_catalog = get_held_items_catalog()

    # new_catalog should be different object, cached should be same
    if new_catalog is not cached_catalog:
        print("✓ create_held_items_catalog creates new dict")
    else:
        print("✗ create_held_items_catalog returned cached version")

    if cached_catalog is catalog1:
        print("✓ get_held_items_catalog still returns cached version")
    else:
        print("✗ Cache was invalidated unexpectedly")
        return False

    print("\n✅ Held Items Catalog Caching: ALL TESTS PASSED")
    return True


def test_focus_sash_reset():
    """Test that Focus Sash resets between battles."""
    print("\n=== Test: Focus Sash Reset Between Battles ===\n")

    # Create test creatures
    tackle = Move(
        name="Tackle", type="Beast", power=40, accuracy=100,
        pp=35, max_pp=35, description="A physical attack"
    )

    species = CreatureSpecies(
        id=1,
        name="TestMon",
        types=["Beast"],
        base_stats=CreatureStats(50, 50, 50, 50, 50),
        moves=[tackle],
        flavor_text="A test creature"
    )

    creature1 = Creature(species=species, level=5, current_hp=0)
    creature2 = Creature(species=species, level=5, current_hp=0)

    # Mark Focus Sash as used
    creature1.focus_sash_used = True
    creature2.focus_sash_used = True

    print("1. Testing Focus Sash reset on battle start...")
    team1 = Team()
    team2 = Team()
    team1.add_creature(creature1)
    team2.add_creature(creature2)

    # Create battle (should reset focus_sash_used)
    battle = Battle(team1, team2)

    if not creature1.focus_sash_used and not creature2.focus_sash_used:
        print("✓ Focus Sash reset to False for both creatures")
    else:
        print(f"✗ Focus Sash not reset: creature1={creature1.focus_sash_used}, creature2={creature2.focus_sash_used}")
        return False

    print("\n2. Testing Choice item lock reset...")
    creature1.choice_locked_move = "TestMove"
    creature2.choice_locked_move = "OtherMove"

    # Create new battle
    creature3 = Creature(species=species, level=5, current_hp=0)
    creature4 = Creature(species=species, level=5, current_hp=0)
    team3 = Team()
    team4 = Team()
    team3.add_creature(creature3)
    team4.add_creature(creature4)

    # Set choice locks
    creature3.choice_locked_move = "Move1"
    creature4.choice_locked_move = "Move2"

    battle2 = Battle(team3, team4)

    if creature3.choice_locked_move is None and creature4.choice_locked_move is None:
        print("✓ Choice item lock reset to None for both creatures")
    else:
        print(f"✗ Choice lock not reset: creature3={creature3.choice_locked_move}, creature4={creature4.choice_locked_move}")
        return False

    print("\n✅ Focus Sash Reset: ALL TESTS PASSED")
    return True


def test_creature_move_validation():
    """Test that creatures validate they have moves."""
    print("\n=== Test: Creature Move Validation ===\n")

    print("1. Testing creature with no moves raises error...")

    # Create species with empty moves list
    species_no_moves = CreatureSpecies(
        id=1,
        name="NoMovesMon",
        types=["Beast"],
        base_stats=CreatureStats(50, 50, 50, 50, 50),
        moves=[],  # Empty moves!
        flavor_text="A broken creature"
    )

    try:
        creature = Creature(species=species_no_moves, level=5, current_hp=0)
        print("✗ Should have raised ValueError for creature with no moves")
        return False
    except ValueError as e:
        if "has no moves" in str(e):
            print(f"✓ Correctly raised error: {e}")
        else:
            print(f"✗ Wrong error message: {e}")
            return False

    print("\n2. Testing creature with moves works fine...")
    tackle = Move(
        name="Tackle", type="Beast", power=40, accuracy=100,
        pp=35, max_pp=35, description="A physical attack"
    )

    species_with_moves = CreatureSpecies(
        id=2,
        name="GoodMon",
        types=["Beast"],
        base_stats=CreatureStats(50, 50, 50, 50, 50),
        moves=[tackle],
        flavor_text="A good creature"
    )

    try:
        creature = Creature(species=species_with_moves, level=5, current_hp=0)
        if len(creature.moves) > 0:
            print(f"✓ Creature created successfully with {len(creature.moves)} move(s)")
        else:
            print("✗ Creature has no moves despite species having moves")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    print("\n✅ Creature Move Validation: ALL TESTS PASSED")
    return True


def test_creature_generation():
    """Test that creature generator creates valid creatures."""
    print("\n=== Test: Creature Generation Validation ===\n")

    print("1. Generating all 151 creatures...")
    generator = CreatureGenerator(seed=12345)
    all_species = generator.generate_all_creatures()

    if len(all_species) == 151:
        print(f"✓ Generated exactly 151 creatures")
    else:
        print(f"✗ Generated {len(all_species)} creatures (expected 151)")
        return False

    print("\n2. Validating all creatures have moves...")
    creatures_without_moves = []
    for species in all_species:
        if not species.moves:
            creatures_without_moves.append(species.id)

    if len(creatures_without_moves) == 0:
        print("✓ All 151 creatures have at least one move")
    else:
        print(f"✗ {len(creatures_without_moves)} creatures have no moves: {creatures_without_moves[:10]}")
        return False

    print("\n3. Validating all creatures have valid stats...")
    invalid_stats = []
    for species in all_species:
        stats = species.base_stats
        if stats.hp <= 0 or stats.attack <= 0 or stats.defense <= 0:
            invalid_stats.append(species.id)

    if len(invalid_stats) == 0:
        print("✓ All creatures have valid stats (HP, attack, defense > 0)")
    else:
        print(f"✗ {len(invalid_stats)} creatures have invalid stats")
        return False

    print("\n4. Validating creature IDs are 1-151...")
    ids = [species.id for species in all_species]
    expected_ids = set(range(1, 152))
    actual_ids = set(ids)

    if actual_ids == expected_ids:
        print("✓ All creature IDs are exactly 1-151 with no gaps")
    else:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if missing:
            print(f"✗ Missing IDs: {sorted(list(missing))[:10]}")
        if extra:
            print(f"✗ Extra IDs: {sorted(list(extra))[:10]}")
        return False

    print("\n✅ Creature Generation Validation: ALL TESTS PASSED")
    return True


def run_all_tests():
    """Run all iteration 20 tests."""
    print("=" * 70)
    print("ITERATION 20 - BUG FIXES & OPTIMIZATIONS TEST SUITE")
    print("=" * 70)

    tests = [
        ("Battle Initialization Validation", test_battle_init_validation),
        ("Held Items Catalog Caching", test_held_items_catalog_caching),
        ("Focus Sash Reset Between Battles", test_focus_sash_reset),
        ("Creature Move Validation", test_creature_move_validation),
        ("Creature Generation Validation", test_creature_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {passed*100//total}%")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
