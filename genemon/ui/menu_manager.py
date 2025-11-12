"""
Menu management system for the game.

This module handles all in-game menus including team, items, shop, badges,
Pokedex, type chart, sprite viewer, and settings.
"""

from typing import Optional
from ..core.input_validator import InputValidator
from ..world.npc import NPC
from .display import Display


class MenuManager:
    """Manages all in-game menus and user interactions."""

    def __init__(self, display: Display):
        """
        Initialize the menu manager.

        Args:
            display: Display instance for rendering UI
        """
        self.display = display

    def show_team_menu(self, state) -> None:
        """
        Show team management menu.

        Args:
            state: GameState instance
        """
        self.display.clear_screen()
        self.display.show_team_summary(state.player_team)

        if not state.player_team.creatures:
            input("Press Enter to continue...")
            return

        print("Select a creature to view (or 0 to go back):")
        choice = InputValidator.get_valid_choice(
            "> ", 0, len(state.player_team.creatures),
            allow_empty=True, empty_value=0
        )

        if 1 <= choice <= len(state.player_team.creatures):
            creature = state.player_team.creatures[choice - 1]
            self.display.show_creature_summary(creature)
            input("Press Enter to continue...")

    def show_items_menu(self, state) -> None:
        """
        Show items menu and allow usage outside of battle.

        Args:
            state: GameState instance
        """
        from ..core.items import get_item

        self.display.clear_screen()
        print(f"\n=== ITEMS ===")
        print(f"Money: ${state.money}\n")
        self.display.show_inventory(state.items, show_descriptions=True)

        if not state.items:
            input("Press Enter to continue...")
            return

        print("Select item to use (or 0 to go back):")
        item_list = list(state.items.keys())
        choice = InputValidator.get_valid_choice(
            "> ", 0, len(item_list),
            allow_empty=True, empty_value=0
        )

        if choice < 1 or choice > len(item_list):
            return  # Cancel

        item_id = item_list[choice - 1]
        item = get_item(item_id)

        if not item:
            print("\nItem not found!")
            input("Press Enter to continue...")
            return

        # Can't use capture balls outside battle
        if item.item_type.value == 'capture':
            print("\nCapture Balls can only be used in battle!")
            input("Press Enter to continue...")
            return

        # Select target creature
        print("\nUse on which creature?")
        self.display.show_team_summary(state.player_team)

        if not state.player_team.creatures:
            input("Press Enter to continue...")
            return

        target_choice = InputValidator.get_valid_choice(
            "> ", 0, len(state.player_team.creatures),
            allow_empty=True, empty_value=0
        )

        if target_choice < 1 or target_choice > len(state.player_team.creatures):
            return  # Cancel

        target_creature = state.player_team.creatures[target_choice - 1]

        # Check if item can be used
        can_use, message = item.can_use_on(target_creature, in_battle=False)
        if not can_use:
            print(f"\n{message}")
            input("Press Enter to continue...")
            return

        # Use the item
        result_message = item.use(target_creature)
        print(f"\n{result_message}")

        # Deduct item from inventory
        state.items[item_id] -= 1
        if state.items[item_id] == 0:
            del state.items[item_id]

        input("Press Enter to continue...")

    def show_shop_menu(self, state, npc: NPC) -> None:
        """
        Show shop menu and allow purchasing items.

        Args:
            state: GameState instance
            npc: The shopkeeper NPC
        """
        from ..core.items import get_item

        while True:
            self.display.clear_screen()
            print(f"\n=== {npc.name}'s Shop ===")
            print(f"Your Money: ${state.money}\n")

            # Display shop inventory
            print("Available Items:")
            for i, item_id in enumerate(npc.shop_inventory, 1):
                item = get_item(item_id)
                if item:
                    owned = state.items.get(item_id, 0)
                    print(f"{i}. {item.name} - ${item.price} (Own: {owned})")
                    print(f"   {item.description}")

            print("\nSelect item to buy (or 0 to exit):")
            choice = InputValidator.get_valid_choice(
                "> ", 0, len(npc.shop_inventory),
                allow_empty=True, empty_value=0
            )

            if choice < 1 or choice > len(npc.shop_inventory):
                break  # Exit shop

            item_id = npc.shop_inventory[choice - 1]
            item = get_item(item_id)

            if not item:
                print("\nItem not found!")
                input("Press Enter to continue...")
                continue

            # Ask quantity
            print(f"\nHow many {item.name} would you like to buy?")
            print(f"Price: ${item.price} each")
            quantity = InputValidator.get_valid_choice(
                "> ", 0, 999,
                allow_empty=True, empty_value=0
            )

            if quantity < 1:
                continue

            total_cost = item.price * quantity

            # Check if player can afford
            if total_cost > state.money:
                print(f"\nYou don't have enough money! (Need: ${total_cost}, Have: ${state.money})")
                input("Press Enter to continue...")
                continue

            # Confirm purchase
            print(f"\nBuy {quantity}x {item.name} for ${total_cost}? (y/n)")
            confirm = input("> ").strip().lower()

            if confirm == 'y':
                # Deduct money
                state.money -= total_cost

                # Add items to inventory
                if item_id in state.items:
                    state.items[item_id] += quantity
                else:
                    state.items[item_id] = quantity

                print(f"\nPurchased {quantity}x {item.name}!")
                input("Press Enter to continue...")

    def show_badges(self, state) -> None:
        """
        Show collected badges.

        Args:
            state: GameState instance
        """
        self.display.clear_screen()
        self.display.print_header("BADGE COLLECTION")

        if not state.badges:
            print("\nYou haven't earned any badges yet!")
            print("Defeat Gym Leaders to earn badges!")
        else:
            print(f"\nBadges Earned: {len(state.badges)}/8\n")

            for i, badge in enumerate(state.badges, 1):
                print(f"{i}. {badge.name}")
                print(f"   Type: {badge.type}")
                print(f"   Gym Leader: {badge.gym_leader}")
                print(f"   {badge.description}")
                print()

        input("\nPress Enter to continue...")

    def show_move_relearner_menu(self, state) -> None:
        """
        Special menu for the Move Relearner NPC to reteach forgotten moves.

        Args:
            state: GameState instance
        """
        self.display.clear_screen()
        self.display.print_header("MOVE RELEARNER")

        if len(state.player_team.creatures) == 0:
            print("\nYou don't have any creatures to teach!")
            return

        # Select creature
        print("\nWhich creature should relearn moves?")
        self.display.show_team_summary(state.player_team)
        print(f"{len(state.player_team.creatures) + 1}. Cancel")

        choice = self.display.get_menu_choice(len(state.player_team.creatures) + 1)

        if choice >= len(state.player_team.creatures):
            return

        creature = state.player_team.creatures[choice]
        species = creature.species

        # Get all learnable moves from learnset
        if not species.learnset:
            print(f"\n{creature.get_display_name()} has no moves to relearn!")
            input("Press Enter to continue...")
            return

        # Get all moves the creature can currently learn (at or below its level)
        learnable_moves = []
        for learn_level, move in sorted(species.learnset.items()):
            if learn_level <= creature.level:
                # Check if creature doesn't already know this move
                if not any(m.name == move.name for m in creature.moves):
                    learnable_moves.append((learn_level, move))

        if not learnable_moves:
            print(f"\n{creature.get_display_name()} already knows all available moves!")
            input("Press Enter to continue...")
            return

        # Display learnable moves
        print(f"\n{creature.get_display_name()} can relearn these moves:")
        for i, (level, move) in enumerate(learnable_moves, 1):
            print(f"{i}. {move.name} (Learned at Lv.{level}) - {move.type} | Power: {move.power} | PP: {move.max_pp}")

        print(f"{len(learnable_moves) + 1}. Cancel")

        move_choice = self.display.get_menu_choice(len(learnable_moves) + 1)

        if move_choice >= len(learnable_moves):
            return

        selected_move = learnable_moves[move_choice][1]

        # If creature has 4 moves, ask which to replace
        if len(creature.moves) >= 4:
            print(f"\n{creature.get_display_name()} already knows 4 moves!")
            print("Which move should be forgotten?")

            for i, move in enumerate(creature.moves, 1):
                print(f"{i}. {move.name} ({move.type}) - Power: {move.power}, PP: {move.pp}/{move.max_pp}")
            print(f"{len(creature.moves) + 1}. Cancel")

            replace_choice = self.display.get_menu_choice(len(creature.moves) + 1)

            if replace_choice >= len(creature.moves):
                print(f"\n{creature.get_display_name()} did not learn {selected_move.name}.")
                input("Press Enter to continue...")
                return

            # Replace the move (deep copy to avoid shared references)
            import copy
            old_move = creature.moves[replace_choice]
            creature.moves[replace_choice] = copy.deepcopy(selected_move)
            print(f"\n{creature.get_display_name()} forgot {old_move.name} and learned {selected_move.name}!")
        else:
            # Add the move (deep copy to avoid shared references)
            import copy
            creature.moves.append(copy.deepcopy(selected_move))
            print(f"\n{creature.get_display_name()} learned {selected_move.name}!")

        input("Press Enter to continue...")

    def show_pokedex(self, state) -> None:
        """
        Show Pokedex.

        Args:
            state: GameState instance
        """
        self.display.clear_screen()
        print("\n=== POKEDEX ===")
        print(f"Seen: {len(state.pokedex_seen)}/151")
        print(f"Caught: {len(state.pokedex_caught)}/151\n")

        print("Enter creature number (1-151) or 0 to go back:")
        choice = InputValidator.get_valid_choice(
            "> ", 0, 151,
            allow_empty=True, empty_value=0
        )

        if 1 <= choice <= 151:
            self.display.show_pokedex_entry(
                choice,
                state.species_dict,
                state.pokedex_seen,
                state.pokedex_caught
            )
            input("\nPress Enter to continue...")

    def show_type_chart_menu(self) -> None:
        """Show type effectiveness chart menu."""
        from ..creatures.types import TYPES

        while True:
            self.display.clear_screen()
            print("\n=== TYPE CHART ===")
            print("1. View all types overview")
            print("2. View specific type effectiveness")
            print("0. Back")

            choice = InputValidator.get_valid_choice(
                "\n> ", 0, 2,
                allow_empty=True, empty_value=0
            )

            if choice == 0:
                break
            elif choice == 1:
                self.display.show_type_chart()
                input("Press Enter to continue...")
            elif choice == 2:
                print("\nAvailable types:")
                for i, type_name in enumerate(TYPES, 1):
                    print(f"{i}. {type_name}")

                type_choice = InputValidator.get_valid_choice(
                    "\nSelect type (or 0 to cancel): ",
                    0,
                    len(TYPES),
                    allow_empty=True,
                    empty_value=0
                )

                if type_choice > 0:
                    selected_type = TYPES[type_choice - 1]
                    self.display.show_type_chart(selected_type)
                    input("Press Enter to continue...")

    def show_sprite_viewer_menu(self, state) -> None:
        """
        Show sprite viewer menu.

        Args:
            state: GameState instance
        """
        self.display.clear_screen()
        print("\n=== SPRITE VIEWER ===")
        print(f"Caught: {len(state.pokedex_caught)}/151")
        print("\nView sprites for which creature?")
        print("Enter creature number (1-151) or 0 to go back:")

        choice = InputValidator.get_valid_choice(
            "> ", 0, 151,
            allow_empty=True, empty_value=0
        )

        if 1 <= choice <= 151:
            self.display.show_sprite_viewer(
                choice,
                state.species_dict,
                state.pokedex_caught
            )
            input("Press Enter to continue...")

    def show_settings_menu(self) -> None:
        """Show settings menu."""
        from ..core.config import get_config

        config = get_config()

        while True:
            self.display.clear_screen()
            config.show_settings()

            print("1. Toggle Terminal Colors")
            print("2. Toggle Auto-Save")
            print("3. Toggle Battle Animations")
            print("4. Toggle Type Effectiveness Display")
            print("5. Toggle Run Confirmation")
            print("6. Reset to Defaults")
            print("0. Back")

            choice = InputValidator.get_valid_choice(
                "\n> ", 0, 6,
                allow_empty=True, empty_value=0
            )

            if choice == 0:
                break
            elif choice == 1:
                new_val = config.toggle("colors_enabled")
                print(f"\nTerminal Colors: {'ON' if new_val else 'OFF'}")
                config.save()
                input("Press Enter to continue...")
            elif choice == 2:
                new_val = config.toggle("auto_save")
                print(f"\nAuto-Save: {'ON' if new_val else 'OFF'}")
                config.save()
                input("Press Enter to continue...")
            elif choice == 3:
                new_val = config.toggle("battle_animations")
                print(f"\nBattle Animations: {'ON' if new_val else 'OFF'}")
                config.save()
                input("Press Enter to continue...")
            elif choice == 4:
                new_val = config.toggle("show_type_effectiveness")
                print(f"\nType Effectiveness Display: {'ON' if new_val else 'OFF'}")
                config.save()
                input("Press Enter to continue...")
            elif choice == 5:
                new_val = config.toggle("confirm_run")
                print(f"\nRun Confirmation: {'ON' if new_val else 'OFF'}")
                config.save()
                input("Press Enter to continue...")
            elif choice == 6:
                print("\nAre you sure you want to reset all settings? (y/n)")
                confirm = input("> ").strip().lower()
                if confirm == 'y':
                    config.reset_to_defaults()
                    print("\nSettings reset to defaults!")
                    input("Press Enter to continue...")
