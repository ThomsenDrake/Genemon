"""
Display and UI utilities for terminal-based interface.
"""

from typing import List, Optional
from ..core.creature import Creature, Team
from ..world.map import Location
from ..world.npc import NPC
from .colors import (
    colored, colored_type, colored_hp, colored_status,
    bold, underline, TerminalColors
)


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
        """Print a header with colors."""
        Display.print_separator()
        print(f"  {bold(text)}")
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
        """Display summary of a creature with colors."""
        species = creature.species
        print(f"\n{'=' * 50}")
        print(f"  {bold(creature.get_display_name().upper())} (Lv. {creature.level})")
        print(f"{'=' * 50}")

        # Color type names
        colored_types = ' / '.join([colored_type(t) for t in species.types])
        print(f"  Type: {colored_types}")

        # Color HP based on percentage
        print(f"  HP: {colored_hp(creature.current_hp, creature.max_hp)}")
        print(f"  Attack: {creature.attack}  Defense: {creature.defense}")
        print(f"  Special: {creature.special}  Speed: {creature.speed}")
        print(f"  EXP: {creature.exp}")

        # Show status if present
        if creature.has_status():
            print(f"  Status: {colored_status(creature.status.value)}")

        print(f"\n  {species.flavor_text}")
        print(f"{'=' * 50}\n")

    @staticmethod
    def show_team_summary(team: Team) -> None:
        """Display summary of player's team with colors."""
        print(f"\n=== {bold('YOUR TEAM')} ===")
        if not team.creatures:
            print("  (Empty)")
        else:
            for i, creature in enumerate(team.creatures, 1):
                # Status indicator
                if creature.is_fainted():
                    status = colored("[FNT]", TerminalColors.RED)
                elif creature.has_status():
                    status_text = creature.status.value.upper()[:3]
                    status = f"[{colored_status(creature.status.value)}]"
                else:
                    status = colored("[OK]", TerminalColors.BRIGHT_GREEN)

                # Colored HP
                hp_display = colored_hp(creature.current_hp, creature.max_hp)

                print(f"{i}. {bold(creature.get_display_name())} Lv.{creature.level} "
                      f"HP: {hp_display} {status}")
        print()

    @staticmethod
    def show_battle_state(
        player_creature: Creature,
        opponent_creature: Creature,
        is_wild: bool = False
    ) -> None:
        """Display battle state with colors."""
        Display.print_separator()

        # Opponent header
        opponent_name = bold(opponent_creature.species.name.upper())
        if is_wild:
            print(f"  WILD {opponent_name}")
        else:
            print(f"  OPPONENT'S {opponent_name}")

        # Opponent type display
        opponent_types = ' / '.join([colored_type(t) for t in opponent_creature.species.types])
        print(f"  Type: {opponent_types}")

        print(f"  Lv.{opponent_creature.level}  "
              f"HP: {colored_hp(opponent_creature.current_hp, opponent_creature.max_hp)}")

        # Colored HP bar
        hp_percent = opponent_creature.current_hp / opponent_creature.max_hp
        bar_length = 20
        filled = int(hp_percent * bar_length)
        bar_filled = colored("#" * filled, TerminalColors.BRIGHT_GREEN if hp_percent > 0.5
                            else TerminalColors.BRIGHT_YELLOW if hp_percent > 0.2
                            else TerminalColors.BRIGHT_RED)
        bar = "[" + bar_filled + "-" * (bar_length - filled) + "]"
        print(f"  {bar}")

        # Show opponent status if present
        if opponent_creature.has_status():
            print(f"  Status: {colored_status(opponent_creature.status.value)}")

        Display.print_separator()

        # Player header
        player_name = bold(player_creature.get_display_name().upper())
        print(f"\n  YOUR {player_name}")

        # Player type display
        player_types = ' / '.join([colored_type(t) for t in player_creature.species.types])
        print(f"  Type: {player_types}")

        print(f"  Lv.{player_creature.level}  "
              f"HP: {colored_hp(player_creature.current_hp, player_creature.max_hp)}")

        # Colored HP bar
        hp_percent = player_creature.current_hp / player_creature.max_hp
        filled = int(hp_percent * bar_length)
        bar_filled = colored("#" * filled, TerminalColors.BRIGHT_GREEN if hp_percent > 0.5
                            else TerminalColors.BRIGHT_YELLOW if hp_percent > 0.2
                            else TerminalColors.BRIGHT_RED)
        bar = "[" + bar_filled + "-" * (bar_length - filled) + "]"
        print(f"  {bar}")

        # Show player status if present
        if player_creature.has_status():
            print(f"  Status: {colored_status(player_creature.status.value)}")

        print()

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
        """Show Pokedex entry for a creature with colors."""
        if creature_id not in seen:
            print(f"#{creature_id:03d}: {colored('??? (Not yet seen)', TerminalColors.GRAY)}")
            return

        species = species_dict[creature_id]
        status = colored("CAUGHT", TerminalColors.BRIGHT_GREEN) if creature_id in caught else colored("SEEN", TerminalColors.BRIGHT_YELLOW)

        print(f"\n{'=' * 60}")
        print(f"  #{species.id:03d}: {bold(species.name.upper())} [{status}]")
        print(f"{'=' * 60}")

        # Color type names
        colored_types = ' / '.join([colored_type(t) for t in species.types])
        print(f"  Type: {colored_types}")

        if creature_id in caught:
            stats = species.base_stats
            print(f"\n  {bold('Base Stats:')}")
            print(f"    HP: {stats.hp}  Attack: {stats.attack}  Defense: {stats.defense}")
            print(f"    Special: {stats.special}  Speed: {stats.speed}")
            print(f"\n  {bold('Moves:')}")
            for move in species.moves[:4]:  # Show first 4 moves
                move_type = colored_type(move.type)
                print(f"    - {move.name} ({move_type}) Power: {move.power}")
            print(f"\n  {species.flavor_text}")

        print(f"{'=' * 60}\n")

    @staticmethod
    def show_moves(creature: Creature) -> None:
        """Display creature's moves with PP information and colors."""
        print(f"\n=== {bold(creature.get_display_name())}'s Moves ===")
        for i, move in enumerate(creature.moves, 1):
            # Color PP based on remaining amount
            pp_percent = move.pp / move.max_pp if move.max_pp > 0 else 0
            if pp_percent > 0.5:
                pp_color = TerminalColors.BRIGHT_GREEN
            elif pp_percent > 0:
                pp_color = TerminalColors.BRIGHT_YELLOW
            else:
                pp_color = TerminalColors.BRIGHT_RED

            pp_display = colored(f"PP: {move.pp}/{move.max_pp}", pp_color)
            if move.pp == 0:
                pp_display += colored(" (OUT OF PP!)", TerminalColors.BRIGHT_RED)

            # Color move type
            move_type = colored_type(move.type)

            print(f"{i}. {bold(move.name)} ({move_type}) - "
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
