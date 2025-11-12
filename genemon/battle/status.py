"""
Battle status effect management.

This module handles all status effects (Burn, Poison, Paralysis, Sleep, Frozen)
and their application, removal, and turn-by-turn processing.
"""

import random
from typing import Optional, Tuple
from ..core.creature import Creature, Move, StatusEffect
from ..core.held_items import EFFECT_AUTO_STATUS


class StatusManager:
    """
    Manages all status effects during battles.

    This class is responsible for:
    - Applying status effects to creatures
    - Processing status damage at end of turn
    - Checking if creatures can move (paralysis, sleep, frozen)
    - Handling status immunity from abilities
    - Managing auto-status items (Flame Orb, Toxic Orb)
    """

    # Status effect damage percentages
    BURN_DAMAGE_PERCENT = 6.25  # 1/16 of max HP per turn
    POISON_DAMAGE_PERCENT = 12.5  # 1/8 of max HP per turn
    HAIL_DAMAGE_PERCENT = 6.25  # 1/16 of max HP per turn
    SANDSTORM_DAMAGE_PERCENT = 6.25  # 1/16 of max HP per turn

    # Status effect chance multipliers
    PARALYSIS_MOVE_CHANCE = 25  # 25% chance to be unable to move
    FROZEN_THAW_CHANCE = 20  # 20% chance to thaw each turn
    SLEEP_MIN_TURNS = 1
    SLEEP_MAX_TURNS = 3

    def __init__(self):
        """Initialize the status manager."""
        pass

    def apply_move_status(
        self,
        move: Move,
        attacker: Creature,
        defender: Creature,
        log_messages: list
    ) -> bool:
        """
        Apply status effect from a move if applicable.

        Args:
            move: The move being used
            attacker: The attacking creature
            defender: The defending creature
            log_messages: List to append status messages to

        Returns:
            True if status was applied, False otherwise
        """
        if not move.status_effect or not move.status_chance:
            return False

        # Check if defender already has a status
        if defender.status != "":
            return False

        # Check for status immunity from abilities
        if self._is_immune_to_status(defender, move.status_effect):
            log_messages.append(f"{defender.get_display_name()} is immune to {move.status_effect}!")
            return False

        # Roll for status chance
        if random.randint(1, 100) <= move.status_chance:
            return self.apply_status(defender, move.status_effect, log_messages)

        return False

    def apply_status(
        self,
        creature: Creature,
        status: str,
        log_messages: list
    ) -> bool:
        """
        Apply a status effect to a creature.

        Args:
            creature: The creature to apply status to
            status: The status effect name (Burn, Poison, etc.)
            log_messages: List to append status messages to

        Returns:
            True if status was applied, False otherwise
        """
        # Check if creature already has a status
        if creature.status != "":
            return False

        # Check for status immunity
        if self._is_immune_to_status(creature, status):
            log_messages.append(f"{creature.get_display_name()} is immune to {status}!")
            return False

        # Apply the status
        creature.status = status

        # Initialize sleep counter if asleep
        if status == "Sleep":
            creature.sleep_turns = random.randint(self.SLEEP_MIN_TURNS, self.SLEEP_MAX_TURNS)

        # Log the status application
        status_messages = {
            "Burn": f"{creature.get_display_name()} was burned!",
            "Poison": f"{creature.get_display_name()} was poisoned!",
            "Paralysis": f"{creature.get_display_name()} was paralyzed!",
            "Sleep": f"{creature.get_display_name()} fell asleep!",
            "Frozen": f"{creature.get_display_name()} was frozen solid!"
        }
        log_messages.append(status_messages.get(status, f"{creature.get_display_name()} was affected!"))

        return True

    def _is_immune_to_status(self, creature: Creature, status: str) -> bool:
        """
        Check if a creature is immune to a status effect.

        Args:
            creature: The creature to check
            status: The status effect name

        Returns:
            True if immune, False otherwise
        """
        if not creature.species.ability:
            return False

        ability_name = creature.species.ability.name

        # Immunity abilities
        immunity_map = {
            "Immunity": ["Poison"],
            "Water Veil": ["Burn"],
            "Limber": ["Paralysis"],
            "Insomnia": ["Sleep"],
            "Vital Spirit": ["Sleep"],
            "Magma Armor": ["Frozen"],
            "Leaf Guard": ["Burn", "Poison", "Paralysis", "Sleep", "Frozen"],  # In certain weather
        }

        if ability_name in immunity_map:
            return status in immunity_map[ability_name]

        return False

    def process_status_damage(
        self,
        creature: Creature,
        log_messages: list
    ):
        """
        Process end-of-turn status damage.

        Args:
            creature: The creature with status
            log_messages: List to append damage messages to
        """
        if not creature.status or creature.is_fainted():
            return

        status = creature.status
        creature_name = creature.get_display_name()

        if status == "Burn":
            damage = max(1, int(creature.max_hp * self.BURN_DAMAGE_PERCENT / 100))
            creature.take_damage(damage)
            log_messages.append(f"{creature_name} is hurt by its burn! ({damage} damage)")

        elif status == "Poison":
            damage = max(1, int(creature.max_hp * self.POISON_DAMAGE_PERCENT / 100))
            creature.take_damage(damage)
            log_messages.append(f"{creature_name} is hurt by poison! ({damage} damage)")

    def can_creature_move(self, creature: Creature) -> Tuple[bool, Optional[str]]:
        """
        Check if a creature can move based on its status.

        Args:
            creature: The creature to check

        Returns:
            Tuple of (can_move, message)
            - can_move: True if creature can move, False otherwise
            - message: Message explaining why creature can't move (if applicable)
        """
        if not creature.status:
            return True, None

        status = creature.status
        creature_name = creature.get_display_name()

        if status == "Sleep":
            if creature.sleep_turns > 0:
                creature.sleep_turns -= 1
                if creature.sleep_turns == 0:
                    creature.status = ""  # Wake up
                    return True, f"{creature_name} woke up!"
                else:
                    return False, f"{creature_name} is fast asleep!"
            else:
                creature.status = ""  # Wake up
                return True, f"{creature_name} woke up!"

        elif status == "Paralysis":
            # 25% chance to be unable to move
            if random.randint(1, 100) <= self.PARALYSIS_MOVE_CHANCE:
                return False, f"{creature_name} is paralyzed and can't move!"

        elif status == "Frozen":
            # 20% chance to thaw each turn
            if random.randint(1, 100) <= self.FROZEN_THAW_CHANCE:
                creature.status = ""  # Thaw out
                return True, f"{creature_name} thawed out!"
            else:
                return False, f"{creature_name} is frozen solid!"

        return True, None

    def apply_auto_status_items(
        self,
        creature: Creature,
        log_messages: list
    ):
        """
        Apply auto-status effects from held items (Flame Orb, Toxic Orb).

        Args:
            creature: The creature holding the item
            log_messages: List to append status messages to
        """
        if not creature.held_item or creature.held_item.effect_type != EFFECT_AUTO_STATUS:
            return

        # Don't apply if creature already has a status
        if creature.status != "":
            return

        item_name = creature.held_item.name
        creature_name = creature.get_display_name()

        if item_name == "Flame Orb":
            self.apply_status(creature, "Burn", log_messages)
            # Override message for clarity
            if creature.status == "Burn":
                log_messages[-1] = f"{creature_name} was burned by its Flame Orb!"

        elif item_name == "Toxic Orb":
            self.apply_status(creature, "Poison", log_messages)
            # Override message for clarity
            if creature.status == "Poison":
                log_messages[-1] = f"{creature_name} was poisoned by its Toxic Orb!"

    def cure_status(self, creature: Creature, log_messages: list):
        """
        Cure a creature's status effect.

        Args:
            creature: The creature to cure
            log_messages: List to append cure messages to
        """
        if creature.status == "":
            return

        old_status = creature.status
        creature.status = ""
        creature.sleep_turns = 0

        log_messages.append(f"{creature.get_display_name()}'s {old_status} was cured!")

    def get_speed_modifier(self, creature: Creature) -> float:
        """
        Get the speed multiplier for a creature based on status.

        Args:
            creature: The creature to check

        Returns:
            Speed multiplier (1.0 for normal, 0.25 for paralyzed)
        """
        if creature.status == "Paralysis":
            return 0.25  # Paralysis reduces speed by 75%
        return 1.0

    def get_attack_modifier(self, creature: Creature) -> float:
        """
        Get the attack multiplier for a creature based on status.

        Args:
            creature: The creature to check

        Returns:
            Attack multiplier (1.0 for normal, 0.5 for burned)
        """
        if creature.status == "Burn":
            return 0.5  # Burn halves physical attack
        return 1.0
