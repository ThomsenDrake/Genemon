"""
Display and UI utilities for terminal-based interface.
"""

from typing import List, Optional
from ..core.creature import Creature, Team
from ..world.map import Location
from ..world.npc import NPC


class Display:
    """Handles text-based display and UI rendering."""

    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        print("\n" * 50)  # Simple clear for terminal

    @staticmethod
    def print_separator(char: str = "=", length: int = 60):
        """Print a separator line."""
        print(char * length)

    @staticmethod
    def print_header(text: str):
        """Print a header."""
        Display.print_separator()
        print(f"  {text}")
        Display.print_separator()

    @staticmethod
    def print_menu(title: str, options: List[str]) -> None:
        """
        Print a menu with numbered options.

        Args:
            title: Menu title
            options: List of option strings
        """
        print(f"\n{title}")
        print("-" * 40)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print()

    @staticmethod
    def get_menu_choice(num_options: int) -> int:
        """
        Get user's menu choice.

        Args:
            num_options: Number of available options

        Returns:
            Selected option index (0-based)
        """
        while True:
            try:
                choice = int(input("Choose an option: "))
                if 1 <= choice <= num_options:
                    return choice - 1
                else:
                    print(f"Please enter a number between 1 and {num_options}")
            except ValueError:
                print("Please enter a valid number")

    @staticmethod
    def show_creature_summary(creature: Creature) -> None:
        """Display summary of a creature."""
        species = creature.species
        print(f"\n{'=' * 50}")
        print(f"  {creature.get_display_name().upper()} (Lv. {creature.level})")
        print(f"{'=' * 50}")
        print(f"  Type: {' / '.join(species.types)}")
        print(f"  HP: {creature.current_hp}/{creature.max_hp}")
        print(f"  Attack: {creature.attack}  Defense: {creature.defense}")
        print(f"  Special: {creature.special}  Speed: {creature.speed}")
        print(f"  EXP: {creature.exp}")
        print(f"\n  {species.flavor_text}")
        print(f"{'=' * 50}\n")

    @staticmethod
    def show_team_summary(team: Team) -> None:
        """Display summary of player's team."""
        print("\n=== YOUR TEAM ===")
        if not team.creatures:
            print("  (Empty)")
        else:
            for i, creature in enumerate(team.creatures, 1):
                if creature.is_fainted():
                    status = "FNT"
                elif creature.has_status():
                    status = creature.status.value.upper()[:3]
                else:
                    status = "OK"
                print(f"{i}. {creature.get_display_name()} Lv.{creature.level} "
                      f"HP: {creature.current_hp}/{creature.max_hp} [{status}]")
        print()

    @staticmethod
    def show_battle_state(
        player_creature: Creature,
        opponent_creature: Creature,
        is_wild: bool = False
    ) -> None:
        """Display battle state."""
        Display.print_separator()
        if is_wild:
            print(f"  WILD {opponent_creature.species.name.upper()}")
        else:
            print(f"  OPPONENT'S {opponent_creature.species.name.upper()}")

        print(f"  Lv.{opponent_creature.level}  "
              f"HP: {opponent_creature.current_hp}/{opponent_creature.max_hp}")

        # Simple HP bar
        hp_percent = opponent_creature.current_hp / opponent_creature.max_hp
        bar_length = 20
        filled = int(hp_percent * bar_length)
        bar = "[" + "#" * filled + "-" * (bar_length - filled) + "]"
        print(f"  {bar}")

        Display.print_separator()

        print(f"\n  YOUR {player_creature.get_display_name().upper()}")
        print(f"  Lv.{player_creature.level}  "
              f"HP: {player_creature.current_hp}/{player_creature.max_hp}")

        # Simple HP bar
        hp_percent = player_creature.current_hp / player_creature.max_hp
        filled = int(hp_percent * bar_length)
        bar = "[" + "#" * filled + "-" * (bar_length - filled) + "]"
        print(f"  {bar}\n")

    @staticmethod
    def show_location(
        location: Location,
        player_x: int,
        player_y: int,
        npcs: List[NPC] = None
    ) -> None:
        """
        Display the current location map.

        Args:
            location: Location to display
            player_x: Player X coordinate
            player_y: Player Y coordinate
            npcs: List of NPCs at this location
        """
        print(f"\n=== {location.name} ===\n")

        # Create a copy of the map with player and NPCs
        for y, row in enumerate(location.tiles):
            line = ""
            for x, tile in enumerate(row):
                # Check if player is here
                if x == player_x and y == player_y:
                    line += "@"
                # Check if NPC is here
                elif npcs:
                    npc_here = None
                    for npc in npcs:
                        if npc.x == x and npc.y == y:
                            npc_here = npc
                            break
                    if npc_here:
                        line += npc_here.sprite
                    else:
                        line += tile.get_char()
                else:
                    line += tile.get_char()
            print(line)
        print()

    @staticmethod
    def show_pokedex_entry(creature_id: int, species_dict: dict, seen: set, caught: set):
        """Show Pokedex entry for a creature."""
        if creature_id not in seen:
            print(f"#{creature_id:03d}: ??? (Not yet seen)")
            return

        species = species_dict[creature_id]
        status = "CAUGHT" if creature_id in caught else "SEEN"

        print(f"\n{'=' * 60}")
        print(f"  #{species.id:03d}: {species.name.upper()} [{status}]")
        print(f"{'=' * 60}")
        print(f"  Type: {' / '.join(species.types)}")

        if creature_id in caught:
            stats = species.base_stats
            print(f"\n  Base Stats:")
            print(f"    HP: {stats.hp}  Attack: {stats.attack}  Defense: {stats.defense}")
            print(f"    Special: {stats.special}  Speed: {stats.speed}")
            print(f"\n  Moves:")
            for move in species.moves[:4]:  # Show first 4 moves
                print(f"    - {move.name} ({move.type}) Power: {move.power}")
            print(f"\n  {species.flavor_text}")

        print(f"{'=' * 60}\n")

    @staticmethod
    def show_moves(creature: Creature) -> None:
        """Display creature's moves with PP information."""
        print(f"\n=== {creature.get_display_name()}'s Moves ===")
        for i, move in enumerate(creature.moves, 1):
            pp_display = f"PP: {move.pp}/{move.max_pp}"
            if move.pp == 0:
                pp_display += " (OUT OF PP!)"
            print(f"{i}. {move.name} ({move.type}) - "
                  f"Power: {move.power} Acc: {move.accuracy}% {pp_display}")
        print()

    @staticmethod
    def show_message(message: str, wait: bool = False) -> None:
        """
        Display a message.

        Args:
            message: Message to display
            wait: If True, wait for user input
        """
        print(f"\n{message}")
        if wait:
            input("\nPress Enter to continue...")

    @staticmethod
    def show_battle_log(messages: List[str]) -> None:
        """Display battle log messages."""
        print("\n--- Battle Log ---")
        for msg in messages:
            print(f"  {msg}")
        print()

    @staticmethod
    def show_inventory(items: dict, show_descriptions: bool = False) -> None:
        """
        Display player's inventory.

        Args:
            items: Dictionary of item_id -> quantity
            show_descriptions: If True, show item descriptions
        """
        from ..core.items import get_item

        print("\n=== INVENTORY ===")
        if not items:
            print("  (Empty)")
        else:
            for i, (item_id, quantity) in enumerate(items.items(), 1):
                item = get_item(item_id)
                if item:
                    print(f"{i}. {item.name} x{quantity}", end="")
                    if show_descriptions:
                        print(f" - {item.description}")
                    else:
                        print()
        print()
