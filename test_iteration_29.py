#!/usr/bin/env python3
"""
Iteration 29 Test Suite - Battle Module Integration

This test suite validates the integration of DamageCalculator and BattleStatManager
into the battle/engine.py module. It ensures backward compatibility and correct
functionality after refactoring.
"""

import unittest
import sys
import os

# Add the loop directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.battle.engine import Battle, BattleAction, BattleResult, Weather, BattleLog
from genemon.battle.damage_calculator import DamageCalculator
from genemon.battle.stat_manager import BattleStatManager
from genemon.core.creature import Creature, Team, Move, CreatureSpecies, CreatureStats, StatusEffect, Ability


def create_test_creature(name="TestMon", types=None, level=10, attack=50, defense=50, hp=100, ability=None, moves=None):
    """Helper function to create test creatures."""
    if types is None:
        types = ["Normal"]
    if moves is None:
        moves = [Move(name="Tackle", type="Normal", power=40, accuracy=100, pp=35, max_pp=35)]

    base_stats = CreatureStats(hp=hp, attack=attack, defense=defense, speed=50, special=50)
    species = CreatureSpecies(
        id=1,
        name=name,
        types=types,
        base_stats=base_stats,
        moves=moves,
        ability=ability,
        flavor_text="A test creature"
    )

    return Creature(species=species, level=level)


class TestBattleModuleIntegration(unittest.TestCase):
    """Test that Battle class properly integrates with DamageCalculator and BattleStatManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.creature_a = create_test_creature("MonA")
        self.creature_b = create_test_creature("MonB")
        self.player_team = Team(creatures=[self.creature_a])
        self.opponent_team = Team(creatures=[self.creature_b])

    def test_battle_has_damage_calculator(self):
        """Test that Battle instance has a DamageCalculator."""
        battle = Battle(self.player_team, self.opponent_team)
        self.assertIsInstance(battle.damage_calculator, DamageCalculator)

    def test_battle_has_stat_manager(self):
        """Test that Battle instance has a BattleStatManager."""
        battle = Battle(self.player_team, self.opponent_team)
        self.assertIsInstance(battle.stat_manager, BattleStatManager)

    def test_battle_initialization_no_errors(self):
        """Test that Battle initializes without errors."""
        try:
            battle = Battle(self.player_team, self.opponent_team)
            self.assertEqual(battle.result, BattleResult.ONGOING)
        except Exception as e:
            self.fail(f"Battle initialization failed: {e}")

    def test_damage_calculator_integration(self):
        """Test that damage calculation works through the battle engine."""
        battle = Battle(self.player_team, self.opponent_team)

        # Execute an attack
        initial_hp = battle.opponent_active.hp
        result = battle.execute_turn(BattleAction.ATTACK, 0)

        # Check that damage was dealt (opponent HP should be reduced)
        self.assertLess(battle.opponent_active.hp, initial_hp,
                        "Damage should have been dealt to opponent")

    def test_stat_manager_integration(self):
        """Test that stat stages are properly managed through stat_manager."""
        battle = Battle(self.player_team, self.opponent_team)

        # Check initial stat stages
        player_stages = battle.stat_manager.get_stat_stages(True)
        self.assertEqual(player_stages["attack"], 0, "Initial attack stage should be 0")

        # Modify stat stage
        success = battle.stat_manager.modify_stat_stage(
            battle.player_active, True, "attack", 2, battle.log
        )
        self.assertTrue(success, "Stat modification should succeed")

        # Check that stat stage was modified
        player_stages = battle.stat_manager.get_stat_stages(True)
        self.assertEqual(player_stages["attack"], 2, "Attack stage should be 2 after modification")


class TestStatStageModification(unittest.TestCase):
    """Test stat stage modification through integrated stat manager."""

    def test_stat_stage_limits(self):
        """Test that stat stages are clamped to -6/+6."""
        creature = create_test_creature()
        team = Team(creatures=[creature])
        opponent = create_test_creature()
        opponent_team = Team(creatures=[opponent])
        battle = Battle(team, opponent_team)

        # Boost attack to maximum
        for i in range(10):  # Try to boost beyond limit
            battle.stat_manager.modify_stat_stage(battle.player_active, True, "attack", 2, battle.log)

        # Check that it's clamped to +6
        player_stages = battle.stat_manager.get_stat_stages(True)
        self.assertEqual(player_stages["attack"], 6, "Attack stage should be clamped to +6")

    def test_stat_stage_multipliers(self):
        """Test that stat stage multipliers are correct."""
        creature = create_test_creature()
        team = Team(creatures=[creature])
        opponent = create_test_creature()
        opponent_team = Team(creatures=[opponent])
        battle = Battle(team, opponent_team)

        # Test various stages
        test_cases = [
            (-6, 0.25),  # -6 stages = 0.25x
            (-3, 0.4),   # -3 stages ≈ 0.4x
            (0, 1.0),    # 0 stages = 1.0x
            (2, 2.0),    # +2 stages = 2.0x
            (6, 4.0),    # +6 stages = 4.0x
        ]

        for stage, expected_mult in test_cases:
            actual_mult = battle.stat_manager.get_stat_stage_multiplier(stage)
            self.assertAlmostEqual(actual_mult, expected_mult, places=2,
                                   msg=f"Stage {stage} should have multiplier {expected_mult}")


class TestDamageCalculation(unittest.TestCase):
    """Test damage calculation through integrated damage calculator."""

    def test_damage_calculation_basic(self):
        """Test that basic damage calculation works."""
        attacker = create_test_creature("Attacker", attack=100)
        defender = create_test_creature("Defender", defense=50)
        player_team = Team(creatures=[attacker])
        opponent_team = Team(creatures=[defender])
        battle = Battle(player_team, opponent_team)

        # Execute an attack
        initial_hp = battle.opponent_active.hp
        battle.execute_turn(BattleAction.ATTACK, 0)
        final_hp = battle.opponent_active.hp

        # Verify damage was dealt
        self.assertLess(final_hp, initial_hp, "Damage should be dealt")
        self.assertGreater(final_hp, 0, "Defender should not be one-shot")


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing battle functionality still works after refactoring."""

    def test_battle_completion(self):
        """Test that battles can complete normally."""
        creature_a = create_test_creature("A")
        creature_b = create_test_creature("B")
        player_team = Team(creatures=[creature_a])
        opponent_team = Team(creatures=[creature_b])
        battle = Battle(player_team, opponent_team, is_wild=True)

        # Execute turns until battle ends (with safety limit)
        turn_limit = 100
        for i in range(turn_limit):
            if battle.result != BattleResult.ONGOING:
                break
            battle.execute_turn(BattleAction.ATTACK, 0)

        # Battle should have ended
        self.assertNotEqual(battle.result, BattleResult.ONGOING,
                            "Battle should end within turn limit")

    def test_wild_battle_can_run(self):
        """Test that running from wild battles still works."""
        creature_a = create_test_creature("A")
        creature_b = create_test_creature("B")
        player_team = Team(creatures=[creature_a])
        opponent_team = Team(creatures=[creature_b])
        battle = Battle(player_team, opponent_team, is_wild=True, can_run=True)

        # Try to run (may succeed or fail due to RNG, but shouldn't crash)
        try:
            result = battle.execute_turn(BattleAction.RUN, None)
            self.assertIn(result, [BattleResult.ONGOING, BattleResult.RAN_AWAY],
                          "Run attempt should return valid result")
        except Exception as e:
            self.fail(f"Running from battle should not raise exception: {e}")


class TestCodeQuality(unittest.TestCase):
    """Test code quality metrics after refactoring."""

    def test_engine_reduced_size(self):
        """Test that engine.py was reduced in size."""
        engine_path = os.path.join(os.path.dirname(__file__), "genemon", "battle", "engine.py")
        with open(engine_path, 'r') as f:
            lines = len(f.readlines())

        # Should be significantly smaller than original 1,370 lines
        self.assertLess(lines, 1200, f"engine.py should be reduced (currently {lines} lines)")
        self.assertGreater(lines, 800, f"engine.py should still have substantial code ({lines} lines)")

    def test_modules_imported(self):
        """Test that new modules are properly imported in engine.py."""
        engine_path = os.path.join(os.path.dirname(__file__), "genemon", "battle", "engine.py")
        with open(engine_path, 'r') as f:
            content = f.read()

        # These imports should exist
        self.assertIn("from .damage_calculator import DamageCalculator", content,
                      "DamageCalculator should be imported")
        self.assertIn("from .stat_manager import BattleStatManager", content,
                      "BattleStatManager should be imported")


def run_tests():
    """Run all tests and display results."""
    print("\n" + "=" * 60)
    print("ITERATION 29 TEST SUITE - BATTLE MODULE INTEGRATION")
    print("=" * 60 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBattleModuleIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStatStageModification))
    suite.addTests(loader.loadTestsFromTestCase(TestDamageCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeQuality))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"TOTAL: {passed}/{total} tests passed ({100 * passed / total:.1f}%)")

    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")

    print("=" * 60 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
