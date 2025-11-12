"""
UI components for the trading system.

Provides menus and interfaces for exporting, importing, and managing trades.
"""

from typing import Optional, List, Tuple
from ..core.trading import TradeManager, TradePackage
from ..core.creature import Creature, Team, CreatureSpecies
from ..core.save_system import GameState
from .display import clear_screen, display_header, display_menu


class TradingUI:
    """
    User interface for trading system.
    """

    def __init__(self, trade_manager: TradeManager, game_state: GameState):
        """
        Initialize trading UI.

        Args:
            trade_manager: TradeManager instance
            game_state: Current game state
        """
        self.trade_manager = trade_manager
        self.game_state = game_state

    def show_trading_menu(self) -> bool:
        """
        Show the main trading menu.

        Returns:
            True to continue in menu, False to exit
        """
        clear_screen()
        display_header("Trading Center")

        print("\nWelcome to the Trading Center!")
        print("Here you can export and import creatures between save files.\n")

        options = [
            "Export Creature",
            "Import Creature",
            "View Trade Files",
            "Trade History",
            "Trade Statistics",
            "Back to Main Menu"
        ]

        choice = display_menu(options)

        if choice == 1:
            self._export_creature_menu()
        elif choice == 2:
            self._import_creature_menu()
        elif choice == 3:
            self._view_trade_files_menu()
        elif choice == 4:
            self._view_trade_history()
        elif choice == 5:
            self._view_trade_stats()
        elif choice == 6:
            return False

        return True

    def _export_creature_menu(self):
        """Menu for exporting a creature."""
        clear_screen()
        display_header("Export Creature")

        print("\nChoose where to export from:\n")
        options = ["Team", "Storage", "Cancel"]
        choice = display_menu(options)

        if choice == 1:
            self._export_from_team()
        elif choice == 2:
            self._export_from_storage()

    def _export_from_team(self):
        """Export a creature from the player's team."""
        if len(self.game_state.player_team.creatures) == 0:
            print("\nYour team is empty!")
            input("\nPress Enter to continue...")
            return

        if len(self.game_state.player_team.creatures) == 1:
            print("\nYou cannot export your last creature!")
            input("\nPress Enter to continue...")
            return

        clear_screen()
        display_header("Export from Team")

        print("\nSelect a creature to export:\n")

        # Display team
        for i, creature in enumerate(self.game_state.player_team.creatures, 1):
            status_str = f" [{creature.status}]" if creature.status else ""
            print(f"{i}. {creature.get_display_name()} - Lv.{creature.level} "
                  f"({creature.hp}/{creature.max_hp} HP){status_str}")

        print(f"{len(self.game_state.player_team.creatures) + 1}. Cancel")

        try:
            choice = int(input("\nChoice: "))
            if choice == len(self.game_state.player_team.creatures) + 1:
                return

            if 1 <= choice <= len(self.game_state.player_team.creatures):
                creature = self.game_state.player_team.creatures[choice - 1]

                # Confirm export
                print(f"\nExport {creature.get_display_name()} (Lv.{creature.level})?")
                print("This will remove it from your team!")
                confirm = input("Type 'yes' to confirm: ").strip().lower()

                if confirm == 'yes':
                    # Export creature
                    filepath = self.trade_manager.export_creature(
                        creature,
                        self.game_state.save_name
                    )

                    # Remove from team
                    self.game_state.player_team.creatures.pop(choice - 1)

                    print(f"\n✓ {creature.get_display_name()} exported successfully!")
                    print(f"Trade file: {filepath}")
                else:
                    print("\nExport cancelled.")
            else:
                print("\nInvalid choice!")

        except ValueError:
            print("\nInvalid input!")

        input("\nPress Enter to continue...")

    def _export_from_storage(self):
        """Export a creature from storage."""
        if len(self.game_state.storage) == 0:
            print("\nYour storage is empty!")
            input("\nPress Enter to continue...")
            return

        clear_screen()
        display_header("Export from Storage")

        print("\nSelect a creature to export:\n")

        # Display storage (first 20 creatures)
        display_count = min(20, len(self.game_state.storage))
        for i in range(display_count):
            creature = self.game_state.storage[i]
            print(f"{i + 1}. {creature.species.name} - Lv.{creature.level}")

        if len(self.game_state.storage) > 20:
            print(f"\n... and {len(self.game_state.storage) - 20} more")

        print(f"{display_count + 1}. Cancel")

        try:
            choice = int(input("\nChoice: "))
            if choice == display_count + 1:
                return

            if 1 <= choice <= display_count:
                creature = self.game_state.storage[choice - 1]

                # Confirm export
                print(f"\nExport {creature.species.name} (Lv.{creature.level})?")
                confirm = input("Type 'yes' to confirm: ").strip().lower()

                if confirm == 'yes':
                    # Export creature
                    filepath = self.trade_manager.export_creature(
                        creature,
                        self.game_state.save_name
                    )

                    # Remove from storage
                    self.game_state.storage.pop(choice - 1)

                    print(f"\n✓ {creature.species.name} exported successfully!")
                    print(f"Trade file: {filepath}")
                else:
                    print("\nExport cancelled.")
            else:
                print("\nInvalid choice!")

        except ValueError:
            print("\nInvalid input!")

        input("\nPress Enter to continue...")

    def _import_creature_menu(self):
        """Menu for importing a creature."""
        trade_files = self.trade_manager.list_trade_files()

        if not trade_files:
            clear_screen()
            display_header("Import Creature")
            print("\nNo trade files available!")
            input("\nPress Enter to continue...")
            return

        clear_screen()
        display_header("Import Creature")

        print("\nAvailable trade files:\n")

        for i, trade_file in enumerate(trade_files, 1):
            print(f"{i}. {trade_file['creature_name']} (Lv.{trade_file['level']}) "
                  f"- from {trade_file['source_save']}")
            print(f"   Exported: {trade_file['export_date'][:10]}")

        print(f"{len(trade_files) + 1}. Cancel")

        try:
            choice = int(input("\nChoice: "))
            if choice == len(trade_files) + 1:
                return

            if 1 <= choice <= len(trade_files):
                trade_file = trade_files[choice - 1]

                # Check team space
                team_full = len(self.game_state.player_team.creatures) >= 6

                print(f"\nImport {trade_file['creature_name']} (Lv.{trade_file['level']})?")
                if team_full:
                    print("Your team is full - creature will go to storage.")

                confirm = input("Type 'yes' to confirm: ").strip().lower()

                if confirm == 'yes':
                    try:
                        # Import creature
                        creature, species = self.trade_manager.import_creature(
                            trade_file['filepath'],
                            self.game_state.species_dict,
                            self.game_state.save_name
                        )

                        # Add species to this save's species dict if new
                        if species.id not in self.game_state.species_dict:
                            self.game_state.species_dict[species.id] = species

                        # Add to team or storage
                        if team_full:
                            self.game_state.storage.append(creature)
                            print(f"\n✓ {creature.species.name} added to storage!")
                        else:
                            self.game_state.player_team.add_creature(creature)
                            print(f"\n✓ {creature.species.name} added to team!")

                        # Mark as seen and caught in Pokedex
                        self.game_state.pokedex_seen.add(species.id)
                        self.game_state.pokedex_caught.add(species.id)

                        # Ask if user wants to delete trade file
                        delete = input("\nDelete trade file? (yes/no): ").strip().lower()
                        if delete == 'yes':
                            self.trade_manager.delete_trade_file(trade_file['filepath'])
                            print("Trade file deleted.")

                    except (FileNotFoundError, ValueError) as e:
                        print(f"\nError importing creature: {e}")
                else:
                    print("\nImport cancelled.")
            else:
                print("\nInvalid choice!")

        except ValueError:
            print("\nInvalid input!")

        input("\nPress Enter to continue...")

    def _view_trade_files_menu(self):
        """View and manage trade files."""
        trade_files = self.trade_manager.list_trade_files()

        clear_screen()
        display_header("Trade Files")

        if not trade_files:
            print("\nNo trade files available!")
        else:
            print(f"\n{len(trade_files)} trade file(s) available:\n")

            for i, trade_file in enumerate(trade_files, 1):
                print(f"{i}. {trade_file['creature_name']} (Lv.{trade_file['level']})")
                print(f"   From: {trade_file['source_save']}")
                print(f"   Date: {trade_file['export_date'][:19]}")
                print(f"   File: {trade_file['filename']}\n")

        input("\nPress Enter to continue...")

    def _view_trade_history(self):
        """View trade history."""
        history = self.trade_manager.get_trade_history(limit=20)

        clear_screen()
        display_header("Trade History")

        if not history:
            print("\nNo trades recorded yet!")
        else:
            print(f"\nRecent trades (showing {len(history)}):\n")

            for record in history:
                print(f"• {record.creature_name} (Lv.{record.creature_level})")
                print(f"  From {record.from_save} → To {record.to_save}")
                print(f"  Date: {record.timestamp[:19]}\n")

        input("\nPress Enter to continue...")

    def _view_trade_stats(self):
        """View trade statistics."""
        stats = self.trade_manager.get_trade_stats()

        clear_screen()
        display_header("Trade Statistics")

        print("\nOverall Trading Statistics:\n")
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Unique Save Files: {stats['unique_saves']}")
        print(f"Unique Species Traded: {stats['unique_species']}")

        input("\nPress Enter to continue...")


def display_trading_tutorial():
    """Display a tutorial about the trading system."""
    clear_screen()
    display_header("Trading System Tutorial")

    print("""
The Trading System allows you to exchange creatures between different save files!

How It Works:
1. Export a creature from your team or storage
2. This creates a .trade file in the saves/trades directory
3. Load a different save file
4. Import the .trade file to add the creature to that save
5. Each save keeps its own unique 151-creature roster

Features:
• Export creatures from team or storage
• Import creatures from any save file
• Trade history tracking
• Automatic Pokedex registration
• Cross-save species compatibility

Tips:
• You cannot export your last team member
• Imported creatures go to your team (or storage if full)
• Trade files can be deleted after import
• Species from other saves are added to your Pokedex

Ready to start trading? Select "Export Creature" to begin!
""")

    input("\nPress Enter to continue...")
