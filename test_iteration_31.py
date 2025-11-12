"""
Test Suite for Iteration 31 - Performance Profiling & Optimization

This test suite validates the performance profiling system and ensures
performance benchmarks work correctly.
"""

import unittest
import time
from genemon.utils.profiler import PerformanceProfiler, ProfileResult, profile, get_profiler


class TestPerformanceProfiler(unittest.TestCase):
    """Test PerformanceProfiler class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()

    def test_profiler_initialization(self):
        """Test that profiler initializes correctly."""
        self.assertIsNotNone(self.profiler)
        self.assertEqual(len(self.profiler.measurements), 0)
        self.assertEqual(len(self.profiler.active_timers), 0)

    def test_measure_context_manager(self):
        """Test profiler as context manager."""
        with self.profiler.measure("test_operation"):
            time.sleep(0.01)  # 10ms

        result = self.profiler.get_result("test_operation")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "test_operation")
        self.assertEqual(result.iterations, 1)
        self.assertGreater(result.duration, 0.009)  # At least 9ms
        self.assertLess(result.duration, 0.1)  # Less than 100ms

    def test_start_stop_timing(self):
        """Test manual start/stop timing."""
        self.profiler.start("manual_test")
        time.sleep(0.01)
        duration = self.profiler.stop("manual_test")

        self.assertGreater(duration, 0.009)
        result = self.profiler.get_result("manual_test")
        self.assertIsNotNone(result)
        self.assertEqual(result.iterations, 1)

    def test_profile_decorator(self):
        """Test profiler as decorator."""
        @self.profiler.profile("decorated_function")
        def test_func():
            time.sleep(0.01)
            return 42

        result = test_func()
        self.assertEqual(result, 42)

        profile_result = self.profiler.get_result("decorated_function")
        self.assertIsNotNone(profile_result)
        self.assertGreater(profile_result.duration, 0.009)

    def test_multiple_iterations(self):
        """Test profiling multiple iterations."""
        for _ in range(10):
            with self.profiler.measure("multi_test"):
                time.sleep(0.001)  # 1ms each

        result = self.profiler.get_result("multi_test")
        self.assertEqual(result.iterations, 10)
        self.assertGreater(result.duration, 0.009)  # Total > 9ms
        self.assertGreater(result.avg_time, 0.0009)  # Avg > 0.9ms

    def test_metadata(self):
        """Test adding metadata to profiling entries."""
        with self.profiler.measure("metadata_test"):
            time.sleep(0.001)

        self.profiler.add_metadata("metadata_test", {"test_key": "test_value", "number": 42})
        result = self.profiler.get_result("metadata_test")

        self.assertIn("test_key", result.metadata)
        self.assertEqual(result.metadata["test_key"], "test_value")
        self.assertEqual(result.metadata["number"], 42)

    def test_get_all_results(self):
        """Test retrieving all results sorted by duration."""
        with self.profiler.measure("fast"):
            time.sleep(0.001)

        with self.profiler.measure("slow"):
            time.sleep(0.01)

        with self.profiler.measure("medium"):
            time.sleep(0.005)

        results = self.profiler.get_results()
        self.assertEqual(len(results), 3)

        # Should be sorted by duration (descending)
        self.assertEqual(results[0].name, "slow")
        self.assertEqual(results[1].name, "medium")
        self.assertEqual(results[2].name, "fast")

    def test_clear_specific(self):
        """Test clearing specific profiling entry."""
        with self.profiler.measure("test1"):
            pass
        with self.profiler.measure("test2"):
            pass

        self.profiler.clear("test1")
        self.assertIsNone(self.profiler.get_result("test1"))
        self.assertIsNotNone(self.profiler.get_result("test2"))

    def test_clear_all(self):
        """Test clearing all profiling data."""
        with self.profiler.measure("test1"):
            pass
        with self.profiler.measure("test2"):
            pass

        self.profiler.clear()
        self.assertEqual(len(self.profiler.measurements), 0)
        self.assertIsNone(self.profiler.get_result("test1"))
        self.assertIsNone(self.profiler.get_result("test2"))

    def test_profile_result_str(self):
        """Test ProfileResult string representation."""
        result = ProfileResult(
            name="test",
            duration=1.5,
            iterations=100,
            avg_time=0.015,
            min_time=0.010,
            max_time=0.020
        )

        str_repr = str(result)
        self.assertIn("test", str_repr)
        self.assertIn("1.5000s", str_repr)
        self.assertIn("100", str_repr)

    def test_global_profiler(self):
        """Test global profiler instance."""
        global_prof = get_profiler()
        self.assertIsInstance(global_prof, PerformanceProfiler)

        @profile("global_test")
        def test_func():
            return 42

        result = test_func()
        self.assertEqual(result, 42)

        # Global profiler should have recorded this
        profile_result = global_prof.get_result("global_test")
        self.assertIsNotNone(profile_result)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test performance benchmarks for critical systems."""

    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()

    def test_creature_generation_performance(self):
        """Test creature generation performance is acceptable."""
        from genemon.creatures.generator import CreatureGenerator

        generator = CreatureGenerator(12345)

        with self.profiler.measure("creature_single"):
            creature = generator._generate_creature(
                creature_id=1,
                power_level="basic",
                stage=1
            )

        result = self.profiler.get_result("creature_single")
        self.assertIsNotNone(result)
        # Single creature should take < 100ms
        self.assertLess(result.avg_time, 0.1)

    def test_battle_damage_calculation_performance(self):
        """Test damage calculation performance."""
        from genemon.creatures.generator import CreatureGenerator
        from genemon.core.creature import Creature
        from genemon.battle.damage_calculator import DamageCalculator

        generator = CreatureGenerator(12345)
        species_list = generator.generate_all_creatures()

        attacker = Creature(species_list[0], level=50)
        defender = Creature(species_list[1], level=50)
        calculator = DamageCalculator()

        # Create stat modifier functions that return base stats (no modifications)
        def attacker_stat_mod(creature, stat_name):
            return getattr(creature, stat_name.lower())

        def defender_stat_mod(creature, stat_name):
            return getattr(creature, stat_name.lower())

        if attacker.moves:
            move = attacker.moves[0]
            with self.profiler.measure("damage_calc"):
                for _ in range(100):
                    calculator.calculate_damage(
                        attacker=attacker,
                        defender=defender,
                        move=move,
                        is_critical=False,
                        weather=None,
                        attacker_stat_modifier=attacker_stat_mod,
                        defender_stat_modifier=defender_stat_mod
                    )

            result = self.profiler.get_result("damage_calc")
            self.assertIsNotNone(result)
            # 100 damage calculations should take < 1 second
            self.assertLess(result.duration, 1.0)
            # Average per calculation should be < 10ms
            self.assertLess(result.avg_time, 0.01)

    def test_npc_loading_performance(self):
        """Test NPC data loading performance."""
        from genemon.data.npc_loader import NPCLoader

        with self.profiler.measure("npc_load"):
            for _ in range(10):
                loader = NPCLoader()
                npcs = loader.load_all_npcs()

        result = self.profiler.get_result("npc_load")
        self.assertIsNotNone(result)
        # 10 NPC loads should take < 1 second
        self.assertLess(result.duration, 1.0)


def print_test_header():
    """Print test suite header."""
    print("\n" + "=" * 70)
    print("ITERATION 31 TEST SUITE - PERFORMANCE PROFILING")
    print("=" * 70 + "\n")


def run_tests():
    """Run all tests and display results."""
    print_test_header()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceProfiler))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmarks))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"TOTAL: {result.testsRun} tests")
    print(f"✓ PASSED: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f"✗ FAILED: {len(result.failures)}")
    if result.errors:
        print(f"⚠ ERRORS: {len(result.errors)}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")

    print("=" * 70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
