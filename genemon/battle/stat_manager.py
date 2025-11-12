"""
Battle stat stage management system.

This module handles all temporary battle stat modifications including:
- Stat stage changes (-6 to +6)
- Ability-based stat modifiers
- Stat stage reset on switch
- Modified stat calculations
"""

from typing import Dict
from ..core.creature import Creature


class BattleStatManager:
    """
    Manages temporary stat stages and modifiers during battles.

    Stat stages range from -6 to +6 and affect stats by multipliers:
    - Stage -6: 0.25x (25% of base)
    - Stage 0: 1.0x (normal)
    - Stage +6: 4.0x (400% of base)
    """

    def __init__(self):
        """Initialize stat stage tracking."""
        # Stat stages for player and opponent (-6 to +6)
        self.player_stat_stages: Dict[str, int] = {
            "attack": 0,
            "defense": 0,
            "speed": 0,
            "special": 0,
            "accuracy": 0,
            "evasion": 0
        }

        self.opponent_stat_stages: Dict[str, int] = {
            "attack": 0,
            "defense": 0,
            "speed": 0,
            "special": 0,
            "accuracy": 0,
            "evasion": 0
        }

        # Ability-based stat modifiers (cached)
        self.player_stat_mods: Dict[str, float] = {}
        self.opponent_stat_mods: Dict[str, float] = {}

    def get_stat_stage_multiplier(self, stage: int) -> float:
        """
        Get the stat multiplier for a given stage.

        Uses the standard competitive formula:
        multiplier = (2 + max(0, stage)) / (2 + max(0, -stage))

        Args:
            stage: Stat stage from -6 to +6

        Returns:
            Multiplier value:
            - Stage -6: 0.25x (25%)
            - Stage -3: 0.4x (40%)
            - Stage 0: 1.0x (100%)
            - Stage +3: 2.5x (250%)
            - Stage +6: 4.0x (400%)
        """
        if stage >= 0:
            return (2 + stage) / 2.0
        else:
            return 2.0 / (2 - stage)

    def modify_stat_stage(
        self,
        creature: Creature,
        is_player: bool,
        stat: str,
        stages: int,
        battle_log: 'BattleLog'
    ) -> bool:
        """
        Modify a creature's stat stage.

        Args:
            creature: The creature to modify
            is_player: True if player's creature, False for opponent
            stat: Stat to modify ("attack", "defense", "speed", "special", "accuracy", "evasion")
            stages: Number of stages to change (positive or negative)
            battle_log: Battle log for messages

        Returns:
            True if stat was changed, False if already at limit
        """
        stat_stages = self.player_stat_stages if is_player else self.opponent_stat_stages

        if stat not in stat_stages:
            return False

        # Check for abilities that affect stat stage changes
        ability = creature.species.ability
        ability_modifier = 1
        ability_inverts = False

        if ability:
            # Simple - doubles stat stage changes
            if ability.effect_type == "double_stat_changes":
                ability_modifier = 2
            # Contrary - inverts stat stage changes
            elif ability.effect_type == "invert_stat_changes":
                ability_inverts = True

        # Apply ability modifiers
        if ability_inverts:
            stages = -stages
        if ability_modifier != 1:
            stages *= ability_modifier

        # Calculate new stage (clamped to -6 to +6)
        old_stage = stat_stages[stat]
        new_stage = max(-6, min(6, old_stage + stages))
        actual_change = new_stage - old_stage

        # If no change, stat is at limit
        if actual_change == 0:
            creature_name = creature.get_display_name()
            # Check if trying to raise or lower
            if stages > 0:
                battle_log.add(f"{creature_name}'s {stat.capitalize()} won't go any higher!")
            else:
                battle_log.add(f"{creature_name}'s {stat.capitalize()} won't go any lower!")
            return False

        # Update the stage
        stat_stages[stat] = new_stage

        # Generate message
        creature_name = creature.get_display_name()
        stat_name = stat.capitalize()

        # Determine magnitude description
        abs_change = abs(actual_change)
        if abs_change == 1:
            magnitude = ""
        elif abs_change == 2:
            magnitude = " sharply"
        elif abs_change >= 3:
            magnitude = " drastically"
        else:
            magnitude = ""

        # Build message
        if actual_change > 0:
            battle_log.add(f"{creature_name}'s {stat_name}{magnitude} rose!")
        else:
            battle_log.add(f"{creature_name}'s {stat_name}{magnitude} fell!")

        # Show ability message if Contrary or Simple activated
        if ability:
            if ability_inverts and stages != 0:
                battle_log.add(f"{creature_name}'s {ability.name} reversed the change!")
            elif ability_modifier == 2 and stages != 0:
                battle_log.add(f"{creature_name}'s {ability.name} doubled the effect!")

        return True

    def reset_stat_stages(self, is_player: bool):
        """
        Reset all stat stages to 0 when creature switches out.

        Args:
            is_player: True to reset player's creature, False for opponent
        """
        stat_stages = self.player_stat_stages if is_player else self.opponent_stat_stages
        for stat in stat_stages:
            stat_stages[stat] = 0

    def get_modified_stat(
        self,
        creature: Creature,
        stat: str,
        is_player: bool
    ) -> int:
        """
        Get a creature's stat with all modifiers applied (stages, abilities, etc.).

        Args:
            creature: The creature
            stat: The stat to get ("attack", "defense", "speed", "special")
            is_player: True if this is the player's creature

        Returns:
            Modified stat value
        """
        # Get base stat
        base_stat = getattr(creature.species.base_stats, stat)

        # Apply stat stage modifier
        stat_stages = self.player_stat_stages if is_player else self.opponent_stat_stages
        if stat in stat_stages:
            stage_multiplier = self.get_stat_stage_multiplier(stat_stages[stat])
        else:
            stage_multiplier = 1.0

        # Apply ability stat modifiers (existing system)
        stat_mods = self.player_stat_mods if is_player else self.opponent_stat_mods
        ability_multiplier = stat_mods.get(stat, 1.0)

        # Calculate final stat
        final_stat = int(base_stat * stage_multiplier * ability_multiplier)

        return max(1, final_stat)

    def update_ability_stat_modifiers(self, creature: Creature, is_player: bool):
        """
        Update cached ability-based stat modifiers for a creature.

        Args:
            creature: The creature to update modifiers for
            is_player: True if player's creature, False for opponent
        """
        stat_mods = self.player_stat_mods if is_player else self.opponent_stat_mods
        stat_mods.clear()

        if not creature or not creature.species.ability:
            return

        ability = creature.species.ability
        ability_name = ability.name
        ability_type = ability.effect_type

        # Attack modifiers
        if ability_name in ["Pure Power", "Huge Power"]:
            stat_mods["attack"] = 2.0  # Double Attack
        elif ability_name == "Hustle":
            stat_mods["attack"] = 1.5  # 1.5x Attack
        elif ability_name == "Guts" and creature.status:
            stat_mods["attack"] = 1.5  # 1.5x Attack when statused
        elif ability_type == "boost_attack":
            boost_amount = ability.effect_data.get("boost", 1.5)
            stat_mods["attack"] = boost_amount

        # Defense modifiers
        if ability_name == "Marvel Scale" and creature.status:
            stat_mods["defense"] = 1.5  # 1.5x Defense when statused
        elif ability_type == "boost_defense":
            boost_amount = ability.effect_data.get("boost", 1.5)
            stat_mods["defense"] = boost_amount

        # Speed modifiers
        if ability_name == "Swift Swim" and hasattr(self, '_weather_for_ability_check'):
            # Weather-based speed boost (requires weather context)
            pass  # Handled in battle engine
        elif ability_name == "Slow Start":
            stat_mods["speed"] = 0.5  # Half speed (first 5 turns)
        elif ability_type == "boost_speed":
            boost_amount = ability.effect_data.get("boost", 2.0)
            stat_mods["speed"] = boost_amount

        # Special stat modifiers (Special Attack/Special Defense combined in this system)
        if ability_type == "boost_special":
            boost_amount = ability.effect_data.get("boost", 1.5)
            stat_mods["special"] = boost_amount

    def get_stat_stages(self, is_player: bool) -> Dict[str, int]:
        """
        Get current stat stages for a side.

        Args:
            is_player: True for player's stat stages, False for opponent

        Returns:
            Dictionary of stat stages
        """
        return self.player_stat_stages.copy() if is_player else self.opponent_stat_stages.copy()

    def set_stat_stage(self, is_player: bool, stat: str, stage: int):
        """
        Directly set a stat stage (for testing or special effects).

        Args:
            is_player: True for player's creature, False for opponent
            stat: Stat to set
            stage: Stage value (-6 to +6)
        """
        stat_stages = self.player_stat_stages if is_player else self.opponent_stat_stages
        if stat in stat_stages:
            stat_stages[stat] = max(-6, min(6, stage))
