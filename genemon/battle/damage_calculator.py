"""
Damage calculation system for battles.

This module handles all damage-related calculations including:
- Base damage formulas
- Type effectiveness and STAB
- Critical hits
- Weather modifiers
- Held item damage modifiers
- Ability damage modifiers
"""

import random
from typing import TYPE_CHECKING
from ..core.creature import Creature, Move, StatusEffect
from ..creatures.types import get_effectiveness
from ..core.held_items import (
    EFFECT_POWER_BOOST, EFFECT_TYPE_BOOST, EFFECT_DEFENSE_BOOST,
    EFFECT_LIFE_ORB, EFFECT_CHOICE_BOOST
)

if TYPE_CHECKING:
    from .engine import Weather


class DamageCalculator:
    """
    Handles all damage calculation logic for battles.

    This class is responsible for computing damage values based on:
    - Attacker and defender stats
    - Move properties
    - Critical hits
    - Weather conditions
    - Held items
    - Abilities
    """

    def __init__(self):
        """Initialize the damage calculator."""
        pass

    def calculate_damage(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        is_critical: bool,
        weather: 'Weather',
        attacker_stat_modifier: callable,
        defender_stat_modifier: callable
    ) -> int:
        """
        Calculate damage for an attack using a simplified Gen 1 formula.

        Args:
            attacker: Attacking creature
            defender: Defending creature
            move: Move being used
            is_critical: Whether this is a critical hit
            weather: Current weather condition
            attacker_stat_modifier: Function to get attacker's modified stats
            defender_stat_modifier: Function to get defender's modified stats

        Returns:
            Damage amount (minimum 1)
        """
        # Base damage calculation
        level = attacker.level
        power = move.power

        # Check for Unaware ability (ignores opponent's stat stages)
        attacker_has_unaware = (attacker.species.ability and
                                attacker.species.ability.effect_type == "ignore_stat_stages")
        defender_has_unaware = (defender.species.ability and
                                defender.species.ability.effect_type == "ignore_stat_stages")

        # Get attack stat (defender's Unaware ignores attacker's Attack stages)
        if defender_has_unaware:
            # Calculate attack without stat stages
            attack_stat = attacker.attack
            # Apply ability modifiers only
            attack_modifier = self._get_ability_attack_modifier(attacker)
            attack_stat = int(attack_stat * attack_modifier)
        else:
            # Normal: includes stat stages
            attack_stat = attacker_stat_modifier(attacker, "attack")

        # Get defense stat (attacker's Unaware ignores defender's Defense stages)
        if attacker_has_unaware:
            # Calculate defense without stat stages
            defense_stat = defender.defense
            # Apply ability modifiers only
            defense_modifier = self._get_ability_defense_modifier(defender)
            defense_stat = int(defense_stat * defense_modifier)
        else:
            # Normal: includes stat stages
            defense_stat = defender_stat_modifier(defender, "defense")

        # Burn reduces attack by 50%
        if attacker.status == StatusEffect.BURN:
            attack_stat = int(attack_stat * 0.5)

        # Base damage formula (simplified Gen 1 style)
        damage = ((2 * level / 5 + 2) * power * attack_stat / defense_stat / 50) + 2

        # Type effectiveness
        effectiveness = get_effectiveness(move.type, defender.species.types)
        damage *= effectiveness

        # STAB (Same Type Attack Bonus)
        if move.type in attacker.species.types:
            damage *= 1.5

        # Critical hit (2x damage multiplier, 3x with Sniper ability)
        if is_critical:
            if attacker.species.ability and attacker.species.ability.name == "Sniper":
                damage *= 3.0  # Sniper boosts crit damage to 3x
            else:
                damage *= 2.0  # Normal crit is 2x

        # Weather effects
        damage = self._apply_weather_modifiers(damage, move.type, weather)

        # Held item effects (before random factor for consistency)
        damage = self._apply_held_item_modifiers(attacker, defender, move, damage, effectiveness)

        # Random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)

        # Apply ability-based damage modifiers
        damage = self._apply_ability_modifiers(attacker, defender, move, int(damage))

        return max(1, int(damage))

    def check_critical_hit(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move
    ) -> bool:
        """
        Check if an attack results in a critical hit.

        Args:
            attacker: Attacking creature
            defender: Defending creature
            move: Move being used

        Returns:
            True if critical hit occurs
        """
        # Check if defender has crit-blocking abilities
        if defender.species.ability:
            if defender.species.ability.name in ["Battle Armor", "Shell Armor"]:
                return False

        # Base critical hit rate by stage
        crit_stage = move.crit_rate if hasattr(move, 'crit_rate') else 0

        # Super Luck increases crit stage by 1
        if attacker.species.ability and attacker.species.ability.name == "Super Luck":
            crit_stage += 1

        # Held items (Scope Lens, Razor Claw) increase crit stage
        if attacker.held_item and attacker.held_item.effect_type == "crit_boost":
            crit_boost = attacker.held_item.effect_data.get("crit_stage", 1)
            crit_stage += crit_boost

        # Critical hit chances by stage
        if crit_stage >= 2:
            # Always crit
            return True
        elif crit_stage == 1:
            # High crit rate: 12.5% (1/8)
            return random.randint(1, 8) == 1
        else:
            # Base crit rate: 6.25% (1/16)
            return random.randint(1, 16) == 1

    def _apply_weather_modifiers(self, damage: float, move_type: str, weather: 'Weather') -> float:
        """
        Apply weather-based damage modifiers.

        Args:
            damage: Base damage amount
            move_type: Type of the move
            weather: Current weather condition

        Returns:
            Modified damage amount
        """
        # Import here to avoid circular dependency
        from .engine import Weather

        if weather == Weather.RAIN:
            if move_type == "Aqua":
                damage *= 1.5  # Rain boosts Aqua moves
            elif move_type == "Flame":
                damage *= 0.5  # Rain weakens Flame moves
        elif weather == Weather.SUN:
            if move_type == "Flame":
                damage *= 1.5  # Sun boosts Flame moves
            elif move_type == "Aqua":
                damage *= 0.5  # Sun weakens Aqua moves

        return damage

    def _apply_held_item_modifiers(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        damage: float,
        effectiveness: float
    ) -> float:
        """
        Apply held item damage modifiers.

        Args:
            attacker: Attacking creature
            defender: Defending creature
            move: Move being used
            damage: Current damage amount
            effectiveness: Type effectiveness multiplier

        Returns:
            Modified damage amount
        """
        if not attacker.held_item:
            return damage

        item = attacker.held_item
        effect_type = item.effect_type

        # Type-boosting items (Charcoal, Mystic Water, etc.) - 1.2x boost
        if effect_type == EFFECT_TYPE_BOOST:
            boost_type = item.effect_data.get("type")
            if boost_type == move.type:
                damage *= 1.2

        # Power-boosting items (Muscle Band, Wise Glasses) - 1.1x boost
        elif effect_type == EFFECT_POWER_BOOST:
            boost_category = item.effect_data.get("category")
            if boost_category == "physical":
                damage *= 1.1

        # Choice items (Band/Specs/Scarf) - 1.5x boost
        elif effect_type == EFFECT_CHOICE_BOOST:
            damage *= 1.5

        # Life Orb - 1.3x boost (recoil handled elsewhere)
        elif effect_type == EFFECT_LIFE_ORB:
            damage *= 1.3

        # Expert Belt - 1.2x boost on super effective moves
        elif item.name == "Expert Belt":
            if effectiveness > 1.0:
                damage *= 1.2

        return damage

    def _apply_ability_modifiers(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        damage: int
    ) -> int:
        """
        Apply ability-based damage modifiers.

        Args:
            attacker: Attacking creature
            defender: Defending creature
            move: Move being used
            damage: Current damage amount

        Returns:
            Modified damage amount
        """
        # Attacker abilities that boost damage
        if attacker.species.ability:
            ability_name = attacker.species.ability.name

            # Pure Power / Huge Power doubles Attack stat
            if ability_name in ["Pure Power", "Huge Power"]:
                damage = int(damage * 1.5)  # Approximate since Attack already doubled in stat calc

            # Guts boosts damage by 50% when statused
            elif ability_name == "Guts" and attacker.status != StatusEffect.NONE:
                damage = int(damage * 1.5)

            # Technician boosts weak moves (<=60 power) by 50%
            elif ability_name == "Technician" and move.power <= 60:
                damage = int(damage * 1.5)

            # Sheer Force boosts moves with secondary effects by 30%
            elif ability_name == "Sheer Force" and (move.status_effect or move.stat_changes):
                damage = int(damage * 1.3)

            # Iron Fist boosts punching moves by 20%
            elif ability_name == "Iron Fist" and "Punch" in move.name:
                damage = int(damage * 1.2)

        # Defender abilities that reduce damage
        if defender.species.ability:
            ability_name = defender.species.ability.name

            # Thick Fat halves Flame/Frost damage
            if ability_name == "Thick Fat" and move.type in ["Flame", "Frost"]:
                damage = int(damage * 0.5)

            # Marvel Scale boosts Defense when statused
            elif ability_name == "Marvel Scale" and defender.status != StatusEffect.NONE:
                damage = int(damage * 0.67)  # ~33% reduction

            # Multiscale halves damage at full HP
            elif ability_name == "Multiscale" and defender.hp == defender.max_hp:
                damage = int(damage * 0.5)

            # Filter/Solid Rock reduce super effective damage
            elif ability_name in ["Filter", "Solid Rock"]:
                effectiveness = get_effectiveness(move.type, defender.species.types)
                if effectiveness > 1.0:
                    damage = int(damage * 0.75)

        return damage

    def _get_ability_attack_modifier(self, creature: Creature) -> float:
        """
        Get attack stat modifier from ability (without stat stages).

        Args:
            creature: Creature to check

        Returns:
            Attack multiplier
        """
        if not creature.species.ability:
            return 1.0

        ability_name = creature.species.ability.name

        # Pure Power / Huge Power double Attack
        if ability_name in ["Pure Power", "Huge Power"]:
            return 2.0

        # Hustle increases Attack by 50%
        elif ability_name == "Hustle":
            return 1.5

        return 1.0

    def _get_ability_defense_modifier(self, creature: Creature) -> float:
        """
        Get defense stat modifier from ability (without stat stages).

        Args:
            creature: Creature to check

        Returns:
            Defense multiplier
        """
        if not creature.species.ability:
            return 1.0

        # Marvel Scale boosts Defense when statused
        if creature.species.ability.name == "Marvel Scale" and creature.status != StatusEffect.NONE:
            return 1.5

        return 1.0
