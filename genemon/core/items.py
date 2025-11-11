"""
Item system for Genemon.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .creature import Creature


class ItemType(Enum):
    """Types of items."""
    HEALING = "healing"          # Restores HP
    PP_RESTORE = "pp_restore"    # Restores PP
    STATUS_HEAL = "status_heal"  # Cures status effects
    CAPTURE = "capture"          # Capture balls
    BATTLE = "battle"            # Battle items (stat boost, etc.)


class ItemEffect(Enum):
    """Specific item effects."""
    HEAL_HP = "heal_hp"
    HEAL_HP_FULL = "heal_hp_full"
    RESTORE_PP = "restore_pp"
    RESTORE_PP_FULL = "restore_pp_full"
    CURE_STATUS = "cure_status"
    CURE_ALL_STATUS = "cure_all_status"
    CAPTURE = "capture"


@dataclass
class Item:
    """
    Represents an item that can be used on creatures.
    """

    id: str
    name: str
    description: str
    item_type: ItemType
    effect: ItemEffect
    effect_value: int = 0  # Amount to heal, PP to restore, etc.
    price: int = 0  # Cost in shops

    def can_use_on(self, creature: Creature, in_battle: bool = False) -> tuple[bool, str]:
        """
        Check if item can be used on a creature.

        Args:
            creature: Target creature
            in_battle: Whether currently in battle

        Returns:
            (can_use, message) tuple
        """
        if creature.is_fainted():
            # Only revival items can be used on fainted creatures (not implemented yet)
            return False, f"{creature.get_display_name()} has fainted!"

        if self.item_type == ItemType.HEALING:
            if creature.current_hp >= creature.max_hp:
                return False, f"{creature.get_display_name()} already has full HP!"
            return True, ""

        elif self.item_type == ItemType.PP_RESTORE:
            # Check if any moves need PP restoration
            if all(move.pp >= move.max_pp for move in creature.moves):
                return False, f"{creature.get_display_name()}'s moves are already at full PP!"
            return True, ""

        elif self.item_type == ItemType.STATUS_HEAL:
            # Will be used when status effects are implemented
            return True, ""

        elif self.item_type == ItemType.CAPTURE:
            if not in_battle:
                return False, "Can only use capture balls in battle!"
            return True, ""

        return False, "Cannot use this item!"

    def use(self, creature: Creature) -> str:
        """
        Use the item on a creature.

        Args:
            creature: Target creature

        Returns:
            Message describing the effect
        """
        name = creature.get_display_name()

        if self.effect == ItemEffect.HEAL_HP:
            before_hp = creature.current_hp
            creature.heal(self.effect_value)
            healed = creature.current_hp - before_hp
            return f"{name} restored {healed} HP!"

        elif self.effect == ItemEffect.HEAL_HP_FULL:
            before_hp = creature.current_hp
            creature.heal()
            healed = creature.current_hp - before_hp
            return f"{name} was fully healed! (+{healed} HP)"

        elif self.effect == ItemEffect.RESTORE_PP:
            creature.restore_pp(self.effect_value)
            return f"{name}'s PP was restored!"

        elif self.effect == ItemEffect.RESTORE_PP_FULL:
            creature.restore_pp()
            return f"{name}'s PP was fully restored!"

        elif self.effect == ItemEffect.CURE_STATUS:
            # Will be implemented with status effects
            return f"{name}'s status was cured!"

        elif self.effect == ItemEffect.CURE_ALL_STATUS:
            # Will be implemented with status effects
            return f"{name}'s status was fully restored!"

        return "The item had no effect."

    def to_dict(self) -> dict:
        """Convert item to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type.value,
            'effect': self.effect.value,
            'effect_value': self.effect_value,
            'price': self.price
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Create item from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            item_type=ItemType(data['item_type']),
            effect=ItemEffect(data['effect']),
            effect_value=data.get('effect_value', 0),
            price=data.get('price', 0)
        )


# Define all available items
ITEMS = {
    # Healing items
    'potion': Item(
        id='potion',
        name='Potion',
        description='Restores 20 HP',
        item_type=ItemType.HEALING,
        effect=ItemEffect.HEAL_HP,
        effect_value=20,
        price=100
    ),
    'super_potion': Item(
        id='super_potion',
        name='Super Potion',
        description='Restores 50 HP',
        item_type=ItemType.HEALING,
        effect=ItemEffect.HEAL_HP,
        effect_value=50,
        price=300
    ),
    'hyper_potion': Item(
        id='hyper_potion',
        name='Hyper Potion',
        description='Restores 120 HP',
        item_type=ItemType.HEALING,
        effect=ItemEffect.HEAL_HP,
        effect_value=120,
        price=600
    ),
    'full_heal_potion': Item(
        id='full_heal_potion',
        name='Full Heal',
        description='Fully restores HP',
        item_type=ItemType.HEALING,
        effect=ItemEffect.HEAL_HP_FULL,
        effect_value=0,
        price=1000
    ),

    # PP restore items
    'ether': Item(
        id='ether',
        name='Ether',
        description='Restores 10 PP to all moves',
        item_type=ItemType.PP_RESTORE,
        effect=ItemEffect.RESTORE_PP,
        effect_value=10,
        price=500
    ),
    'max_ether': Item(
        id='max_ether',
        name='Max Ether',
        description='Fully restores PP to all moves',
        item_type=ItemType.PP_RESTORE,
        effect=ItemEffect.RESTORE_PP_FULL,
        effect_value=0,
        price=1000
    ),

    # Status healing items
    'antidote': Item(
        id='antidote',
        name='Antidote',
        description='Cures poison',
        item_type=ItemType.STATUS_HEAL,
        effect=ItemEffect.CURE_STATUS,
        effect_value=0,
        price=200
    ),
    'awakening': Item(
        id='awakening',
        name='Awakening',
        description='Cures sleep',
        item_type=ItemType.STATUS_HEAL,
        effect=ItemEffect.CURE_STATUS,
        effect_value=0,
        price=200
    ),
    'burn_heal': Item(
        id='burn_heal',
        name='Burn Heal',
        description='Cures burn',
        item_type=ItemType.STATUS_HEAL,
        effect=ItemEffect.CURE_STATUS,
        effect_value=0,
        price=200
    ),
    'paralyze_heal': Item(
        id='paralyze_heal',
        name='Paralyze Heal',
        description='Cures paralysis',
        item_type=ItemType.STATUS_HEAL,
        effect=ItemEffect.CURE_STATUS,
        effect_value=0,
        price=200
    ),
    'full_restore': Item(
        id='full_restore',
        name='Full Restore',
        description='Fully restores HP and cures all status',
        item_type=ItemType.STATUS_HEAL,
        effect=ItemEffect.CURE_ALL_STATUS,
        effect_value=0,
        price=1500
    ),

    # Capture items
    'capture_ball': Item(
        id='capture_ball',
        name='Capture Ball',
        description='A ball for capturing wild creatures',
        item_type=ItemType.CAPTURE,
        effect=ItemEffect.CAPTURE,
        effect_value=1,
        price=200
    ),
}


def get_item(item_id: str) -> Optional[Item]:
    """Get an item by ID."""
    return ITEMS.get(item_id)


def get_all_items() -> dict:
    """Get all available items."""
    return ITEMS.copy()
