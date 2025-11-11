"""
Type system with effectiveness calculations.
"""

from typing import Dict, List


# Define custom types for this game (not using Pokemon names)
TYPES = [
    "Flame",      # Fire-like
    "Aqua",       # Water-like
    "Leaf",       # Grass-like
    "Volt",       # Electric-like
    "Frost",      # Ice-like
    "Terra",      # Ground/Rock-like
    "Gale",       # Flying-like
    "Toxin",      # Poison-like
    "Mind",       # Psychic-like
    "Spirit",     # Ghost-like
    "Beast",      # Normal-like
    "Brawl",      # Fighting-like
    "Insect",     # Bug-like
    "Metal",      # Steel-like
    "Mystic",     # Fairy-like
    "Shadow"      # Dark-like
]


# Type effectiveness chart: {attacking_type: {defending_type: multiplier}}
# 2.0 = super effective, 0.5 = not very effective, 0.0 = no effect
TYPE_EFFECTIVENESS: Dict[str, Dict[str, float]] = {
    "Flame": {
        "Leaf": 2.0, "Frost": 2.0, "Insect": 2.0, "Metal": 2.0,
        "Flame": 0.5, "Aqua": 0.5, "Terra": 0.5, "Spirit": 0.5
    },
    "Aqua": {
        "Flame": 2.0, "Terra": 2.0,
        "Aqua": 0.5, "Leaf": 0.5, "Frost": 0.5, "Spirit": 0.5
    },
    "Leaf": {
        "Aqua": 2.0, "Terra": 2.0,
        "Flame": 0.5, "Leaf": 0.5, "Toxin": 0.5, "Gale": 0.5,
        "Insect": 0.5, "Metal": 0.5
    },
    "Volt": {
        "Aqua": 2.0, "Gale": 2.0,
        "Volt": 0.5, "Leaf": 0.5, "Terra": 0.0
    },
    "Frost": {
        "Leaf": 2.0, "Terra": 2.0, "Gale": 2.0,
        "Flame": 0.5, "Aqua": 0.5, "Frost": 0.5, "Metal": 0.5
    },
    "Terra": {
        "Flame": 2.0, "Volt": 2.0, "Toxin": 2.0, "Metal": 2.0,
        "Leaf": 0.5, "Insect": 0.5, "Gale": 0.0
    },
    "Gale": {
        "Leaf": 2.0, "Brawl": 2.0, "Insect": 2.0,
        "Volt": 0.5, "Terra": 0.5, "Metal": 0.5
    },
    "Toxin": {
        "Leaf": 2.0, "Mystic": 2.0,
        "Toxin": 0.5, "Terra": 0.5, "Spirit": 0.5, "Metal": 0.0
    },
    "Mind": {
        "Brawl": 2.0, "Toxin": 2.0,
        "Mind": 0.5, "Metal": 0.5, "Shadow": 0.0
    },
    "Spirit": {
        "Mind": 2.0, "Spirit": 2.0,
        "Shadow": 0.5, "Beast": 0.0
    },
    "Beast": {
        "Spirit": 0.0, "Terra": 0.5, "Metal": 0.5
    },
    "Brawl": {
        "Beast": 2.0, "Frost": 2.0, "Terra": 2.0, "Metal": 2.0, "Shadow": 2.0,
        "Toxin": 0.5, "Gale": 0.5, "Mind": 0.5, "Insect": 0.5,
        "Mystic": 0.5, "Spirit": 0.0
    },
    "Insect": {
        "Leaf": 2.0, "Mind": 2.0, "Mystic": 2.0,
        "Flame": 0.5, "Brawl": 0.5, "Toxin": 0.5, "Gale": 0.5,
        "Spirit": 0.5, "Metal": 0.5
    },
    "Metal": {
        "Frost": 2.0, "Terra": 2.0, "Mystic": 2.0,
        "Flame": 0.5, "Aqua": 0.5, "Volt": 0.5, "Metal": 0.5
    },
    "Mystic": {
        "Brawl": 2.0, "Shadow": 2.0,
        "Flame": 0.5, "Toxin": 0.5, "Metal": 0.5
    },
    "Shadow": {
        "Mind": 2.0, "Spirit": 2.0,
        "Brawl": 0.5, "Mystic": 0.5, "Shadow": 0.5
    }
}


def get_effectiveness(attack_type: str, defending_types: List[str]) -> float:
    """
    Calculate type effectiveness multiplier.

    Args:
        attack_type: The type of the attacking move
        defending_types: List of types of the defending creature

    Returns:
        Multiplier (e.g., 2.0 for super effective, 0.5 for not very effective)
    """
    if attack_type not in TYPE_EFFECTIVENESS:
        return 1.0

    multiplier = 1.0
    for def_type in defending_types:
        type_chart = TYPE_EFFECTIVENESS[attack_type]
        if def_type in type_chart:
            multiplier *= type_chart[def_type]

    return multiplier


def get_type_color(type_name: str) -> str:
    """Get a color code for a type (for UI purposes)."""
    colors = {
        "Flame": "red",
        "Aqua": "blue",
        "Leaf": "green",
        "Volt": "yellow",
        "Frost": "cyan",
        "Terra": "brown",
        "Gale": "lightblue",
        "Toxin": "purple",
        "Mind": "pink",
        "Spirit": "violet",
        "Beast": "gray",
        "Brawl": "orange",
        "Insect": "lime",
        "Metal": "silver",
        "Mystic": "magenta",
        "Shadow": "darkgray"
    }
    return colors.get(type_name, "white")
