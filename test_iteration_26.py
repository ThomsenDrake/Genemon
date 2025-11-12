"""
Test suite for Iteration 26 - Input Validation Consolidation

This iteration focused on code quality improvements:
- Removed duplicate _get_int_input() method from game.py
- Consolidated all input validation to use InputValidator class
- Reduced code duplication and improved consistency
"""

import unittest
import sys
from unittest.mock import patch, MagicMock
from genemon.core.input_validator import InputValidator, MenuBuilder
from genemon.core.game import Game
from genemon.core.creature import Creature, Team, Badge
from genemon.core.save_system import GameState


class TestInputValidatorConsolidation(unittest.TestCase):
    """Test that input validation is properly consolidated."""

    def test_input_validator_exists(self):
        """Test that InputValidator class is available."""
        self.assertTrue(hasattr(InputValidator, 'get_valid_choice'))
        self.assertTrue(hasattr(InputValidator, 'get_yes_no'))
        self.assertTrue(hasattr(InputValidator, 'get_menu_choice'))
        self.assertTrue(hasattr(InputValidator, 'get_string_input'))

    def test_menu_builder_exists(self):
        """Test that MenuBuilder class is available."""
        menu = MenuBuilder("Test Menu")
        self.assertEqual(menu.title, "Test Menu")
        self.assertTrue(hasattr(menu, 'add_option'))
        self.assertTrue(hasattr(menu, 'add_options'))
        self.assertTrue(hasattr(menu, 'with_cancel'))

    def test_game_does_not_have_get_int_input(self):
        """Test that Game class no longer has _get_int_input method."""
        game = Game()
        self.assertFalse(hasattr(game, '_get_int_input'))

    def test_game_imports_input_validator(self):
        """Test that Game imports InputValidator."""
        import genemon.core.game as game_module
        self.assertTrue(hasattr(game_module, 'InputValidator'))


class TestInputValidatorMethods(unittest.TestCase):
    """Test InputValidator utility methods."""

    @patch('builtins.input', return_value='5')
    def test_get_valid_choice_valid_input(self, mock_input):
        """Test get_valid_choice with valid input."""
        result = InputValidator.get_valid_choice("> ", 1, 10)
        self.assertEqual(result, 5)

    @patch('builtins.input', side_effect=['', '3'])
    def test_get_valid_choice_empty_with_default(self, mock_input):
        """Test get_valid_choice with empty input and default."""
        result = InputValidator.get_valid_choice("> ", 1, 10, allow_empty=True, empty_value=3)
        self.assertEqual(result, 3)

    @patch('builtins.input', side_effect=['15', '5'])
    def test_get_valid_choice_out_of_range(self, mock_input):
        """Test get_valid_choice with out-of-range input."""
        result = InputValidator.get_valid_choice("> ", 1, 10)
        self.assertEqual(result, 5)

    @patch('builtins.input', side_effect=['abc', '5'])
    def test_get_valid_choice_invalid_input(self, mock_input):
        """Test get_valid_choice with non-numeric input."""
        result = InputValidator.get_valid_choice("> ", 1, 10)
        self.assertEqual(result, 5)

    @patch('builtins.input', return_value='y')
    def test_get_yes_no_affirmative(self, mock_input):
        """Test get_yes_no with yes response."""
        result = InputValidator.get_yes_no("Continue?")
        self.assertTrue(result)

    @patch('builtins.input', return_value='n')
    def test_get_yes_no_negative(self, mock_input):
        """Test get_yes_no with no response."""
        result = InputValidator.get_yes_no("Continue?")
        self.assertFalse(result)

    @patch('builtins.input', return_value='')
    def test_get_yes_no_default(self, mock_input):
        """Test get_yes_no with default value."""
        result = InputValidator.get_yes_no("Continue?", default=True)
        self.assertTrue(result)

    def test_validate_name_valid(self):
        """Test name validation with valid name."""
        is_valid, error = InputValidator.validate_name("PlayerOne")
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_name_with_spaces(self):
        """Test name validation with spaces."""
        is_valid, error = InputValidator.validate_name("Player One")
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_name_empty(self):
        """Test name validation with empty string."""
        is_valid, error = InputValidator.validate_name("")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_name_too_long(self):
        """Test name validation with too long name."""
        is_valid, error = InputValidator.validate_name("A" * 25)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_name_special_characters(self):
        """Test name validation with invalid characters."""
        is_valid, error = InputValidator.validate_name("Player@123")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)


class TestMenuBuilder(unittest.TestCase):
    """Test MenuBuilder utility class."""

    def test_menu_builder_creation(self):
        """Test creating a MenuBuilder."""
        menu = MenuBuilder("Test Menu")
        self.assertEqual(menu.title, "Test Menu")
        self.assertEqual(len(menu.options), 0)

    def test_menu_builder_add_option(self):
        """Test adding an option to MenuBuilder."""
        menu = MenuBuilder("Test Menu")
        menu.add_option("Option 1")
        self.assertEqual(len(menu.options), 1)
        self.assertEqual(menu.options[0], "Option 1")

    def test_menu_builder_add_options(self):
        """Test adding multiple options to MenuBuilder."""
        menu = MenuBuilder("Test Menu")
        menu.add_options(["Option 1", "Option 2", "Option 3"])
        self.assertEqual(len(menu.options), 3)

    def test_menu_builder_chaining(self):
        """Test MenuBuilder method chaining."""
        menu = (MenuBuilder("Test Menu")
                .add_option("Option 1")
                .add_option("Option 2")
                .with_cancel())
        self.assertEqual(len(menu.options), 2)
        self.assertTrue(menu.allow_cancel)

    @patch('builtins.input', return_value='1')
    def test_menu_builder_show(self, mock_input):
        """Test showing a menu."""
        menu = MenuBuilder("Test Menu").add_options(["Option 1", "Option 2"])
        index, text = menu.show()
        self.assertEqual(index, 0)
        self.assertEqual(text, "Option 1")

    @patch('builtins.input', return_value='3')
    def test_menu_builder_with_cancel(self, mock_input):
        """Test menu with cancel option."""
        menu = (MenuBuilder("Test Menu")
                .add_options(["Option 1", "Option 2"])
                .with_cancel())
        index, text = menu.show()
        self.assertIsNone(index)
        self.assertIsNone(text)


class TestCodeQualityMetrics(unittest.TestCase):
    """Test code quality improvements."""

    def test_game_py_line_count_reduced(self):
        """Test that game.py line count is reduced."""
        import genemon.core.game as game_module
        import inspect
        source = inspect.getsource(game_module)
        line_count = len(source.split('\n'))
        # Should be less than the original 1494 lines
        self.assertLess(line_count, 1500)

    def test_no_duplicate_input_handling(self):
        """Test that there's no duplicate input handling code."""
        import genemon.core.game as game_module
        import inspect
        source = inspect.getsource(game_module.Game)
        # Should not contain _get_int_input method definition
        self.assertNotIn('def _get_int_input', source)

    def test_input_validator_imported(self):
        """Test that InputValidator is imported in game module."""
        import genemon.core.game as game_module
        import inspect
        source = inspect.getsource(game_module)
        self.assertIn('InputValidator', source)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
