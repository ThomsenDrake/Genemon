"""
Input validation utility for consistent user input handling.

This module provides a centralized way to validate and process user input
across the game, reducing code duplication and improving error handling.
"""

from typing import Optional, List, Tuple, Callable
from .exceptions import InvalidInputError, InvalidChoiceError


class InputValidator:
    """
    Utility class for validating and processing user input.

    This class provides methods for common input validation patterns used
    throughout the game, such as menu choices, yes/no prompts, and numeric
    input validation.
    """

    @staticmethod
    def get_valid_choice(
        prompt: str,
        min_value: int,
        max_value: int,
        allow_empty: bool = False,
        empty_value: any = None,
        invalid_message: str = None
    ) -> any:
        """
        Get a valid numeric choice from the user within a range.

        Args:
            prompt: The prompt to display to the user
            min_value: Minimum valid value (inclusive)
            max_value: Maximum valid value (inclusive)
            allow_empty: Whether empty input is allowed
            empty_value: Value to return for empty input
            invalid_message: Custom message for invalid input

        Returns:
            The validated choice (int) or empty_value if empty input allowed

        Raises:
            InvalidChoiceError: If input is invalid and allow_empty is False
        """
        while True:
            try:
                user_input = input(prompt).strip()

                # Handle empty input
                if not user_input:
                    if allow_empty:
                        return empty_value
                    if invalid_message:
                        print(invalid_message)
                    else:
                        print("Please enter a value.")
                    continue

                # Convert to integer
                choice = int(user_input)

                # Validate range
                if min_value <= choice <= max_value:
                    return choice
                else:
                    if invalid_message:
                        print(invalid_message)
                    else:
                        print(f"Please enter a number between {min_value} and {max_value}.")

            except ValueError:
                if invalid_message:
                    print(invalid_message)
                else:
                    print("Invalid input. Please enter a number.")

    @staticmethod
    def get_yes_no(
        prompt: str,
        default: Optional[bool] = None,
        yes_values: List[str] = None,
        no_values: List[str] = None
    ) -> bool:
        """
        Get a yes/no response from the user.

        Args:
            prompt: The prompt to display
            default: Default value if user presses enter (None for no default)
            yes_values: List of strings that count as "yes" (default: ['y', 'yes'])
            no_values: List of strings that count as "no" (default: ['n', 'no'])

        Returns:
            True for yes, False for no
        """
        if yes_values is None:
            yes_values = ['y', 'yes']
        if no_values is None:
            no_values = ['n', 'no']

        # Add default indicator to prompt
        if default is not None:
            default_str = "[Y/n]" if default else "[y/N]"
            full_prompt = f"{prompt} {default_str}: "
        else:
            full_prompt = f"{prompt} [y/n]: "

        while True:
            user_input = input(full_prompt).strip().lower()

            # Handle empty input with default
            if not user_input and default is not None:
                return default

            # Check yes/no values
            if user_input in yes_values:
                return True
            elif user_input in no_values:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    @staticmethod
    def get_menu_choice(
        prompt: str,
        options: List[str],
        allow_cancel: bool = False,
        cancel_text: str = "Cancel",
        show_numbers: bool = True
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Display a menu and get user's choice.

        Args:
            prompt: The prompt to display before the menu
            options: List of menu option strings
            allow_cancel: Whether to add a cancel option
            cancel_text: Text for cancel option
            show_numbers: Whether to show option numbers

        Returns:
            Tuple of (index, option_text) where index is 0-based.
            Returns (None, None) if cancelled.
        """
        # Display menu
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            if show_numbers:
                print(f"{i}. {option}")
            else:
                print(f"  {option}")

        if allow_cancel:
            cancel_index = len(options) + 1
            if show_numbers:
                print(f"{cancel_index}. {cancel_text}")
            else:
                print(f"  {cancel_text}")

        # Get choice
        max_choice = len(options) + (1 if allow_cancel else 0)
        choice = InputValidator.get_valid_choice(
            "\nYour choice: ",
            1,
            max_choice,
            invalid_message=f"Please enter a number between 1 and {max_choice}."
        )

        # Handle cancel
        if allow_cancel and choice == cancel_index:
            return None, None

        # Return 0-based index and option text
        return choice - 1, options[choice - 1]

    @staticmethod
    def get_string_input(
        prompt: str,
        min_length: int = 1,
        max_length: int = 100,
        allow_empty: bool = False,
        validator: Optional[Callable[[str], bool]] = None,
        validator_message: str = "Invalid input."
    ) -> str:
        """
        Get string input with validation.

        Args:
            prompt: The prompt to display
            min_length: Minimum string length
            max_length: Maximum string length
            allow_empty: Whether empty input is allowed
            validator: Optional custom validation function
            validator_message: Message to show if validator fails

        Returns:
            Validated string input
        """
        while True:
            user_input = input(prompt).strip()

            # Handle empty input
            if not user_input:
                if allow_empty:
                    return user_input
                print(f"Please enter at least {min_length} character(s).")
                continue

            # Check length
            if len(user_input) < min_length:
                print(f"Input must be at least {min_length} character(s) long.")
                continue

            if len(user_input) > max_length:
                print(f"Input must be at most {max_length} character(s) long.")
                continue

            # Custom validation
            if validator and not validator(user_input):
                print(validator_message)
                continue

            return user_input

    @staticmethod
    def get_confirmation(
        action: str,
        details: str = None,
        default_no: bool = True
    ) -> bool:
        """
        Get confirmation for an important action.

        Args:
            action: The action to confirm (e.g., "delete save file")
            details: Optional additional details
            default_no: Whether default is no (safer for destructive actions)

        Returns:
            True if confirmed, False otherwise
        """
        print(f"\n⚠️  CONFIRMATION REQUIRED")
        print(f"Action: {action}")
        if details:
            print(f"Details: {details}")

        return InputValidator.get_yes_no(
            "Are you sure you want to continue?",
            default=not default_no
        )

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a player or save file name.

        Args:
            name: The name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check length
        if len(name) < 1:
            return False, "Name cannot be empty."

        if len(name) > 20:
            return False, "Name must be 20 characters or less."

        # Check for alphanumeric and spaces only
        if not all(c.isalnum() or c.isspace() or c in "-_" for c in name):
            return False, "Name can only contain letters, numbers, spaces, hyphens, and underscores."

        # Check for at least one letter
        if not any(c.isalpha() for c in name):
            return False, "Name must contain at least one letter."

        return True, None

    @staticmethod
    def pause_for_input(message: str = "Press Enter to continue..."):
        """
        Pause execution until user presses enter.

        Args:
            message: Message to display
        """
        input(message)

    @staticmethod
    def safe_int_input(
        prompt: str,
        default: int = 0,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Get integer input with fallback to default on error.

        Args:
            prompt: The prompt to display
            default: Default value if conversion fails
            min_value: Optional minimum value
            max_value: Optional maximum value

        Returns:
            Validated integer or default
        """
        try:
            value = int(input(prompt).strip())

            if min_value is not None and value < min_value:
                print(f"Value too low, using minimum: {min_value}")
                return min_value

            if max_value is not None and value > max_value:
                print(f"Value too high, using maximum: {max_value}")
                return max_value

            return value

        except ValueError:
            print(f"Invalid input, using default: {default}")
            return default


class MenuBuilder:
    """
    Helper class for building consistent menus throughout the game.

    This class provides a fluent interface for creating menus with
    consistent formatting and behavior.
    """

    def __init__(self, title: str):
        """
        Initialize menu builder.

        Args:
            title: The menu title
        """
        self.title = title
        self.options: List[str] = []
        self.allow_cancel = False
        self.cancel_text = "Cancel"

    def add_option(self, text: str) -> 'MenuBuilder':
        """
        Add an option to the menu.

        Args:
            text: Option text

        Returns:
            Self for chaining
        """
        self.options.append(text)
        return self

    def add_options(self, texts: List[str]) -> 'MenuBuilder':
        """
        Add multiple options to the menu.

        Args:
            texts: List of option texts

        Returns:
            Self for chaining
        """
        self.options.extend(texts)
        return self

    def with_cancel(self, cancel_text: str = "Cancel") -> 'MenuBuilder':
        """
        Enable cancel option.

        Args:
            cancel_text: Text for cancel option

        Returns:
            Self for chaining
        """
        self.allow_cancel = True
        self.cancel_text = cancel_text
        return self

    def show(self) -> Tuple[Optional[int], Optional[str]]:
        """
        Display the menu and get user choice.

        Returns:
            Tuple of (index, option_text) or (None, None) if cancelled
        """
        return InputValidator.get_menu_choice(
            self.title,
            self.options,
            allow_cancel=self.allow_cancel,
            cancel_text=self.cancel_text
        )

    def show_and_get_index(self) -> Optional[int]:
        """
        Display the menu and get only the index.

        Returns:
            Index (0-based) or None if cancelled
        """
        index, _ = self.show()
        return index
