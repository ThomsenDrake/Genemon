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

    @staticmethod
    def show_type_chart(selected_type: Optional[str] = None) -> None:
        """
        Display type effectiveness chart.

        Args:
            selected_type: If provided, show detailed info for this type
        """
        from ..creatures.types import TYPES, TYPE_EFFECTIVENESS

        if selected_type:
            # Show detailed chart for one type
            if selected_type not in TYPES:
                print(f"Unknown type: {selected_type}")
                return

            print(f"\n{'=' * 60}")
            print(f"  {bold(colored_type(selected_type))} TYPE EFFECTIVENESS")
            print(f"{'=' * 60}")

            effectiveness = TYPE_EFFECTIVENESS.get(selected_type, {})

            # Strong against (2x damage)
            strong = [t for t, mult in effectiveness.items() if mult == 2.0]
            if strong:
                print(f"\n  {colored('STRONG AGAINST (2x damage):', TerminalColors.BRIGHT_GREEN)}")
                for t in strong:
                    print(f"    - {colored_type(t)}")

            # Weak against (0.5x damage)
            weak = [t for t, mult in effectiveness.items() if mult == 0.5]
            if weak:
                print(f"\n  {colored('WEAK AGAINST (0.5x damage):', TerminalColors.BRIGHT_YELLOW)}")
                for t in weak:
                    print(f"    - {colored_type(t)}")

            # No effect (0x damage)
            no_effect = [t for t, mult in effectiveness.items() if mult == 0.0]
            if no_effect:
                print(f"\n  {colored('NO EFFECT (immune):', TerminalColors.BRIGHT_RED)}")
                for t in no_effect:
                    print(f"    - {colored_type(t)}")

            # Neutral (1x damage - default for types not listed)
            listed_types = set(strong + weak + no_effect)
            neutral = [t for t in TYPES if t not in listed_types]
            if neutral:
                print(f"\n  {colored('NEUTRAL (1x damage):', TerminalColors.WHITE)}")
                neutral_str = ', '.join([colored_type(t) for t in neutral])
                print(f"    {neutral_str}")

            print(f"\n{'=' * 60}\n")
        else:
            # Show all types overview
            print(f"\n{'=' * 60}")
            print(f"  {bold('TYPE EFFECTIVENESS CHART')}")
            print(f"{'=' * 60}")
            print(f"\n  {colored('Legend:', TerminalColors.BOLD)}")
            print(f"    {colored('++', TerminalColors.BRIGHT_GREEN)} = Super effective (2x damage)")
            print(f"    {colored('--', TerminalColors.BRIGHT_YELLOW)} = Not very effective (0.5x damage)")
            print(f"    {colored('XX', TerminalColors.BRIGHT_RED)} = No effect (0x damage)")
            print(f"    {colored('==', TerminalColors.WHITE)} = Neutral (1x damage)")
            print(f"\n  All {len(TYPES)} types:")

            # Display types in columns
            types_per_row = 4
            for i in range(0, len(TYPES), types_per_row):
                row_types = TYPES[i:i + types_per_row]
                formatted_types = [f"{colored_type(t):20}" for t in row_types]
                print(f"    {''.join(formatted_types)}")

            print(f"\n  Tip: Use the Type Chart menu to view specific type matchups!")
            print(f"{'=' * 60}\n")

    @staticmethod
    def show_sprite_viewer(creature_id: int, species_dict: dict, caught: set) -> None:
        """
        Display sprite viewer for a specific creature.

        Args:
            creature_id: ID of creature to view
            species_dict: Dictionary of all creature species
            caught: Set of caught creature IDs
        """
        if creature_id not in species_dict:
            print(f"\nCreature #{creature_id:03d} does not exist!")
            return

        if creature_id not in caught:
            print(f"\nYou haven't caught creature #{creature_id:03d} yet!")
            print("Catch it first to view its sprites.")
            return

        species = species_dict[creature_id]

        print(f"\n{'=' * 60}")
        print(f"  {bold('SPRITE VIEWER')}")
        print(f"  #{species.id:03d}: {bold(species.name.upper())}")
        print(f"{'=' * 60}")

        # Display type
        colored_types = ' / '.join([colored_type(t) for t in species.types])
        print(f"\n  Type: {colored_types}")

        # Show front sprite
        if hasattr(species, 'front_sprite') and species.front_sprite:
            print(f"\n  {bold('FRONT SPRITE (Battle View):')}")
            Display._render_sprite_ascii(species.front_sprite)

        # Show back sprite
        if hasattr(species, 'back_sprite') and species.back_sprite:
            print(f"\n  {bold('BACK SPRITE (Your Team View):')}")
            Display._render_sprite_ascii(species.back_sprite)

        # Show mini sprite
        if hasattr(species, 'mini_sprite') and species.mini_sprite:
            print(f"\n  {bold('MINI SPRITE (Overworld):')}")
            Display._render_sprite_ascii(species.mini_sprite)

        print(f"\n{'=' * 60}\n")

    @staticmethod
    def _render_sprite_ascii(sprite_data: List[List[str]], scale: int = 1) -> None:
        """
        Render sprite data as colored ASCII art.

        Args:
            sprite_data: 2D array of hex color strings
            scale: Scale factor for rendering
        """
        if not sprite_data:
            print("    (No sprite data)")
            return

        # Render sprite with colored blocks
        for row in sprite_data:
            line = "    "  # Indent
            for _ in range(scale):  # Vertical scaling
                for color_hex in row:
                    if color_hex == "#000000" or color_hex.lower() == "transparent":
                        # Transparent or black - use space
                        char = "  " * scale
                    else:
                        # Use colored block character
                        char = "\u2588\u2588" * scale  # Full block
                    line += char
                print(line)
                if scale > 1:
                    line = "    "
