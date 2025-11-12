"""
Shiny creature utilities.
Handles shiny status determination and display.
"""

import random
from typing import Optional
from ..core.creature import Creature, CreatureSpecies


# Shiny encounter rate: 1/4096 (same as modern Pokemon games)
SHINY_RATE = 4096


def roll_shiny(rng: Optional[random.Random] = None) -> bool:
    """
    Roll for shiny status.

    Args:
        rng: Optional random number generator for deterministic results

    Returns:
        True if shiny, False otherwise (1/4096 chance)
    """
    if rng is None:
        rng = random

    return rng.randint(1, SHINY_RATE) == 1


def create_creature_with_shiny_check(
    species: CreatureSpecies,
    level: int,
    rng: Optional[random.Random] = None
) -> Creature:
    """
    Create a creature instance with automatic shiny checking.

    Args:
        species: The creature species
        level: Starting level
        rng: Optional random number generator

    Returns:
        Creature instance with is_shiny set based on random roll
    """
    is_shiny = roll_shiny(rng)

    creature = Creature(
        species=species,
        level=level,
        is_shiny=is_shiny
    )

    return creature


def get_shiny_indicator(creature: Creature) -> str:
    """
    Get a visual indicator for shiny status.

    Args:
        creature: The creature to check

    Returns:
        String with shiny indicator (sparkle symbol) or empty string
    """
    if creature.is_shiny:
        return " ✨"  # Sparkle emoji for shiny
    return ""


def get_shiny_text(creature: Creature) -> str:
    """
    Get descriptive text for shiny status.

    Args:
        creature: The creature to check

    Returns:
        String describing shiny status
    """
    if creature.is_shiny:
        return " (SHINY!)"
    return ""
