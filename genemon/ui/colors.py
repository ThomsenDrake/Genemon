"""
Terminal color support using ANSI escape codes.
"""

import sys
import os


class TerminalColors:
    """
    ANSI color codes for terminal output.
    Provides both foreground and background colors, plus text formatting.
    """

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'

    # Bright foreground colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Text formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'

    # Reset
    RESET = '\033[0m'
    RESET_COLOR = '\033[39m'
    RESET_BG = '\033[49m'

    @staticmethod
    def is_supported() -> bool:
        """
        Check if terminal supports ANSI color codes.

        Returns:
            True if colors are supported, False otherwise
        """
        # Check if output is a TTY
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False

        # Check for NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False

        # Check for FORCE_COLOR environment variable
        if os.environ.get('FORCE_COLOR'):
            return True

        # Windows CMD doesn't support ANSI by default (unless Windows 10+)
        if sys.platform == 'win32':
            # Try to enable ANSI support on Windows 10+
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except (AttributeError, OSError):
                # AttributeError: ctypes.windll doesn't exist on non-Windows
                # OSError: SetConsoleMode failed
                return False

        # Unix-like systems generally support ANSI
        return True


class ColorSupport:
    """
    Wrapper class that automatically disables colors if not supported.
    """

    _enabled = None

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if color support is enabled."""
        if cls._enabled is None:
            cls._enabled = TerminalColors.is_supported()
        return cls._enabled

    @classmethod
    def enable(cls):
        """Force enable color support."""
        cls._enabled = True

    @classmethod
    def disable(cls):
        """Force disable color support."""
        cls._enabled = False

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """
        Colorize text with the given color code.

        Args:
            text: Text to colorize
            color: ANSI color code

        Returns:
            Colorized text (or plain text if colors disabled)
        """
        if cls.is_enabled():
            return f"{color}{text}{TerminalColors.RESET}"
        return text


# Type-specific colors
TYPE_COLORS_ANSI = {
    "Flame": TerminalColors.BRIGHT_RED,
    "Aqua": TerminalColors.BRIGHT_BLUE,
    "Leaf": TerminalColors.BRIGHT_GREEN,
    "Volt": TerminalColors.BRIGHT_YELLOW,
    "Frost": TerminalColors.CYAN,
    "Terra": TerminalColors.YELLOW,
    "Gale": TerminalColors.WHITE,
    "Toxin": TerminalColors.MAGENTA,
    "Mind": TerminalColors.BRIGHT_MAGENTA,
    "Spirit": TerminalColors.MAGENTA,
    "Beast": TerminalColors.GRAY,
    "Brawl": TerminalColors.RED,
    "Insect": TerminalColors.GREEN,
    "Metal": TerminalColors.WHITE,
    "Mystic": TerminalColors.BRIGHT_CYAN,
    "Shadow": TerminalColors.GRAY,
}


def colored(text: str, color: str) -> str:
    """
    Colorize text with the given color.

    Args:
        text: Text to colorize
        color: ANSI color code from TerminalColors

    Returns:
        Colorized text (or plain text if colors disabled)
    """
    return ColorSupport.colorize(text, color)


def colored_type(type_name: str) -> str:
    """
    Colorize a type name with its associated color.

    Args:
        type_name: Name of the type (e.g., "Flame", "Aqua")

    Returns:
        Colorized type name
    """
    color = TYPE_COLORS_ANSI.get(type_name, TerminalColors.WHITE)
    return colored(type_name, color)


def colored_hp(current: int, maximum: int) -> str:
    """
    Colorize HP display based on percentage.

    Args:
        current: Current HP
        maximum: Maximum HP

    Returns:
        Colorized HP string
    """
    if maximum == 0:
        return colored(f"{current}/{maximum}", TerminalColors.GRAY)

    percent = current / maximum

    if percent > 0.5:
        color = TerminalColors.BRIGHT_GREEN
    elif percent > 0.2:
        color = TerminalColors.BRIGHT_YELLOW
    else:
        color = TerminalColors.BRIGHT_RED

    return colored(f"{current}/{maximum}", color)


def colored_status(status: str) -> str:
    """
    Colorize status effect name.

    Args:
        status: Status effect name

    Returns:
        Colorized status name
    """
    status_colors = {
        "burn": TerminalColors.BRIGHT_RED,
        "poison": TerminalColors.MAGENTA,
        "paralysis": TerminalColors.BRIGHT_YELLOW,
        "sleep": TerminalColors.CYAN,
        "freeze": TerminalColors.BRIGHT_CYAN,
    }

    color = status_colors.get(status.lower(), TerminalColors.WHITE)
    return colored(status.upper(), color)


def bold(text: str) -> str:
    """Make text bold."""
    return colored(text, TerminalColors.BOLD)


def underline(text: str) -> str:
    """Underline text."""
    return colored(text, TerminalColors.UNDERLINE)
