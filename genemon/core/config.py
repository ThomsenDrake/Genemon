"""
Configuration system for game settings.
"""

import json
import os
from typing import Optional
from ..ui.colors import ColorSupport


class GameConfig:
    """
    Game configuration manager.
    Handles user preferences and settings.
    """

    DEFAULT_CONFIG = {
        "colors_enabled": True,
        "auto_save": True,
        "battle_animations": True,
        "show_type_effectiveness": True,
        "confirm_run": True,
    }

    def __init__(self, config_path: str = "genemon_config.json"):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.settings = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.config_path):
            # Create default config file
            self.save()
            return False

        try:
            with open(self.config_path, 'r') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to handle new settings
                self.settings.update(loaded_settings)

            # Apply color setting
            if self.settings["colors_enabled"]:
                ColorSupport.enable()
            else:
                ColorSupport.disable()

            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config: {e}")
            return False

    def save(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
            return False

    def get(self, key: str, default=None):
        """
        Get a configuration value.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value) -> None:
        """
        Set a configuration value.

        Args:
            key: Setting key
            value: New value
        """
        self.settings[key] = value

        # Apply special settings immediately
        if key == "colors_enabled":
            if value:
                ColorSupport.enable()
            else:
                ColorSupport.disable()

    def toggle(self, key: str) -> bool:
        """
        Toggle a boolean setting.

        Args:
            key: Setting key

        Returns:
            New value after toggle
        """
        current = self.settings.get(key, False)
        new_value = not current
        self.set(key, new_value)
        return new_value

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = self.DEFAULT_CONFIG.copy()
        self.save()

    def show_settings(self) -> None:
        """Display current settings."""
        print("\n" + "=" * 60)
        print("  GAME SETTINGS")
        print("=" * 60)
        print()

        setting_descriptions = {
            "colors_enabled": "Terminal Colors",
            "auto_save": "Auto-Save After Battles",
            "battle_animations": "Battle Animations",
            "show_type_effectiveness": "Show Type Effectiveness in Battles",
            "confirm_run": "Confirm Before Running from Battle",
        }

        for key, description in setting_descriptions.items():
            value = self.settings.get(key, "N/A")
            status = "ON" if value else "OFF"
            print(f"  {description:40} [{status}]")

        print()
        print("=" * 60)
        print()


# Global config instance
_global_config: Optional[GameConfig] = None


def get_config() -> GameConfig:
    """
    Get the global configuration instance.

    Returns:
        Global GameConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = GameConfig()
    return _global_config


def init_config(config_path: str = "genemon_config.json") -> GameConfig:
    """
    Initialize the global configuration.

    Args:
        config_path: Path to configuration file

    Returns:
        Initialized GameConfig instance
    """
    global _global_config
    _global_config = GameConfig(config_path)
    return _global_config
