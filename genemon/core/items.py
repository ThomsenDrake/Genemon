"""
Item system for Genemon.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict
from .creature import Creature, Move


class ItemType(Enum):
    """Types of items."""
    HEALING = "healing"          # Restores HP
    PP_RESTORE = "pp_restore"    # Restores PP
    STATUS_HEAL = "status_heal"  # Cures status effects
    CAPTURE = "capture"          # Capture balls
    BATTLE = "battle"            # Battle items (stat boost, etc.)
    TM = "tm"                    # Technical Machines (teach moves)


class ItemEffect(Enum):
    """Specific item effects."""
    HEAL_HP = "heal_hp"
    HEAL_HP_FULL = "heal_hp_full"
    RESTORE_PP = "restore_pp"
    RESTORE_PP_FULL = "restore_pp_full"
    CURE_STATUS = "cure_status"
    CURE_ALL_STATUS = "cure_all_status"
    CAPTURE = "capture"
    TEACH_MOVE = "teach_move"


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
    tm_move: Optional['Move'] = None  # For TM items, the move they teach (imported from creature module)

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

        elif self.item_type == ItemType.TM:
            if not self.tm_move:
                return False, "This TM has no move data!"

            # Check if creature can learn this TM
            if not creature.can_learn_tm(self.tm_move.name):
                return False, f"{creature.get_display_name()} cannot learn {self.tm_move.name}!"

            # Check if creature already knows this move
            if any(move.name == self.tm_move.name for move in creature.moves):
                return False, f"{creature.get_display_name()} already knows {self.tm_move.name}!"

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
            if creature.has_status():
                status_name = creature.status.value.capitalize()
                creature.cure_status()
                return f"{name}'s {status_name} was cured!"
            else:
                return f"{name} has no status to cure!"

        elif self.effect == ItemEffect.CURE_ALL_STATUS:
            if creature.has_status():
                status_name = creature.status.value.capitalize()
                creature.cure_status()
                return f"{name}'s {status_name} was cured!"
            else:
                return f"{name} has no status to cure!"

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


def _create_tm_moves() -> Dict[str, Move]:
    """Create all TM moves. Returns a dictionary of move_name -> Move."""
    return {
        # Universal TMs
        "Swift Strike": Move("Swift Strike", "Beast", 60, 100, 20, 20, "A swift, unavoidable strike."),
        "Mega Impact": Move("Mega Impact", "Beast", 90, 85, 10, 10, "A devastating tackle attack."),
        "Fury Slash": Move("Fury Slash", "Beast", 55, 95, 25, 25, "Slashes the foe with fury."),

        # Type-specific TMs
        "Flame Burst": Move("Flame Burst", "Flame", 75, 95, 15, 15, "A burst of searing flames."),
        "Inferno Blast": Move("Inferno Blast", "Flame", 95, 80, 10, 10, "An overwhelming inferno."),
        "Sacred Flame": Move("Sacred Flame", "Flame", 70, 100, 15, 15, "A mystical holy flame."),

        "Hydro Blast": Move("Hydro Blast", "Aqua", 75, 95, 15, 15, "A powerful water blast."),
        "Aqua Storm": Move("Aqua Storm", "Aqua", 85, 90, 12, 12, "A raging water storm."),
        "Tidal Wave": Move("Tidal Wave", "Aqua", 95, 85, 10, 10, "A massive tidal wave."),

        "Vine Storm": Move("Vine Storm", "Leaf", 75, 95, 15, 15, "Whips with vines fiercely."),
        "Petal Burst": Move("Petal Burst", "Leaf", 70, 100, 20, 20, "A burst of sharp petals."),
        "Solar Beam": Move("Solar Beam", "Leaf", 110, 90, 8, 8, "Gathers solar energy to attack."),

        "Thunder Blast": Move("Thunder Blast", "Volt", 80, 90, 15, 15, "A powerful thunderbolt."),
        "Volt Storm": Move("Volt Storm", "Volt", 90, 85, 10, 10, "A raging electrical storm."),
        "Electric Surge": Move("Electric Surge", "Volt", 70, 100, 18, 18, "An electric shockwave."),

        "Frost Beam": Move("Frost Beam", "Frost", 75, 95, 15, 15, "A freezing ice beam."),
        "Ice Storm": Move("Ice Storm", "Frost", 85, 90, 12, 12, "A blizzard of ice."),
        "Frozen Fury": Move("Frozen Fury", "Frost", 95, 85, 10, 10, "Unleashes frozen wrath."),

        "Earth Blast": Move("Earth Blast", "Terra", 75, 95, 15, 15, "Hurls rocks at the foe."),
        "Quake Storm": Move("Quake Storm", "Terra", 95, 85, 10, 10, "Causes a massive earthquake."),
        "Boulder Crush": Move("Boulder Crush", "Terra", 85, 90, 12, 12, "Crushes with boulders."),

        "Aero Blast": Move("Aero Blast", "Gale", 75, 95, 15, 15, "A cutting wind blast."),
        "Sky Storm": Move("Sky Storm", "Gale", 90, 85, 10, 10, "A powerful wind storm."),
        "Whirlwind": Move("Whirlwind", "Gale", 70, 100, 18, 18, "A swirling gust of wind."),

        "Toxic Blast": Move("Toxic Blast", "Toxin", 75, 95, 15, 15, "Sprays toxic poison."),
        "Poison Storm": Move("Poison Storm", "Toxin", 85, 90, 12, 12, "A storm of poison."),
        "Venom Strike": Move("Venom Strike", "Toxin", 70, 100, 18, 18, "Strikes with venom."),

        "Psychic Blast": Move("Psychic Blast", "Mind", 85, 90, 15, 15, "Uses psychic power."),
        "Mind Storm": Move("Mind Storm", "Mind", 95, 85, 10, 10, "Overwhelms the mind."),
        "Confusion Wave": Move("Confusion Wave", "Mind", 70, 100, 18, 18, "Confuses the target."),

        "Spirit Blast": Move("Spirit Blast", "Spirit", 75, 95, 15, 15, "A ghostly attack."),
        "Ghost Storm": Move("Ghost Storm", "Spirit", 90, 85, 10, 10, "A storm of spirits."),
        "Shadow Strike": Move("Shadow Strike", "Spirit", 70, 100, 18, 18, "Strikes from shadows."),

        "Wild Slash": Move("Wild Slash", "Beast", 70, 100, 20, 20, "A wild, feral slash."),
        "Feral Strike": Move("Feral Strike", "Beast", 80, 92, 15, 15, "A savage strike."),
        "Primal Fury": Move("Primal Fury", "Beast", 90, 88, 12, 12, "Unleashes primal rage."),

        "Power Punch": Move("Power Punch", "Brawl", 75, 95, 18, 18, "A powerful punch."),
        "Combat Strike": Move("Combat Strike", "Brawl", 85, 90, 15, 15, "A martial arts strike."),
        "Fighting Fury": Move("Fighting Fury", "Brawl", 95, 85, 10, 10, "Unleashes fighting spirit."),

        "Bug Blast": Move("Bug Blast", "Insect", 75, 95, 15, 15, "A swarm attack."),
        "Swarm Storm": Move("Swarm Storm", "Insect", 85, 90, 12, 12, "A massive swarm."),
        "Insect Fury": Move("Insect Fury", "Insect", 90, 88, 12, 12, "Insect rage unleashed."),

        "Steel Slash": Move("Steel Slash", "Metal", 75, 95, 18, 18, "Slashes with steel."),
        "Metal Storm": Move("Metal Storm", "Metal", 90, 85, 12, 12, "A storm of metal."),
        "Iron Impact": Move("Iron Impact", "Metal", 85, 90, 15, 15, "Impacts with iron force."),

        "Mystic Blast": Move("Mystic Blast", "Mystic", 75, 95, 15, 15, "A mystical attack."),
        "Fairy Storm": Move("Fairy Storm", "Mystic", 85, 90, 12, 12, "A storm of fairy magic."),
        "Magic Strike": Move("Magic Strike", "Mystic", 70, 100, 18, 18, "Strikes with magic."),

        "Dark Blast": Move("Dark Blast", "Shadow", 75, 95, 15, 15, "A blast of darkness."),
        "Shadow Storm": Move("Shadow Storm", "Shadow", 90, 85, 10, 10, "A storm of shadows."),
        "Void Strike": Move("Void Strike", "Shadow", 85, 90, 12, 12, "Strikes from the void."),

        # Weather-changing moves (NEW in v0.10.0)
        "Rain Dance": Move("Rain Dance", "Aqua", 0, 100, 5, 5, "Summons rain for 5 turns."),
        "Sunny Day": Move("Sunny Day", "Flame", 0, 100, 5, 5, "Summons harsh sunlight for 5 turns."),
        "Sandstorm": Move("Sandstorm", "Terra", 0, 100, 5, 5, "Summons a sandstorm for 5 turns."),
        "Hail": Move("Hail", "Frost", 0, 100, 5, 5, "Summons hail for 5 turns."),
    }


# Create TM moves
TM_MOVES = _create_tm_moves()


def _create_tms() -> Dict[str, Item]:
    """Create TM items."""
    tms = {}
    tm_number = 1

    # Group TMs by category for easier organization
    tm_groups = {
        "universal": ["Swift Strike", "Mega Impact", "Fury Slash"],
        "flame": ["Flame Burst", "Inferno Blast", "Sacred Flame"],
        "aqua": ["Hydro Blast", "Aqua Storm", "Tidal Wave"],
        "leaf": ["Vine Storm", "Petal Burst", "Solar Beam"],
        "volt": ["Thunder Blast", "Volt Storm", "Electric Surge"],
        "frost": ["Frost Beam", "Ice Storm", "Frozen Fury"],
        "terra": ["Earth Blast", "Quake Storm", "Boulder Crush"],
        "gale": ["Aero Blast", "Sky Storm", "Whirlwind"],
        "toxin": ["Toxic Blast", "Poison Storm", "Venom Strike"],
        "mind": ["Psychic Blast", "Mind Storm", "Confusion Wave"],
        "spirit": ["Spirit Blast", "Ghost Storm", "Shadow Strike"],
        "beast": ["Wild Slash", "Feral Strike", "Primal Fury"],
        "brawl": ["Power Punch", "Combat Strike", "Fighting Fury"],
        "insect": ["Bug Blast", "Swarm Storm", "Insect Fury"],
        "metal": ["Steel Slash", "Metal Storm", "Iron Impact"],
        "mystic": ["Mystic Blast", "Fairy Storm", "Magic Strike"],
        "shadow": ["Dark Blast", "Shadow Storm", "Void Strike"],
        "weather": ["Rain Dance", "Sunny Day", "Sandstorm", "Hail"],  # NEW in v0.10.0
    }

    for category, move_names in tm_groups.items():
        for move_name in move_names:
            if move_name in TM_MOVES:
                tm_id = f"tm{tm_number:02d}"
                tm_move = TM_MOVES[move_name]

                tms[tm_id] = Item(
                    id=tm_id,
                    name=f"TM{tm_number:02d} {move_name}",
                    description=f"Teaches {move_name} ({tm_move.type}-type, {tm_move.power} power)",
                    item_type=ItemType.TM,
                    effect=ItemEffect.TEACH_MOVE,
                    effect_value=0,
                    price=3000,  # TMs are expensive!
                    tm_move=tm_move
                )
                tm_number += 1

    return tms


# Add TMs to ITEMS
ITEMS.update(_create_tms())


def get_item(item_id: str) -> Optional[Item]:
    """Get an item by ID."""
    return ITEMS.get(item_id)


def get_all_items() -> dict:
    """Get all available items."""
    return ITEMS.copy()
