"""
Tests for Iteration 27 - MenuManager Refactoring

This test suite validates the new MenuManager module and ensures
that the menu extraction from game.py was successful.
"""

import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch, MagicMock

# Add the loop directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.ui.menu_manager import MenuManager
from genemon.ui.display import Display
from genemon.core.game import Game


class TestMenuManagerExists(unittest.TestCase):
    """Test that MenuManager module was created successfully."""

    def test_menu_manager_module_exists(self):
        """Test that MenuManager module can be imported."""
        from genemon.ui import menu_manager
        self.assertTrue(hasattr(menu_manager, 'MenuManager'))

    def test_menu_manager_class_exists(self):
        """Test that MenuManager class is available."""
        from genemon.ui.menu_manager import MenuManager
        self.assertTrue(callable(MenuManager))

    def test_menu_manager_initialization(self):
        """Test that MenuManager can be instantiated."""
        display = Display()
        manager = MenuManager(display)
        self.assertIsNotNone(manager)
        self.assertEqual(manager.display, display)


class TestMenuManagerMethods(unittest.TestCase):
    """Test that MenuManager has all required methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.display = Display()
        self.manager = MenuManager(self.display)

    def test_has_show_team_menu(self):
        """Test that show_team_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_team_menu'))
        self.assertTrue(callable(self.manager.show_team_menu))

    def test_has_show_items_menu(self):
        """Test that show_items_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_items_menu'))
        self.assertTrue(callable(self.manager.show_items_menu))

    def test_has_show_shop_menu(self):
        """Test that show_shop_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_shop_menu'))
        self.assertTrue(callable(self.manager.show_shop_menu))

    def test_has_show_badges(self):
        """Test that show_badges method exists."""
        self.assertTrue(hasattr(self.manager, 'show_badges'))
        self.assertTrue(callable(self.manager.show_badges))

    def test_has_show_move_relearner_menu(self):
        """Test that show_move_relearner_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_move_relearner_menu'))
        self.assertTrue(callable(self.manager.show_move_relearner_menu))

    def test_has_show_pokedex(self):
        """Test that show_pokedex method exists."""
        self.assertTrue(hasattr(self.manager, 'show_pokedex'))
        self.assertTrue(callable(self.manager.show_pokedex))

    def test_has_show_type_chart_menu(self):
        """Test that show_type_chart_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_type_chart_menu'))
        self.assertTrue(callable(self.manager.show_type_chart_menu))

    def test_has_show_sprite_viewer_menu(self):
        """Test that show_sprite_viewer_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_sprite_viewer_menu'))
        self.assertTrue(callable(self.manager.show_sprite_viewer_menu))

    def test_has_show_settings_menu(self):
        """Test that show_settings_menu method exists."""
        self.assertTrue(hasattr(self.manager, 'show_settings_menu'))
        self.assertTrue(callable(self.manager.show_settings_menu))


class TestGameIntegration(unittest.TestCase):
    """Test that Game class properly integrates with MenuManager."""

    def test_game_imports_menu_manager(self):
        """Test that Game imports MenuManager."""
        import genemon.core.game as game_module
        # Check if MenuManager is imported in the module
        self.assertTrue('MenuManager' in dir(game_module))

    def test_game_has_menu_manager_attribute(self):
        """Test that Game instance has menu_manager attribute."""
        game = Game()
        self.assertTrue(hasattr(game, 'menu_manager'))
        self.assertIsInstance(game.menu_manager, MenuManager)

    def test_game_no_longer_has_old_menu_methods(self):
        """Test that old menu methods were removed from Game class."""
        game = Game()

        # These methods should no longer exist in Game class
        self.assertFalse(hasattr(game, '_show_team_menu'))
        self.assertFalse(hasattr(game, '_show_items_menu'))
        self.assertFalse(hasattr(game, '_shop_menu'))
        self.assertFalse(hasattr(game, '_show_badges'))
        self.assertFalse(hasattr(game, '_move_relearner_menu'))
        self.assertFalse(hasattr(game, '_show_pokedex'))
        self.assertFalse(hasattr(game, '_show_type_chart_menu'))
        self.assertFalse(hasattr(game, '_show_sprite_viewer_menu'))
        self.assertFalse(hasattr(game, '_show_settings_menu'))

    def test_game_still_has_trading_and_breeding_menus(self):
        """Test that trading and breeding menus are still in Game class."""
        game = Game()

        # These methods should still exist (they weren't moved)
        self.assertTrue(hasattr(game, '_show_trading_menu'))
        self.assertTrue(hasattr(game, '_show_breeding_menu'))


class TestCodeQualityMetrics(unittest.TestCase):
    """Test that code quality improved with refactoring."""

    def test_game_py_line_count_reduced(self):
        """Test that game.py line count was significantly reduced."""
        game_file = os.path.join(os.path.dirname(__file__), 'genemon', 'core', 'game.py')

        with open(game_file, 'r') as f:
            lines = len(f.readlines())

        # game.py should now be around 1081 lines (was 1467)
        self.assertLess(lines, 1150, f"game.py should be under 1150 lines (found {lines})")
        self.assertGreater(lines, 1000, f"game.py should have over 1000 lines (found {lines})")

    def test_menu_manager_created(self):
        """Test that menu_manager.py was created."""
        menu_manager_file = os.path.join(os.path.dirname(__file__), 'genemon', 'ui', 'menu_manager.py')
        self.assertTrue(os.path.exists(menu_manager_file))

    def test_menu_manager_line_count(self):
        """Test that menu_manager.py contains the extracted code."""
        menu_manager_file = os.path.join(os.path.dirname(__file__), 'genemon', 'ui', 'menu_manager.py')

        with open(menu_manager_file, 'r') as f:
            lines = len(f.readlines())

        # menu_manager.py should be around 468 lines
        self.assertGreater(lines, 400, f"menu_manager.py should have over 400 lines (found {lines})")
        self.assertLess(lines, 550, f"menu_manager.py should be under 550 lines (found {lines})")

    def test_total_python_line_count(self):
        """Test that total Python line count is reasonable."""
        import subprocess

        result = subprocess.run(
            ['find', '.', '-name', '*.py', '-type', 'f', '-exec', 'wc', '-l', '{}', '+'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )

        lines = result.stdout.strip().split('\n')
        total_line = lines[-1]
        total_lines = int(total_line.split()[0])

        # Total should be around 18,000-19,000 lines (11,860 core + tests)
        self.assertGreater(total_lines, 15000, f"Total Python lines should be over 15000 (found {total_lines})")


class TestMenuManagerDocumentation(unittest.TestCase):
    """Test that MenuManager has proper documentation."""

    def test_module_has_docstring(self):
        """Test that menu_manager module has a docstring."""
        from genemon.ui import menu_manager
        self.assertIsNotNone(menu_manager.__doc__)
        self.assertGreater(len(menu_manager.__doc__), 50)

    def test_class_has_docstring(self):
        """Test that MenuManager class has a docstring."""
        from genemon.ui.menu_manager import MenuManager
        self.assertIsNotNone(MenuManager.__doc__)

    def test_methods_have_docstrings(self):
        """Test that MenuManager methods have docstrings."""
        from genemon.ui.menu_manager import MenuManager

        methods_to_check = [
            'show_team_menu',
            'show_items_menu',
            'show_shop_menu',
            'show_badges',
            'show_move_relearner_menu',
            'show_pokedex',
            'show_type_chart_menu',
            'show_sprite_viewer_menu',
            'show_settings_menu'
        ]

        for method_name in methods_to_check:
            method = getattr(MenuManager, method_name)
            self.assertIsNotNone(method.__doc__, f"{method_name} should have a docstring")


class TestCodeStructure(unittest.TestCase):
    """Test code structure and imports."""

    def test_menu_manager_imports_input_validator(self):
        """Test that MenuManager imports InputValidator."""
        from genemon.ui import menu_manager
        import inspect

        source = inspect.getsource(menu_manager)
        self.assertIn('InputValidator', source)

    def test_menu_manager_imports_display(self):
        """Test that MenuManager imports Display."""
        from genemon.ui import menu_manager
        import inspect

        source = inspect.getsource(menu_manager)
        self.assertIn('Display', source)

    def test_no_duplicate_code(self):
        """Test that menu code is not duplicated between game.py and menu_manager.py."""
        game_file = os.path.join(os.path.dirname(__file__), 'genemon', 'core', 'game.py')
        menu_file = os.path.join(os.path.dirname(__file__), 'genemon', 'ui', 'menu_manager.py')

        with open(game_file, 'r') as f:
            game_content = f.read()

        # Check that menu method definitions are not in game.py
        self.assertNotIn('def _show_team_menu(self):', game_content)
        self.assertNotIn('def _show_items_menu(self):', game_content)
        self.assertNotIn('def _shop_menu(self, npc:', game_content)
        self.assertNotIn('def _show_badges(self):', game_content)
        self.assertNotIn('def _move_relearner_menu(self):', game_content)
        self.assertNotIn('def _show_pokedex(self):', game_content)
        self.assertNotIn('def _show_type_chart_menu(self):', game_content)
        self.assertNotIn('def _show_sprite_viewer_menu(self):', game_content)
        self.assertNotIn('def _show_settings_menu(self):', game_content)


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMenuManagerExists))
    suite.addTests(loader.loadTestsFromTestCase(TestMenuManagerMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestGameIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeQualityMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestMenuManagerDocumentation))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeStructure))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
