"""
Test suite for Iteration 28 - Battle Module Extraction (Preparation Phase)

This test suite validates:
1. DamageCalculator module exists and is well-structured
2. BattleStatManager module exists and is well-structured
3. Both modules are properly documented
4. Modules are ready for future integration into battle/engine.py
5. Code quality metrics

NOTE: This iteration creates the modules but does NOT integrate them into the battle system yet.
Future iterations will perform the integration and add functional tests.
"""

import unittest
import os
from genemon.battle.damage_calculator import DamageCalculator
from genemon.battle.stat_manager import BattleStatManager
from genemon.battle.engine import BattleLog


class TestDamageCalculatorModule(unittest.TestCase):
    """Test the extracted DamageCalculator module structure."""

    def test_module_import(self):
        """Test that DamageCalculator module can be imported."""
        self.assertIsNotNone(DamageCalculator)

    def test_calculator_instantiation(self):
        """Test that DamageCalculator can be instantiated."""
        calculator = DamageCalculator()
        self.assertIsInstance(calculator, DamageCalculator)

    def test_has_calculate_damage_method(self):
        """Test that calculate_damage method exists."""
        calculator = DamageCalculator()
        self.assertTrue(hasattr(calculator, 'calculate_damage'))
        self.assertTrue(callable(getattr(calculator, 'calculate_damage')))

    def test_has_check_critical_hit_method(self):
        """Test that check_critical_hit method exists."""
        calculator = DamageCalculator()
        self.assertTrue(hasattr(calculator, 'check_critical_hit'))
        self.assertTrue(callable(getattr(calculator, 'check_critical_hit')))

    def test_has_weather_modifiers_method(self):
        """Test that _apply_weather_modifiers method exists."""
        calculator = DamageCalculator()
        self.assertTrue(hasattr(calculator, '_apply_weather_modifiers'))
        self.assertTrue(callable(getattr(calculator, '_apply_weather_modifiers')))

    def test_has_held_item_modifiers_method(self):
        """Test that _apply_held_item_modifiers method exists."""
        calculator = DamageCalculator()
        self.assertTrue(hasattr(calculator, '_apply_held_item_modifiers'))
        self.assertTrue(callable(getattr(calculator, '_apply_held_item_modifiers')))

    def test_has_ability_modifiers_method(self):
        """Test that _apply_ability_modifiers method exists."""
        calculator = DamageCalculator()
        self.assertTrue(hasattr(calculator, '_apply_ability_modifiers'))
        self.assertTrue(callable(getattr(calculator, '_apply_ability_modifiers')))


class TestBattleStatManagerModule(unittest.TestCase):
    """Test the extracted BattleStatManager module structure."""

    def test_module_import(self):
        """Test that BattleStatManager module can be imported."""
        self.assertIsNotNone(BattleStatManager)

    def test_stat_manager_instantiation(self):
        """Test that BattleStatManager can be instantiated."""
        stat_manager = BattleStatManager()
        self.assertIsInstance(stat_manager, BattleStatManager)

    def test_has_initial_stat_stages(self):
        """Test that stat_manager has initial stat stage dictionaries."""
        stat_manager = BattleStatManager()
        self.assertIsNotNone(stat_manager.player_stat_stages)
        self.assertIsNotNone(stat_manager.opponent_stat_stages)
        self.assertIsInstance(stat_manager.player_stat_stages, dict)
        self.assertIsInstance(stat_manager.opponent_stat_stages, dict)

    def test_has_required_stats(self):
        """Test that all required stats are tracked."""
        stat_manager = BattleStatManager()
        required_stats = ["attack", "defense", "speed", "special", "accuracy", "evasion"]
        for stat in required_stats:
            self.assertIn(stat, stat_manager.player_stat_stages)
            self.assertIn(stat, stat_manager.opponent_stat_stages)

    def test_has_modify_stat_stage_method(self):
        """Test that modify_stat_stage method exists."""
        stat_manager = BattleStatManager()
        self.assertTrue(hasattr(stat_manager, 'modify_stat_stage'))
        self.assertTrue(callable(getattr(stat_manager, 'modify_stat_stage')))

    def test_has_reset_stat_stages_method(self):
        """Test that reset_stat_stages method exists."""
        stat_manager = BattleStatManager()
        self.assertTrue(hasattr(stat_manager, 'reset_stat_stages'))
        self.assertTrue(callable(getattr(stat_manager, 'reset_stat_stages')))

    def test_has_get_modified_stat_method(self):
        """Test that get_modified_stat method exists."""
        stat_manager = BattleStatManager()
        self.assertTrue(hasattr(stat_manager, 'get_modified_stat'))
        self.assertTrue(callable(getattr(stat_manager, 'get_modified_stat')))

    def test_has_get_stat_stage_multiplier_method(self):
        """Test that get_stat_stage_multiplier method exists."""
        stat_manager = BattleStatManager()
        self.assertTrue(hasattr(stat_manager, 'get_stat_stage_multiplier'))
        self.assertTrue(callable(getattr(stat_manager, 'get_stat_stage_multiplier')))


class TestCodeQualityMetrics(unittest.TestCase):
    """Test code quality improvements for Iteration 28."""

    def test_damage_calculator_file_exists(self):
        """Test that damage_calculator.py was created."""
        file_path = "genemon/battle/damage_calculator.py"
        self.assertTrue(os.path.exists(file_path), f"{file_path} should exist")

    def test_stat_manager_file_exists(self):
        """Test that stat_manager.py was created."""
        file_path = "genemon/battle/stat_manager.py"
        self.assertTrue(os.path.exists(file_path), f"{file_path} should exist")

    def test_damage_calculator_line_count(self):
        """Test that damage_calculator.py has reasonable size."""
        with open("genemon/battle/damage_calculator.py", 'r') as f:
            lines = len(f.readlines())
        self.assertGreater(lines, 200, "DamageCalculator should have substantial code")
        self.assertLess(lines, 600, "DamageCalculator should be focused")

    def test_stat_manager_line_count(self):
        """Test that stat_manager.py has reasonable size."""
        with open("genemon/battle/stat_manager.py", 'r') as f:
            lines = len(f.readlines())
        self.assertGreater(lines, 150, "StatManager should have substantial code")
        self.assertLess(lines, 400, "StatManager should be focused")

    def test_modules_have_docstrings(self):
        """Test that new modules have proper documentation."""
        from genemon.battle import damage_calculator, stat_manager

        self.assertIsNotNone(damage_calculator.__doc__, "damage_calculator should have module docstring")
        self.assertIsNotNone(stat_manager.__doc__, "stat_manager should have module docstring")
        self.assertGreater(len(damage_calculator.__doc__), 50, "Docstring should be substantial")
        self.assertGreater(len(stat_manager.__doc__), 50, "Docstring should be substantial")

    def test_classes_have_docstrings(self):
        """Test that classes have proper documentation."""
        self.assertIsNotNone(DamageCalculator.__doc__, "DamageCalculator should have docstring")
        self.assertIsNotNone(BattleStatManager.__doc__, "BattleStatManager should have docstring")


class TestModuleStructure(unittest.TestCase):
    """Test overall module structure and organization."""

    def test_battle_module_exists(self):
        """Test that genemon.battle module exists."""
        import genemon.battle
        self.assertIsNotNone(genemon.battle)

    def test_can_import_all_new_modules(self):
        """Test that all new modules can be imported together."""
        try:
            from genemon.battle.damage_calculator import DamageCalculator
            from genemon.battle.stat_manager import BattleStatManager
            from genemon.battle.engine import BattleLog
            success = True
        except ImportError:
            success = False
        self.assertTrue(success, "Should be able to import all new modules")

    def test_modules_dont_conflict_with_engine(self):
        """Test that new modules don't break existing engine imports."""
        try:
            from genemon.battle import engine
            self.assertIsNotNone(engine)
            success = True
        except ImportError:
            success = False
        self.assertTrue(success, "New modules should not break engine import")


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
