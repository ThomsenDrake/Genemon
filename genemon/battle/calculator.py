"""
Battle damage calculation and type effectiveness logic.

This module handles all damage calculations, critical hits, and effectiveness
checks for the battle system.
"""

import random
from typing import Tuple
from ..core.creature import Creature, Move
from ..creatures.types import get_effectiveness
from ..core.held_items import (
    EFFECT_POWER_BOOST, EFFECT_TYPE_BOOST, EFFECT_DEFENSE_BOOST,
    EFFECT_CRIT_BOOST, EFFECT_LIFE_ORB, EFFECT_CHOICE_BOOST
)


class BattleCalculator:
    """
    Handles all damage calculations for battles.

    This class is responsible for:
    - Type effectiveness calculations
    - Critical hit determination
    - Damage formula application
    - Held item damage modifiers
    - Stat stage multipliers
    - Weather damage modifiers
    """

    # Critical hit rate constants
    BASE_CRIT_RATE = 6.25  # Base 1/16 chance (6.25%)
    HIGH_CRIT_RATE = 12.5  # Moves with high crit rate (12.5%)
    CRIT_DAMAGE_MULTIPLIER = 2.0  # Critical hits do 2x damage
    SNIPER_CRIT_MULTIPLIER = 3.0  # Sniper ability makes crits do 3x

    # Stat stage multiplier lookup table
    # Stages range from -6 to +6, with 0 being neutral (1.0x)
    STAT_STAGE_MULTIPLIERS = {
        -6: 0.25,   # 2/8
        -5: 0.286,  # 2/7
        -4: 0.333,  # 2/6
        -3: 0.4,    # 2/5
        -2: 0.5,    # 2/4
        -1: 0.667,  # 2/3
        0: 1.0,     # 2/2
        1: 1.5,     # 3/2
        2: 2.0,     # 4/2
        3: 2.5,     # 5/2
        4: 3.0,     # 6/2
        5: 3.5,     # 7/2
        6: 4.0,     # 8/2
    }

    def __init__(self):
        """Initialize the battle calculator."""
        pass

    def calculate_damage(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        is_critical: bool,
        weather: str,
        attacker_stat_stages: dict,
        defender_stat_stages: dict,
        attacker_stat_mods: dict,
        defender_stat_mods: dict
    ) -> int:
        """
        Calculate damage dealt by a move.

        Args:
            attacker: The attacking creature
            defender: The defending creature
            move: The move being used
            is_critical: Whether this is a critical hit
            weather: Current weather condition
            attacker_stat_stages: Attacker's stat stage modifiers (-6 to +6)
            defender_stat_stages: Defender's stat stage modifiers (-6 to +6)
            attacker_stat_mods: Attacker's ability-based stat multipliers
            defender_stat_mods: Defender's ability-based stat multipliers

        Returns:
            Damage amount (integer)
        """
        # Base damage formula: ((2 * Level / 5 + 2) * Power * Attack/Defense) / 50 + 2

        # Get effective attack and defense stats
        attack_stat, defense_stat = self._get_effective_stats(
            attacker, defender, move, is_critical,
            attacker_stat_stages, defender_stat_stages,
            attacker_stat_mods, defender_stat_mods
        )

        # Base damage calculation
        level_factor = (2 * attacker.level / 5 + 2)
        damage = (level_factor * move.power * attack_stat / defense_stat) / 50 + 2

        # Apply STAB (Same Type Attack Bonus) - 1.5x if move type matches creature type
        stab = 1.5 if move.type in attacker.species.types else 1.0
        damage *= stab

        # Apply type effectiveness
        effectiveness = get_effectiveness(move.type, defender.species.types)
        damage *= effectiveness

        # Apply critical hit multiplier
        if is_critical:
            # Check for Sniper ability
            if attacker.species.ability and attacker.species.ability.name == "Sniper":
                damage *= self.SNIPER_CRIT_MULTIPLIER
            else:
                damage *= self.CRIT_DAMAGE_MULTIPLIER

        # Apply random factor (85-100%)
        random_factor = random.uniform(0.85, 1.0)
        damage *= random_factor

        # Apply weather modifiers
        damage = self._apply_weather_modifiers(damage, move, weather)

        # Apply held item modifiers
        damage = self._apply_held_item_modifiers(damage, attacker, defender, move, effectiveness)

        # Apply ability damage modifiers
        damage = self._apply_ability_modifiers(damage, attacker, defender, move)

        # Ensure minimum damage of 1
        return max(1, int(damage))

    def _get_effective_stats(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        is_critical: bool,
        attacker_stat_stages: dict,
        defender_stat_stages: dict,
        attacker_stat_mods: dict,
        defender_stat_mods: dict
    ) -> Tuple[float, float]:
        """
        Get effective attack and defense stats with all modifiers applied.

        Returns:
            Tuple of (effective_attack, effective_defense)
        """
        # Determine which stats to use based on move category
        if move.category == "physical":
            attack_base = attacker.attack
            defense_base = defender.defense
            attack_stage_key = "attack"
            defense_stage_key = "defense"
        else:  # special
            attack_base = attacker.special
            defense_base = defender.defense  # Using defense for special defense too
            attack_stage_key = "special"
            defense_stage_key = "defense"

        # Apply stat stages
        attack_stage = attacker_stat_stages.get(attack_stage_key, 0)
        defense_stage = defender_stat_stages.get(defense_stage_key, 0)

        # Critical hits ignore positive defense stages and negative attack stages
        if is_critical:
            if attack_stage < 0:
                attack_stage = 0
            if defense_stage > 0:
                defense_stage = 0

        attack_multiplier = self.STAT_STAGE_MULTIPLIERS.get(attack_stage, 1.0)
        defense_multiplier = self.STAT_STAGE_MULTIPLIERS.get(defense_stage, 1.0)

        # Apply stat stage multipliers
        effective_attack = attack_base * attack_multiplier
        effective_defense = defense_base * defense_multiplier

        # Apply ability-based stat modifiers
        effective_attack *= attacker_stat_mods.get(attack_stage_key, 1.0)
        effective_defense *= defender_stat_mods.get(defense_stage_key, 1.0)

        # Apply status effect modifiers
        if attacker.status == "Burn" and move.category == "physical":
            effective_attack *= 0.5  # Burn halves physical attack

        return effective_attack, effective_defense

    def _apply_weather_modifiers(self, damage: float, move: Move, weather: str) -> float:
        """Apply weather-based damage modifiers."""
        if weather == "rain":
            if move.type == "Aqua":
                damage *= 1.5  # Rain boosts Water moves
            elif move.type == "Flame":
                damage *= 0.5  # Rain weakens Fire moves
        elif weather == "sun":
            if move.type == "Flame":
                damage *= 1.5  # Sun boosts Fire moves
            elif move.type == "Aqua":
                damage *= 0.5  # Sun weakens Water moves

        return damage

    def _apply_held_item_modifiers(
        self,
        damage: float,
        attacker: Creature,
        defender: Creature,
        move: Move,
        effectiveness: float
    ) -> float:
        """Apply held item damage modifiers."""
        if not attacker.held_item:
            return damage

        item = attacker.held_item

        # Type boost items (e.g., Charcoal for Flame, Mystic Water for Aqua)
        if item.effect_type == EFFECT_TYPE_BOOST and item.effect_value == move.type:
            damage *= 1.2  # 20% boost for matching type

        # Power boost items
        if item.effect_type == EFFECT_POWER_BOOST:
            if item.name == "Expert Belt" and effectiveness > 1.0:
                damage *= 1.2  # Expert Belt boosts super-effective moves
            elif item.name in ["Muscle Band", "Wise Glasses"]:
                # Muscle Band for physical, Wise Glasses for special
                if (item.name == "Muscle Band" and move.category == "physical") or \
                   (item.name == "Wise Glasses" and move.category == "special"):
                    damage *= 1.1  # 10% boost

        # Choice items (Band/Specs/Scarf)
        if item.effect_type == EFFECT_CHOICE_BOOST:
            if item.name == "Choice Band" and move.category == "physical":
                damage *= 1.5  # 50% boost to physical moves
            elif item.name == "Choice Specs" and move.category == "special":
                damage *= 1.5  # 50% boost to special moves

        # Life Orb
        if item.effect_type == EFFECT_LIFE_ORB:
            damage *= 1.3  # 30% boost (recoil handled separately)

        return damage

    def _apply_ability_modifiers(
        self,
        damage: float,
        attacker: Creature,
        defender: Creature,
        move: Move
    ) -> float:
        """Apply ability-based damage modifiers."""
        # Attacker abilities
        if attacker.species.ability:
            ability_name = attacker.species.ability.name

            # Guts boosts Attack when statused (handled in stat calculation)
            # Technician boosts low-power moves
            if ability_name == "Technician" and move.power <= 60:
                damage *= 1.5

            # Sheer Force removes secondary effects but boosts power
            if ability_name == "Sheer Force" and (move.status_effect or move.stat_changes):
                damage *= 1.3

        # Defender abilities
        if defender.species.ability:
            ability_name = defender.species.ability.name

            # Filter reduces super-effective damage
            if ability_name == "Filter" and get_effectiveness(move.type, defender.species.types) > 1.0:
                damage *= 0.75

            # Solid Rock reduces super-effective damage
            if ability_name == "Solid Rock" and get_effectiveness(move.type, defender.species.types) > 1.0:
                damage *= 0.75

        return damage

    def check_critical_hit(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move
    ) -> bool:
        """
        Determine if an attack is a critical hit.

        Args:
            attacker: The attacking creature
            defender: The defending creature
            move: The move being used

        Returns:
            True if critical hit, False otherwise
        """
        # Check for abilities that prevent critical hits
        if defender.species.ability and defender.species.ability.name in ["Battle Armor", "Shell Armor"]:
            return False  # These abilities block critical hits

        # Base critical hit rate
        crit_rate = self.BASE_CRIT_RATE

        # High-crit moves (moves with certain keywords)
        high_crit_keywords = ["Slash", "Claw", "Strike", "Razor"]
        if any(keyword in move.name for keyword in high_crit_keywords):
            crit_rate = self.HIGH_CRIT_RATE

        # Super Luck ability increases crit rate
        if attacker.species.ability and attacker.species.ability.name == "Super Luck":
            crit_rate *= 2  # Double the crit rate

        # Crit-boosting items (Scope Lens, Razor Claw)
        if attacker.held_item and attacker.held_item.effect_type == EFFECT_CRIT_BOOST:
            crit_rate *= 1.5  # 50% increase to crit rate

        # Roll for critical hit
        return random.random() * 100 < crit_rate

    def get_stat_stage_multiplier(self, stages: int) -> float:
        """
        Get the multiplier for a given stat stage.

        Args:
            stages: Stat stage from -6 to +6

        Returns:
            Multiplier value
        """
        return self.STAT_STAGE_MULTIPLIERS.get(max(-6, min(6, stages)), 1.0)
