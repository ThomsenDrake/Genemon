"""
Held items catalog and effects.

Held items provide passive bonuses when equipped to creatures.
"""

import random
from typing import List, Dict
from .creature import HeldItem


# Held item effect types
EFFECT_POWER_BOOST = "power_boost"  # Boosts attack power by X%
EFFECT_TYPE_BOOST = "type_boost"  # Boosts moves of a specific type by X%
EFFECT_DEFENSE_BOOST = "defense_boost"  # Boosts defense by X%
EFFECT_SPEED_BOOST = "speed_boost"  # Boosts speed by X%
EFFECT_HP_BOOST = "hp_boost"  # Boosts max HP by X%
EFFECT_CRIT_BOOST = "crit_boost"  # Increases critical hit rate
EFFECT_STATUS_IMMUNE = "status_immune"  # Immune to specific status
EFFECT_ACCURACY_BOOST = "accuracy_boost"  # Boosts move accuracy
EFFECT_STAT_HEAL = "stat_heal"  # Restores HP each turn
EFFECT_FOCUS_BAND = "focus_band"  # Chance to survive fatal hit with 1 HP
EFFECT_CHOICE_BOOST = "choice_boost"  # Massive boost but locks into one move
EFFECT_LIFE_ORB = "life_orb"  # Boosts power but takes recoil damage
EFFECT_CONTACT_DAMAGE = "contact_damage"  # Damages attackers on contact moves
EFFECT_AUTO_STATUS = "auto_status"  # Auto-inflicts status on holder


# Global catalog cache (initialized lazily)
_HELD_ITEMS_CATALOG = None


def create_held_items_catalog() -> Dict[str, HeldItem]:
    """
    Create the catalog of all available held items.

    Returns:
        Dictionary mapping item names to HeldItem objects
    """
    items = {}

    # Power boosting items (20% boost)
    items["Muscle Band"] = HeldItem(
        name="Muscle Band",
        description="Boosts physical attack power by 20%",
        effect_type=EFFECT_POWER_BOOST,
        effect_value=1.2,
        effect_data={"stat": "attack"}
    )

    items["Wise Glasses"] = HeldItem(
        name="Wise Glasses",
        description="Boosts special attack power by 20%",
        effect_type=EFFECT_POWER_BOOST,
        effect_value=1.2,
        effect_data={"stat": "special"}
    )

    # Type-specific boost items (20% boost for that type)
    type_items = {
        "Charcoal": ("Flame", "fire"),
        "Mystic Water": ("Aqua", "water"),
        "Miracle Seed": ("Leaf", "plant"),
        "Never-Melt Ice": ("Frost", "ice"),
        "Black Belt": ("Brawl", "fighting"),
        "Poison Barb": ("Venom", "poison"),
        "Soft Sand": ("Terra", "ground"),
        "Sharp Beak": ("Sky", "flying"),
        "Twisted Spoon": ("Mind", "psychic"),
        "Silver Powder": ("Bug", "bug"),
        "Hard Stone": ("Metal", "rock"),
        "Spell Tag": ("Phantom", "ghost"),
        "Dragon Scale": ("Dragon", "dragon"),
        "Silk Scarf": ("Beast", "normal"),
        "Metal Coat": ("Steel", "steel"),
        "Dark Gem": ("Shade", "dark")
    }

    for item_name, (type_name, type_theme) in type_items.items():
        items[item_name] = HeldItem(
            name=item_name,
            description=f"Boosts {type_name}-type moves by 20%",
            effect_type=EFFECT_TYPE_BOOST,
            effect_value=1.2,
            effect_data={"type": type_name}
        )

    # Defensive items
    items["Assault Vest"] = HeldItem(
        name="Assault Vest",
        description="Greatly boosts special defense by 50%",
        effect_type=EFFECT_DEFENSE_BOOST,
        effect_value=1.5,
        effect_data={"stat": "special"}
    )

    items["Rocky Helmet"] = HeldItem(
        name="Rocky Helmet",
        description="Damages attackers when hit by contact moves",
        effect_type=EFFECT_CONTACT_DAMAGE,
        effect_value=0.16,  # 1/6 of attacker's max HP
        effect_data={"contact_damage": 0.16}
    )

    # Speed items
    items["Quick Claw"] = HeldItem(
        name="Quick Claw",
        description="20% chance to move first regardless of speed",
        effect_type=EFFECT_SPEED_BOOST,
        effect_value=1.0,
        effect_data={"priority_chance": 0.20}
    )

    items["Iron Ball"] = HeldItem(
        name="Iron Ball",
        description="Halves speed but grounds flying types",
        effect_type=EFFECT_SPEED_BOOST,
        effect_value=0.5,
        effect_data={"grounded": True}
    )

    # Critical hit items
    items["Scope Lens"] = HeldItem(
        name="Scope Lens",
        description="Increases critical hit rate by 1 stage",
        effect_type=EFFECT_CRIT_BOOST,
        effect_value=1.0,
        effect_data={"crit_stage": 1}
    )

    items["Razor Claw"] = HeldItem(
        name="Razor Claw",
        description="Sharply increases critical hit rate by 1 stage",
        effect_type=EFFECT_CRIT_BOOST,
        effect_value=1.0,
        effect_data={"crit_stage": 1}
    )

    # Status orbs (auto-inflict status on holder)
    items["Flame Orb"] = HeldItem(
        name="Flame Orb",
        description="Burns the holder at the end of each turn",
        effect_type=EFFECT_AUTO_STATUS,
        effect_value=1.0,
        effect_data={"status": "burn"}
    )

    items["Toxic Orb"] = HeldItem(
        name="Toxic Orb",
        description="Badly poisons the holder at the end of each turn",
        effect_type=EFFECT_AUTO_STATUS,
        effect_value=1.0,
        effect_data={"status": "poison"}
    )

    # Healing items
    items["Leftovers"] = HeldItem(
        name="Leftovers",
        description="Restores 1/16 of max HP each turn",
        effect_type=EFFECT_STAT_HEAL,
        effect_value=0.0625,  # 1/16
        effect_data={}
    )

    items["Shell Bell"] = HeldItem(
        name="Shell Bell",
        description="Restores 1/8 of damage dealt to opponent",
        effect_type=EFFECT_STAT_HEAL,
        effect_value=0.125,  # 1/8
        effect_data={"heal_on_damage": True}
    )

    # Survival items
    items["Focus Band"] = HeldItem(
        name="Focus Band",
        description="10% chance to survive a fatal hit with 1 HP",
        effect_type=EFFECT_FOCUS_BAND,
        effect_value=0.10,
        effect_data={}
    )

    items["Focus Sash"] = HeldItem(
        name="Focus Sash",
        description="Guarantees survival of fatal hit at full HP with 1 HP (one-time)",
        effect_type=EFFECT_FOCUS_BAND,
        effect_value=1.0,
        effect_data={"requires_full_hp": True, "one_time": True}
    )

    # Choice items (50% boost but lock into one move)
    items["Choice Band"] = HeldItem(
        name="Choice Band",
        description="Boosts Attack by 50% but locks into first move used",
        effect_type=EFFECT_CHOICE_BOOST,
        effect_value=1.5,
        effect_data={"stat": "attack", "locks_move": True}
    )

    items["Choice Specs"] = HeldItem(
        name="Choice Specs",
        description="Boosts Special by 50% but locks into first move used",
        effect_type=EFFECT_CHOICE_BOOST,
        effect_value=1.5,
        effect_data={"stat": "special", "locks_move": True}
    )

    items["Choice Scarf"] = HeldItem(
        name="Choice Scarf",
        description="Boosts Speed by 50% but locks into first move used",
        effect_type=EFFECT_CHOICE_BOOST,
        effect_value=1.5,
        effect_data={"stat": "speed", "locks_move": True}
    )

    # Life Orb (power boost with recoil)
    items["Life Orb"] = HeldItem(
        name="Life Orb",
        description="Boosts move power by 30% but takes 10% recoil damage",
        effect_type=EFFECT_LIFE_ORB,
        effect_value=1.3,
        effect_data={"recoil": 0.10}
    )

    # Expert Belt (super-effective bonus)
    items["Expert Belt"] = HeldItem(
        name="Expert Belt",
        description="Boosts super-effective moves by 20%",
        effect_type=EFFECT_POWER_BOOST,
        effect_value=1.2,
        effect_data={"only_super_effective": True}
    )

    return items


def get_random_held_item(rng: random.Random = None) -> HeldItem:
    """
    Get a random held item from the catalog.

    Args:
        rng: Random number generator (optional)

    Returns:
        Random HeldItem
    """
    if rng is None:
        rng = random.Random()

    catalog = create_held_items_catalog()
    item_name = rng.choice(list(catalog.keys()))
    return catalog[item_name]


def get_held_items_catalog() -> Dict[str, HeldItem]:
    """
    Get the cached held items catalog (lazy initialization).

    Returns:
        Dictionary mapping item names to HeldItem objects
    """
    global _HELD_ITEMS_CATALOG
    if _HELD_ITEMS_CATALOG is None:
        _HELD_ITEMS_CATALOG = create_held_items_catalog()
    return _HELD_ITEMS_CATALOG


def get_held_item_by_name(name: str) -> HeldItem:
    """
    Get a specific held item by name.

    Args:
        name: Name of the held item

    Returns:
        HeldItem if found, None otherwise
    """
    catalog = get_held_items_catalog()
    return catalog.get(name)


def get_type_boost_item(type_name: str) -> HeldItem:
    """
    Get the type-boosting held item for a specific type.

    Args:
        type_name: Type name (e.g., "Flame", "Aqua")

    Returns:
        HeldItem for that type, or None if not found
    """
    catalog = get_held_items_catalog()
    for item in catalog.values():
        if (item.effect_type == EFFECT_TYPE_BOOST and
            item.effect_data and
            item.effect_data.get("type") == type_name):
            return item
    return None
