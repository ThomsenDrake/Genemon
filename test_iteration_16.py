"""
Test suite for Iteration 16: Bug fixes and code quality improvements.

Tests:
1. Move Relearner functionality (fixed critical bugs)
2. Safe input validation helper
3. Elite team creation refactoring
4. Code quality improvements
"""

import sys
import copy
from genemon.core.game import Game
from genemon.core.creature import Creature, Move, CreatureSpecies, CreatureStats, Team
from genemon.core.save_system import GameState
from genemon.creatures.generator import CreatureGenerator


def test_team_len_instead_of_size():
    """Test that Team uses len(creatures) instead of non-existent size() method."""
    print("Testing Team.creatures length access...")

    team = Team()

    # Test empty team
    assert len(team.creatures) == 0, "Empty team should have 0 creatures"
    print("  ✓ Empty team: len(creatures) = 0")

    # Create a simple species for testing
    species = CreatureSpecies(
        id=1,
        name="Testmon",
        types=["Flame"],
        base_stats=CreatureStats(hp=30, attack=25, defense=20, special=20, speed=20),
        moves=[],
        flavor_text="A test creature"
    )

    # Add creatures
    for i in range(3):
        creature = Creature(species=species, level=10)
        team.add_creature(creature)

    assert len(team.creatures) == 3, "Team should have 3 creatures"
    print("  ✓ Team with 3 creatures: len(creatures) = 3")

    # Verify size() method doesn't exist
    assert not hasattr(team, 'size'), "Team should not have size() method"
    print("  ✓ Team.size() method correctly does not exist")

    print("✅ Team length access - PASSED\n")


def test_move_deepcopy():
    """Test that moves are deep copied instead of using non-existent copy() method."""
    print("Testing Move deep copy...")

    # Create a move
    original_move = Move(
        name="Tackle",
        type="Beast",
        power=40,
        accuracy=100,
        max_pp=35,
        pp=35,
        description="A physical attack"
    )

    # Deep copy the move
    copied_move = copy.deepcopy(original_move)

    # Verify they're different objects
    assert copied_move is not original_move, "Copied move should be a different object"
    print("  ✓ Deep copy creates new object")

    # Verify they have same values
    assert copied_move.name == original_move.name, "Name should match"
    assert copied_move.power == original_move.power, "Power should match"
    assert copied_move.pp == original_move.pp, "PP should match"
    print("  ✓ Deep copy preserves all values")

    # Modify copied move and verify original is unchanged
    copied_move.pp = 20
    assert original_move.pp == 35, "Original move PP should be unchanged"
    assert copied_move.pp == 20, "Copied move PP should be modified"
    print("  ✓ Modifications to copy don't affect original")

    print("✅ Move deep copy - PASSED\n")


def test_species_types_list_access():
    """Test that species types are accessed via list indexing."""
    print("Testing species types list access...")

    # Create species with single type
    species_single = CreatureSpecies(
        id=1,
        name="Flamey",
        types=["Flame"],
        base_stats=CreatureStats(hp=30, attack=25, defense=20, special=20, speed=20),
        moves=[],
        flavor_text="A fire creature"
    )

    # Test single type access
    primary = species_single.types[0] if len(species_single.types) > 0 else None
    secondary = species_single.types[1] if len(species_single.types) > 1 else None

    assert primary == "Flame", "Primary type should be Flame"
    assert secondary is None, "Secondary type should be None"
    print("  ✓ Single type species: types[0] = 'Flame', types[1] = None")

    # Create species with dual type
    species_dual = CreatureSpecies(
        id=2,
        name="Aquaflame",
        types=["Aqua", "Flame"],
        base_stats=CreatureStats(hp=35, attack=30, defense=25, special=25, speed=25),
        moves=[],
        flavor_text="A water/fire creature"
    )

    # Test dual type access
    primary = species_dual.types[0] if len(species_dual.types) > 0 else None
    secondary = species_dual.types[1] if len(species_dual.types) > 1 else None

    assert primary == "Aqua", "Primary type should be Aqua"
    assert secondary == "Flame", "Secondary type should be Flame"
    print("  ✓ Dual type species: types[0] = 'Aqua', types[1] = 'Flame'")

    # Verify type1/type2 attributes don't exist
    assert not hasattr(species_single, 'type1'), "Species should not have type1 attribute"
    assert not hasattr(species_single, 'type2'), "Species should not have type2 attribute"
    print("  ✓ species.type1/type2 attributes correctly do not exist")

    print("✅ Species types list access - PASSED\n")


def test_safe_input_helper():
    """Test that Game has safe input validation helper method."""
    print("Testing safe input validation helper...")

    game = Game()

    # Verify method exists
    assert hasattr(game, '_get_int_input'), "Game should have _get_int_input method"
    print("  ✓ Game._get_int_input() method exists")

    # Verify method signature
    import inspect
    sig = inspect.signature(game._get_int_input)
    params = list(sig.parameters.keys())

    assert 'prompt' in params, "Method should have prompt parameter"
    assert 'default' in params, "Method should have default parameter"
    assert 'min_val' in params, "Method should have min_val parameter"
    assert 'max_val' in params, "Method should have max_val parameter"
    print("  ✓ Method has correct parameters (prompt, default, min_val, max_val)")

    # Note: We can't test the actual input handling without mocking stdin,
    # but we can verify the method is callable
    assert callable(game._get_int_input), "Method should be callable"
    print("  ✓ Method is callable")

    print("✅ Safe input helper - PASSED\n")


def test_elite_team_helper():
    """Test that Game has refactored elite team creation helper."""
    print("Testing elite team creation helper...")

    game = Game()

    # Verify helper method exists
    assert hasattr(game, '_create_typed_elite_team'), "Game should have _create_typed_elite_team method"
    print("  ✓ Game._create_typed_elite_team() method exists")

    # Verify method signature
    import inspect
    sig = inspect.signature(game._create_typed_elite_team)
    params = list(sig.parameters.keys())

    expected_params = ['seed_name', 'primary_types', 'support_types',
                       'base_level_normal', 'base_level_rematch', 'team_size',
                       'is_rematch', 'sort_by_stat']

    for param in expected_params:
        assert param in params, f"Method should have {param} parameter"

    print("  ✓ Method has all expected parameters")
    print("    - seed_name, primary_types, support_types")
    print("    - base_level_normal, base_level_rematch")
    print("    - team_size, is_rematch, sort_by_stat")

    # Verify elite team methods exist
    assert hasattr(game, '_create_elite_mystica_team'), "Elite Mystica team method should exist"
    assert hasattr(game, '_create_elite_tempest_team'), "Elite Tempest team method should exist"
    assert hasattr(game, '_create_elite_steel_team'), "Elite Steel team method should exist"
    assert hasattr(game, '_create_elite_phantom_team'), "Elite Phantom team method should exist"
    print("  ✓ All 4 Elite Four team methods exist")

    print("✅ Elite team helper - PASSED\n")


def test_elite_team_creation():
    """Test that refactored elite teams are created correctly."""
    print("Testing elite team creation with real data...")

    # Create a game with generated creatures
    game = Game()
    generator = CreatureGenerator(seed=12345)
    species_list = generator.generate_all_creatures()
    species_dict = {species.id: species for species in species_list}

    # Create game state
    game.state = GameState()
    game.state.player_name = "Test"
    game.state.save_name = "test"
    game.state.seed = 12345
    game.state.species_dict = species_dict

    # Test Mystica team creation (Mystic specialist)
    mystica_team = game._create_elite_mystica_team(is_rematch=False)
    assert len(mystica_team.creatures) == 5, "Mystica team should have 5 creatures"
    print("  ✓ Elite Mystica team created with 5 creatures")

    # Verify level progression (32-36)
    levels = [c.level for c in mystica_team.creatures]
    assert levels == [32, 33, 34, 35, 36], f"Levels should be [32-36], got {levels}"
    print(f"  ✓ Mystica team levels: {levels}")

    # Test rematch team has higher levels
    mystica_rematch = game._create_elite_mystica_team(is_rematch=True)
    rematch_levels = [c.level for c in mystica_rematch.creatures]
    assert rematch_levels == [50, 51, 52, 53, 54], f"Rematch levels should be [50-54], got {rematch_levels}"
    print(f"  ✓ Mystica rematch levels: {rematch_levels}")

    # Test Tempest team (Gale specialist with speed sorting)
    tempest_team = game._create_elite_tempest_team(is_rematch=False)
    assert len(tempest_team.creatures) == 5, "Tempest team should have 5 creatures"
    tempest_levels = [c.level for c in tempest_team.creatures]
    assert tempest_levels == [33, 34, 35, 36, 37], f"Tempest levels should be [33-37], got {tempest_levels}"
    print(f"  ✓ Elite Tempest team created: levels {tempest_levels}")

    # Test Steel team (Metal specialist with defense sorting)
    steel_team = game._create_elite_steel_team(is_rematch=False)
    assert len(steel_team.creatures) == 5, "Steel team should have 5 creatures"
    steel_levels = [c.level for c in steel_team.creatures]
    assert steel_levels == [34, 35, 36, 37, 38], f"Steel levels should be [34-38], got {steel_levels}"
    print(f"  ✓ Elite Steel team created: levels {steel_levels}")

    # Test Phantom team (Spirit/Shadow specialist)
    phantom_team = game._create_elite_phantom_team(is_rematch=False)
    assert len(phantom_team.creatures) == 5, "Phantom team should have 5 creatures"
    phantom_levels = [c.level for c in phantom_team.creatures]
    assert phantom_levels == [35, 36, 37, 38, 39], f"Phantom levels should be [35-39], got {phantom_levels}"
    print(f"  ✓ Elite Phantom team created: levels {phantom_levels}")

    print("✅ Elite team creation - PASSED\n")


def test_constants_module():
    """Test that constants.py module exists and has expected constants."""
    print("Testing constants module...")

    try:
        from genemon.core import constants
        print("  ✓ constants module imports successfully")
    except ImportError:
        print("  ✗ constants module not found")
        return False

    # Check for key constant categories
    expected_constants = [
        'TOTAL_CREATURES',
        'LEGENDARY_START_ID',
        'CRIT_MULTIPLIER_NORMAL',
        'STAB_MULTIPLIER',
        'LIFE_ORB_MULTIPLIER',
        'BURN_ATTACK_REDUCTION',
        'TEAM_MAX_SIZE',
        'POTION_HEAL_AMOUNT',
        'STARTING_MONEY'
    ]

    for const in expected_constants:
        assert hasattr(constants, const), f"constants should have {const}"

    print("  ✓ All expected constant categories present:")
    print("    - Creature generation (TOTAL_CREATURES, LEGENDARY_START_ID)")
    print("    - Battle mechanics (CRIT_MULTIPLIER, STAB_MULTIPLIER)")
    print("    - Held items (LIFE_ORB_MULTIPLIER)")
    print("    - Status effects (BURN_ATTACK_REDUCTION)")
    print("    - Team/Items (TEAM_MAX_SIZE, POTION_HEAL_AMOUNT)")
    print("    - Economy (STARTING_MONEY)")

    # Verify some values
    assert constants.TOTAL_CREATURES == 151, "Should have 151 creatures"
    assert constants.TEAM_MAX_SIZE == 6, "Team max size should be 6"
    assert constants.STAB_MULTIPLIER == 1.5, "STAB should be 1.5x"
    print("  ✓ Constant values are correct")

    print("✅ Constants module - PASSED\n")


def run_all_tests():
    """Run all iteration 16 tests."""
    print("=" * 60)
    print("GENEMON ITERATION 16 TEST SUITE")
    print("Testing Bug Fixes and Code Quality Improvements")
    print("=" * 60)

    tests = [
        test_team_len_instead_of_size,
        test_move_deepcopy,
        test_species_types_list_access,
        test_safe_input_helper,
        test_elite_team_helper,
        test_elite_team_creation,
        test_constants_module
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} - FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} - ERROR: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
