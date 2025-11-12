"""
Battle weather system management.

This module handles all weather conditions (Rain, Sun, Sandstorm, Hail)
and their effects on battles.
"""

from enum import Enum
from ..core.creature import Creature


class Weather(Enum):
    """Weather conditions that affect battles."""
    NONE = "none"
    RAIN = "rain"          # Boosts Aqua moves, weakens Flame moves
    SUN = "sun"            # Boosts Flame moves, weakens Aqua moves
    SANDSTORM = "sandstorm"  # Damages non-Terra/Metal/Rock creatures each turn
    HAIL = "hail"          # Damages non-Frost creatures each turn


class WeatherManager:
    """
    Manages weather conditions during battles.

    This class is responsible for:
    - Setting and clearing weather conditions
    - Processing weather damage at end of turn
    - Handling weather immunity from abilities and types
    - Managing weather-related ability triggers
    """

    # Weather damage constants
    WEATHER_DAMAGE_PERCENT = 6.25  # 1/16 of max HP per turn

    # Type immunities to weather
    SANDSTORM_IMMUNE_TYPES = ["Terra", "Metal", "Rock"]
    HAIL_IMMUNE_TYPES = ["Frost"]

    def __init__(self):
        """Initialize the weather manager."""
        self.current_weather = Weather.NONE
        self.weather_turns_remaining = 0  # 0 = infinite until changed

    def set_weather(self, weather: Weather, turns: int, log_messages: list):
        """
        Set the current weather condition.

        Args:
            weather: The weather to set
            turns: Number of turns weather lasts (0 = infinite)
            log_messages: List to append weather messages to
        """
        self.current_weather = weather
        self.weather_turns_remaining = turns

        weather_messages = {
            Weather.RAIN: "It started to rain!",
            Weather.SUN: "The sunlight turned harsh!",
            Weather.SANDSTORM: "A sandstorm kicked up!",
            Weather.HAIL: "It started to hail!",
            Weather.NONE: "The weather cleared up!"
        }

        if weather in weather_messages:
            log_messages.append(weather_messages[weather])

    def process_weather_effects(
        self,
        player_active: Creature,
        opponent_active: Creature,
        log_messages: list
    ):
        """
        Process end-of-turn weather effects.

        Args:
            player_active: Player's active creature
            opponent_active: Opponent's active creature
            log_messages: List to append weather damage messages to
        """
        # Countdown weather turns
        if self.weather_turns_remaining > 0:
            self.weather_turns_remaining -= 1
            if self.weather_turns_remaining == 0:
                self.current_weather = Weather.NONE
                log_messages.append("The weather cleared up!")
                return

        # Process weather damage
        if self.current_weather == Weather.SANDSTORM:
            self._process_sandstorm_damage(player_active, log_messages)
            self._process_sandstorm_damage(opponent_active, log_messages)

        elif self.current_weather == Weather.HAIL:
            self._process_hail_damage(player_active, log_messages)
            self._process_hail_damage(opponent_active, log_messages)

    def _process_sandstorm_damage(self, creature: Creature, log_messages: list):
        """
        Process sandstorm damage for a creature.

        Args:
            creature: The creature to damage
            log_messages: List to append damage messages to
        """
        if creature.is_fainted():
            return

        # Check type immunity
        if any(t in self.SANDSTORM_IMMUNE_TYPES for t in creature.species.types):
            return

        # Check for Sand Veil/Sand Rush ability (immune to sandstorm damage)
        if creature.species.ability and creature.species.ability.name in ["Sand Veil", "Sand Rush", "Sand Force"]:
            return

        # Apply damage
        damage = max(1, int(creature.max_hp * self.WEATHER_DAMAGE_PERCENT / 100))
        creature.take_damage(damage)
        log_messages.append(f"{creature.get_display_name()} is buffeted by the sandstorm! ({damage} damage)")

    def _process_hail_damage(self, creature: Creature, log_messages: list):
        """
        Process hail damage for a creature.

        Args:
            creature: The creature to damage
            log_messages: List to append damage messages to
        """
        if creature.is_fainted():
            return

        # Check type immunity
        if any(t in self.HAIL_IMMUNE_TYPES for t in creature.species.types):
            return

        # Check for Ice Body/Snow Cloak ability (immune to hail damage)
        if creature.species.ability and creature.species.ability.name in ["Ice Body", "Snow Cloak", "Slush Rush"]:
            return

        # Apply damage
        damage = max(1, int(creature.max_hp * self.WEATHER_DAMAGE_PERCENT / 100))
        creature.take_damage(damage)
        log_messages.append(f"{creature.get_display_name()} is buffeted by the hail! ({damage} damage)")

    def get_speed_modifier(self, creature: Creature) -> float:
        """
        Get weather-based speed modifier for a creature.

        Args:
            creature: The creature to check

        Returns:
            Speed multiplier (usually 1.0, or 2.0 for weather-boosting abilities)
        """
        if not creature.species.ability:
            return 1.0

        ability_name = creature.species.ability.name

        # Speed-boosting weather abilities
        if ability_name == "Swift Swim" and self.current_weather == Weather.RAIN:
            return 2.0
        elif ability_name == "Chlorophyll" and self.current_weather == Weather.SUN:
            return 2.0
        elif ability_name == "Sand Rush" and self.current_weather == Weather.SANDSTORM:
            return 2.0
        elif ability_name == "Slush Rush" and self.current_weather == Weather.HAIL:
            return 2.0

        return 1.0

    def get_accuracy_modifier(self, attacker: Creature, defender: Creature) -> float:
        """
        Get weather-based accuracy modifier.

        Args:
            attacker: The attacking creature
            defender: The defending creature

        Returns:
            Accuracy multiplier (usually 1.0, or 0.8 for evasion abilities)
        """
        # Sand Veil in sandstorm increases evasion
        if (self.current_weather == Weather.SANDSTORM and
            defender.species.ability and
            defender.species.ability.name == "Sand Veil"):
            return 0.8  # 20% reduction in accuracy

        # Snow Cloak in hail increases evasion
        if (self.current_weather == Weather.HAIL and
            defender.species.ability and
            defender.species.ability.name == "Snow Cloak"):
            return 0.8  # 20% reduction in accuracy

        return 1.0

    def apply_weather_ability_effects(
        self,
        creature: Creature,
        is_on_entry: bool,
        log_messages: list
    ):
        """
        Apply weather-setting abilities when creatures enter battle.

        Args:
            creature: The creature that just entered battle
            is_on_entry: True if this is being called on battle entry
            log_messages: List to append weather messages to
        """
        if not is_on_entry or not creature.species.ability:
            return

        ability_name = creature.species.ability.name
        weather_abilities = {
            "Drizzle": Weather.RAIN,
            "Drought": Weather.SUN,
            "Sand Stream": Weather.SANDSTORM,
            "Snow Warning": Weather.HAIL
        }

        if ability_name in weather_abilities:
            new_weather = weather_abilities[ability_name]
            if self.current_weather != new_weather:
                self.set_weather(new_weather, turns=0, log_messages=log_messages)
                log_messages.append(f"{creature.get_display_name()}'s {ability_name} activated!")

    def get_current_weather(self) -> Weather:
        """
        Get the current weather condition.

        Returns:
            Current Weather enum value
        """
        return self.current_weather

    def is_weather_active(self, weather: Weather) -> bool:
        """
        Check if a specific weather condition is active.

        Args:
            weather: The weather to check

        Returns:
            True if the specified weather is active, False otherwise
        """
        return self.current_weather == weather

    def clear_weather(self, log_messages: list):
        """
        Clear the current weather.

        Args:
            log_messages: List to append weather messages to
        """
        if self.current_weather != Weather.NONE:
            self.set_weather(Weather.NONE, turns=0, log_messages=log_messages)
