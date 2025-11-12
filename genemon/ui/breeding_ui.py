"""
Breeding Center UI module.
Handles all breeding-related menus and displays.
"""

from typing import Optional, List
from ..core.creature import Creature
from ..core.breeding import BreedingCenter, Egg
from .display import Display


class BreedingUI:
    """UI for the breeding center."""

    def __init__(self, display: Display):
        """
        Initialize breeding UI.

        Args:
            display: Display instance for rendering
        """
        self.display = display

    def show_breeding_menu(
        self,
        breeding_center: BreedingCenter,
        player_team: List[Creature],
        storage: List[Creature]
    ) -> Optional[str]:
        """
        Show the main breeding menu.

        Args:
            breeding_center: The breeding center instance
            player_team: List of creatures in player's team
            storage: List of creatures in storage

        Returns:
            Action string or None
        """
        while True:
            self.display.clear_screen()
            self.display.print_header("BREEDING CENTER")

            print("\nWelcome to the Breeding Center!")
            print("Here you can breed creatures to produce eggs.\n")

            # Show current status
            print(f"Active Breeding Pairs: {len(breeding_center.breeding_pairs)}")
            print(f"Eggs Ready: {len(breeding_center.eggs)}\n")

            options = [
                "Start Breeding",
                "Collect Egg",
                "Hatch Egg",
                "View Breeding Pairs",
                "View Eggs",
                "Back"
            ]

            self.display.print_menu("What would you like to do?", options)
            choice = self.display.get_menu_choice(len(options))

            if choice == 0:
                return "start_breeding"
            elif choice == 1:
                return "collect_egg"
            elif choice == 2:
                return "hatch_egg"
            elif choice == 3:
                return "view_pairs"
            elif choice == 4:
                return "view_eggs"
            elif choice == 5:
                return None

    def select_breeding_parents(
        self,
        available_creatures: List[Creature]
    ) -> Optional[tuple[Creature, Creature]]:
        """
        Let player select two creatures for breeding.

        Args:
            available_creatures: List of available creatures

        Returns:
            Tuple of (parent1, parent2) or None if cancelled
        """
        if len(available_creatures) < 2:
            print("\nYou need at least 2 creatures to breed!")
            input("Press Enter to continue...")
            return None

        self.display.clear_screen()
        self.display.print_header("SELECT BREEDING PARENTS")

        print("\nSelect the first parent:")
        print("-" * 60)

        for i, creature in enumerate(available_creatures, 1):
            shiny_mark = " ✨" if creature.is_shiny else ""
            print(f"{i}. {creature.get_display_name()} (Lv {creature.level}) - HP: {creature.current_hp}/{creature.max_hp}{shiny_mark}")

        print("0. Cancel")

        parent1_choice = self.display.get_menu_choice(len(available_creatures))
        if parent1_choice < 0 or parent1_choice >= len(available_creatures):
            return None

        parent1 = available_creatures[parent1_choice]

        # Filter out the first parent
        remaining_creatures = [c for c in available_creatures if c is not parent1]

        if len(remaining_creatures) == 0:
            print("\nNo other creatures available!")
            input("Press Enter to continue...")
            return None

        self.display.clear_screen()
        self.display.print_header("SELECT BREEDING PARENTS")

        print(f"\nFirst parent: {parent1.get_display_name()}")
        print("\nSelect the second parent:")
        print("-" * 60)

        for i, creature in enumerate(remaining_creatures, 1):
            shiny_mark = " ✨" if creature.is_shiny else ""
            print(f"{i}. {creature.get_display_name()} (Lv {creature.level}) - HP: {creature.current_hp}/{creature.max_hp}{shiny_mark}")

        print("0. Cancel")

        parent2_choice = self.display.get_menu_choice(len(remaining_creatures))
        if parent2_choice < 0 or parent2_choice >= len(remaining_creatures):
            return None

        parent2 = remaining_creatures[parent2_choice]

        return (parent1, parent2)

    def show_breeding_pairs(self, breeding_center: BreedingCenter):
        """
        Display active breeding pairs.

        Args:
            breeding_center: The breeding center instance
        """
        self.display.clear_screen()
        self.display.print_header("ACTIVE BREEDING PAIRS")

        if not breeding_center.breeding_pairs:
            print("\nNo active breeding pairs.")
        else:
            print("\nActive Breeding Pairs:")
            print("-" * 60)

            for i, (parent1, parent2) in enumerate(breeding_center.breeding_pairs, 1):
                print(f"\nPair {i}:")
                print(f"  Parent 1: {parent1.get_display_name()} (Lv {parent1.level})")
                print(f"  Parent 2: {parent2.get_display_name()} (Lv {parent2.level})")
                print(f"  Species: {parent1.species.name}")

        input("\nPress Enter to continue...")

    def show_eggs(self, breeding_center: BreedingCenter):
        """
        Display eggs ready to hatch.

        Args:
            breeding_center: The breeding center instance
        """
        self.display.clear_screen()
        self.display.print_header("EGGS READY TO HATCH")

        if not breeding_center.eggs:
            print("\nNo eggs ready.")
        else:
            print("\nEggs Ready to Hatch:")
            print("-" * 60)

            for i, egg in enumerate(breeding_center.eggs, 1):
                shiny_mark = " ✨ (SHINY!)" if egg.is_shiny else ""
                print(f"\nEgg {i}:")
                print(f"  Species: {egg.species.name}{shiny_mark}")
                print(f"  Inherited Moves: {len(egg.inherited_moves)}")
                if egg.inherited_moves:
                    for move in egg.inherited_moves:
                        print(f"    - {move.name} ({move.type})")

        input("\nPress Enter to continue...")

    def select_egg(self, eggs: List[Egg]) -> int:
        """
        Let player select an egg.

        Args:
            eggs: List of available eggs

        Returns:
            Index of selected egg, or -1 if cancelled
        """
        if not eggs:
            print("\nNo eggs available!")
            input("Press Enter to continue...")
            return -1

        self.display.clear_screen()
        self.display.print_header("SELECT EGG")

        print("\nSelect an egg:")
        print("-" * 60)

        for i, egg in enumerate(eggs, 1):
            shiny_mark = " ✨ (SHINY!)" if egg.is_shiny else ""
            print(f"{i}. {egg.species.name} Egg{shiny_mark}")

        print("0. Cancel")

        choice = self.display.get_menu_choice(len(eggs))
        return choice if 0 <= choice < len(eggs) else -1

    def select_breeding_pair(self, pairs: List[tuple]) -> int:
        """
        Let player select a breeding pair to collect egg from.

        Args:
            pairs: List of breeding pairs

        Returns:
            Index of selected pair, or -1 if cancelled
        """
        if not pairs:
            print("\nNo breeding pairs available!")
            input("Press Enter to continue...")
            return -1

        self.display.clear_screen()
        self.display.print_header("SELECT BREEDING PAIR")

        print("\nSelect a breeding pair to collect egg from:")
        print("-" * 60)

        for i, (parent1, parent2) in enumerate(pairs, 1):
            print(f"{i}. {parent1.get_display_name()} + {parent2.get_display_name()}")

        print("0. Cancel")

        choice = self.display.get_menu_choice(len(pairs))
        return choice if 0 <= choice < len(pairs) else -1
