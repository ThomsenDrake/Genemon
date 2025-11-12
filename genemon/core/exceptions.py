"""
Custom exception hierarchy for Genemon.

This module defines custom exceptions for better error handling throughout
the game, making it easier to catch and handle specific error conditions.
"""


class GenemonError(Exception):
    """
    Base exception for all Genemon-specific errors.

    All custom exceptions in the game should inherit from this base class.
    """

    def __init__(self, message: str, context: dict = None):
        """
        Initialize a Genemon error.

        Args:
            message: Human-readable error message
            context: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


# ==============================================================================
# BATTLE SYSTEM EXCEPTIONS
# ==============================================================================

class BattleError(GenemonError):
    """Base class for battle-related errors."""
    pass


class InvalidBattleStateError(BattleError):
    """Raised when battle is in an invalid state."""
    pass


class NoActivCreatureError(BattleError):
    """Raised when no active creature is available for battle."""
    pass


class InvalidMoveError(BattleError):
    """Raised when attempting to use an invalid move."""
    pass


class NoPPError(BattleError):
    """Raised when a move has no PP remaining."""
    pass


# ==============================================================================
# CREATURE SYSTEM EXCEPTIONS
# ==============================================================================

class CreatureError(GenemonError):
    """Base class for creature-related errors."""
    pass


class InvalidCreatureError(CreatureError):
    """Raised when creature data is invalid."""
    pass


class CreatureFaintedError(CreatureError):
    """Raised when trying to use a fainted creature."""
    pass


class NoMovesError(CreatureError):
    """Raised when a creature has no moves."""
    pass


# ==============================================================================
# SAVE/LOAD EXCEPTIONS
# ==============================================================================

class SaveError(GenemonError):
    """Base class for save/load errors."""
    pass


class SaveFileNotFoundError(SaveError):
    """Raised when save file cannot be found."""
    pass


class SaveFileCorruptedError(SaveError):
    """Raised when save file is corrupted or invalid."""
    pass


class SaveFileVersionError(SaveError):
    """Raised when save file version is incompatible."""
    pass


# ==============================================================================
# GENERATION EXCEPTIONS
# ==============================================================================

class GenerationError(GenemonError):
    """Base class for creature generation errors."""
    pass


class InvalidGenerationSeedError(GenerationError):
    """Raised when generation seed is invalid."""
    pass


class GenerationFailedError(GenerationError):
    """Raised when creature generation fails."""
    pass


# ==============================================================================
# GAME STATE EXCEPTIONS
# ==============================================================================

class GameStateError(GenemonError):
    """Base class for game state errors."""
    pass


class InvalidGameStateError(GameStateError):
    """Raised when game state is invalid or inconsistent."""
    pass


class GameNotInitializedError(GameStateError):
    """Raised when game operations are attempted before initialization."""
    pass


# ==============================================================================
# WORLD/MAP EXCEPTIONS
# ==============================================================================

class WorldError(GenemonError):
    """Base class for world/map errors."""
    pass


class InvalidLocationError(WorldError):
    """Raised when location is invalid or doesn't exist."""
    pass


class InvalidMovementError(WorldError):
    """Raised when attempted movement is invalid."""
    pass


# ==============================================================================
# ITEM SYSTEM EXCEPTIONS
# ==============================================================================

class ItemError(GenemonError):
    """Base class for item-related errors."""
    pass


class InvalidItemError(ItemError):
    """Raised when item is invalid or doesn't exist."""
    pass


class CannotUseItemError(ItemError):
    """Raised when item cannot be used in current context."""
    pass


class InsufficientFundsError(ItemError):
    """Raised when player doesn't have enough money to purchase item."""
    pass


# ==============================================================================
# VALIDATION EXCEPTIONS
# ==============================================================================

class ValidationError(GenemonError):
    """Base class for validation errors."""
    pass


class InvalidInputError(ValidationError):
    """Raised when user input is invalid."""
    pass


class InvalidChoiceError(ValidationError):
    """Raised when user choice is out of valid range."""
    pass


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def format_error_with_context(error: GenemonError) -> str:
    """
    Format an error with its context for logging.

    Args:
        error: The error to format

    Returns:
        Formatted error string with context
    """
    error_type = type(error).__name__
    if error.context:
        context_items = []
        for key, value in error.context.items():
            context_items.append(f"  {key}: {value}")
        context_str = "\n".join(context_items)
        return f"{error_type}: {error.message}\nContext:\n{context_str}"
    return f"{error_type}: {error.message}"


def raise_with_context(exception_class: type, message: str, **context):
    """
    Raise an exception with context information.

    Args:
        exception_class: The exception class to raise
        message: The error message
        **context: Keyword arguments for error context

    Example:
        raise_with_context(
            InvalidBattleStateError,
            "No active creatures available",
            player_team_size=0,
            opponent_team_size=1
        )
    """
    raise exception_class(message, context=context)
