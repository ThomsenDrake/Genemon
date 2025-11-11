"""
Main game engine and game loop.
"""

import random
from typing import Optional
from .save_system import GameState, SaveManager
from .creature import Creature, Team
from ..world.map import World, Location
from ..world.npc import NPCRegistry, NPC
from ..battle.engine import Battle, BattleAction, BattleResult
from ..ui.display import Display


class Game:
    """Main game engine."""

    def __init__(self):
        """Initialize the game engine."""
        self.state: Optional[GameState] = None
        self.save_manager = SaveManager()
        self.world = World()
        self.npc_registry = NPCRegistry()
        self.display = Display()
        self.running = False

    def run(self):
        """Main game loop."""
        self.running = True

        self.display.clear_screen()
        self.display.print_header("GENEMON - Monster Collector RPG")

        # Main menu
        while self.running:
            self._main_menu()

    def _main_menu(self):
        """Display main menu."""
        options = [
            "New Game",
            "Load Game",
            "Exit"
        ]

        self.display.print_menu("Main Menu", options)
        choice = self.display.get_menu_choice(len(options))

        if choice == 0:
            self._new_game()
        elif choice == 1:
            self._load_game()
        elif choice == 2:
            self.running = False
            print("\nThanks for playing!")

    def _new_game(self):
        """Start a new game."""
        self.display.clear_screen()
        self.display.print_header("NEW GAME")

        print("Welcome to the world of Genemon!")
        print("In this world, you'll encounter 151 unique creatures,")
        print("each generated specially for your adventure!\n")

        player_name = input("What is your name? ").strip() or "Player"
        save_name = input("Save file name? ").strip() or "save1"

        # Choose starter
        print("\nChoose your starter creature:")
        print("1. Starter 1 (Flame type)")
        print("2. Starter 2 (Aqua type)")
        print("3. Starter 3 (Leaf type)")

        starter_choice = self.display.get_menu_choice(3)

        # Create new game with generated creatures
        print("\nGenerating your unique world...")
        self.state = self.save_manager.create_new_game(
            save_name,
            player_name,
            starter_choice
        )

        # Save immediately
        self.save_manager.save_game(self.state)

        print(f"\nWelcome, {player_name}!")
        print(f"Your adventure begins in {self.world.get_starting_location().name}!")
        input("\nPress Enter to start...")

        # Start game loop
        self._game_loop()

    def _load_game(self):
        """Load an existing game."""
        saves = self.save_manager.list_saves()

        if not saves:
            print("\nNo save files found!")
            input("Press Enter to continue...")
            return

        print("\nAvailable saves:")
        for i, save in enumerate(saves, 1):
            print(f"{i}. {save}")

        choice = self.display.get_menu_choice(len(saves))
        save_name = saves[choice]

        self.state = self.save_manager.load_game(save_name)

        if self.state:
            print(f"\nWelcome back, {self.state.player_name}!")
            input("Press Enter to continue...")
            self._game_loop()

    def _game_loop(self):
        """Main gameplay loop."""
        while self.state:
            self.display.clear_screen()

            # Get current location
            location = self.world.get_location(self.state.current_location)
            npcs = self.npc_registry.get_npcs_at_location(location.id)

            # Display location
            self.display.show_location(
                location,
                self.state.player_x,
                self.state.player_y,
                npcs
            )

            # Display menu
            options = [
                "Move",
                "Team",
                "Items",
                "Pokedex",
                "Save",
                "Quit to Menu"
            ]

            self.display.print_menu("What do you want to do?", options)
            choice = self.display.get_menu_choice(len(options))

            if choice == 0:
                self._handle_movement(location, npcs)
            elif choice == 1:
                self._show_team_menu()
            elif choice == 2:
                self._show_items_menu()
            elif choice == 3:
                self._show_pokedex()
            elif choice == 4:
                self.save_manager.save_game(self.state)
                print("\nGame saved!")
                input("Press Enter to continue...")
            elif choice == 5:
                self.state = None  # Exit to main menu

    def _handle_movement(self, location: Location, npcs: list):
        """Handle player movement."""
        print("\nMove: [W] Up  [S] Down  [A] Left  [D] Right  [X] Cancel")
        direction = input("Direction: ").strip().lower()

        new_x, new_y = self.state.player_x, self.state.player_y

        if direction == 'w':
            new_y -= 1
        elif direction == 's':
            new_y += 1
        elif direction == 'a':
            new_x -= 1
        elif direction == 'd':
            new_x += 1
        elif direction == 'x':
            return

        # Check if move is valid
        if location.is_walkable(new_x, new_y):
            self.state.player_x = new_x
            self.state.player_y = new_y

            # Check for NPC interaction
            npc = self.npc_registry.get_npc_at_position(
                location.id,
                new_x,
                new_y
            )
            if npc:
                self._interact_with_npc(npc)

            # Check for wild encounter
            tile = location.get_tile(new_x, new_y)
            if tile and tile.can_encounter:
                if random.random() < tile.encounter_rate:
                    self._wild_encounter()

    def _interact_with_npc(self, npc: NPC):
        """Interact with an NPC."""
        self.display.clear_screen()
        print(npc.get_dialogue())

        if npc.is_shopkeeper:
            print("\nWould you like to buy something? (y/n)")
            choice = input("> ").strip().lower()
            if choice == 'y':
                self._shop_menu(npc)
        elif npc.is_healer:
            print("\nWould you like me to heal your creatures? (y/n)")
            choice = input("> ").strip().lower()
            if choice == 'y':
                self.state.player_team.heal_all()
                print("\nYour creatures are fully healed!")
                input("Press Enter to continue...")
        elif npc.is_trainer and not npc.has_been_defeated:
            print("\nThe trainer wants to battle!")
            input("Press Enter to continue...")

            # Create trainer battle (simplified - no actual team yet)
            # For now, create a random wild creature for the trainer
            self._trainer_battle(npc)

        input("\nPress Enter to continue...")

    def _wild_encounter(self):
        """Handle wild creature encounter."""
        # Choose a random creature from the roster
        creature_id = random.randint(1, len(self.state.species_dict))
        species = self.state.species_dict[creature_id]

        # Add to seen
        self.state.pokedex_seen.add(creature_id)

        # Create wild creature at appropriate level
        level = random.randint(2, 10)
        wild_creature = Creature(species=species, level=level, current_hp=0)

        # Create battle
        wild_team = Team()
        wild_team.add_creature(wild_creature)

        self._battle(wild_team, is_wild=True)

    def _trainer_battle(self, npc: NPC):
        """Handle trainer battle."""
        # Check if trainer has a fixed team stored
        if npc.id in self.state.trainer_teams:
            # Use stored team
            trainer_team = self.state.trainer_teams[npc.id]
        else:
            # Generate and store a new team for this trainer
            trainer_team = self._generate_trainer_team(npc)
            self.state.trainer_teams[npc.id] = trainer_team

        result = self._battle(trainer_team, is_wild=False)

        if result == BattleResult.PLAYER_WIN:
            npc.has_been_defeated = True
            self.state.defeated_trainers.append(npc.id)

    def _generate_trainer_team(self, npc: NPC) -> Team:
        """
        Generate a fixed team for a trainer NPC.

        Args:
            npc: The trainer NPC

        Returns:
            Team for the trainer
        """
        # Use NPC ID as seed for reproducibility
        rng = random.Random(hash(npc.id + str(self.state.seed)))

        trainer_team = Team()

        # Determine team size and level based on NPC type
        if "gym_leader" in npc.id:
            team_size = rng.randint(3, 6)
            min_level = 12
            max_level = 18
        elif "rival" in npc.id:
            team_size = rng.randint(2, 4)
            min_level = 8
            max_level = 14
        else:
            # Regular trainers
            team_size = rng.randint(1, 3)
            min_level = 5
            max_level = 12

        # Generate team
        for i in range(team_size):
            # Pick a random creature from the roster
            creature_id = rng.randint(1, len(self.state.species_dict))
            species = self.state.species_dict[creature_id]
            level = rng.randint(min_level, max_level)

            # Create creature
            creature = Creature(species=species, level=level, current_hp=0)
            trainer_team.add_creature(creature)

        return trainer_team

    def _battle(self, opponent_team: Team, is_wild: bool = False) -> BattleResult:
        """Handle a battle."""
        battle = Battle(
            self.state.player_team,
            opponent_team,
            is_wild=is_wild,
            can_run=is_wild
        )

        while battle.result == BattleResult.ONGOING:
            self.display.clear_screen()

            # Show battle state
            self.display.show_battle_state(
                battle.player_active,
                battle.opponent_active,
                is_wild
            )

            # Show recent battle log
            self.display.show_battle_log(battle.log.get_recent(5))

            # Battle menu - Items is now always available
            options = ["Attack", "Items", "Team", "Run"] if is_wild else ["Attack", "Items", "Team"]

            if is_wild:
                options.insert(3, "Capture")  # Insert Capture before Run

            self.display.print_menu("Battle Menu", options)
            choice = self.display.get_menu_choice(len(options))

            if choice == 0:  # Attack
                self.display.show_moves(battle.player_active)
                move_choice = self.display.get_menu_choice(
                    len(battle.player_active.moves)
                )
                battle.execute_turn(BattleAction.ATTACK, move_choice)

            elif choice == 1:  # Items
                self._use_item_in_battle(battle)

            elif choice == 2:  # Team
                self.display.show_team_summary(self.state.player_team)
                if len(self.state.player_team.creatures) > 1:
                    print("Switch to which creature?")
                    switch_choice = self.display.get_menu_choice(
                        len(self.state.player_team.creatures)
                    )
                    battle.execute_turn(BattleAction.SWITCH, switch_choice)
                else:
                    input("No other creatures available! Press Enter...")

            elif choice == 3 and is_wild:  # Capture
                # Check if player has capture balls
                if 'capture_ball' not in self.state.items or self.state.items['capture_ball'] <= 0:
                    print("\nYou don't have any Capture Balls!")
                    input("Press Enter to continue...")
                elif battle.try_capture(ball_strength=1.0):
                    # Deduct capture ball
                    self.state.items['capture_ball'] -= 1
                    if self.state.items['capture_ball'] == 0:
                        del self.state.items['capture_ball']

                    # Add to team or storage
                    captured = battle.opponent_active
                    if self.state.player_team.add_creature(captured):
                        print(f"\n{captured.species.name} was added to your team!")
                    else:
                        self.state.storage.append(captured)
                        print(f"\n{captured.species.name} was sent to storage!")

                    self.state.pokedex_caught.add(captured.species.id)
                    input("Press Enter to continue...")

            elif (choice == 3 and not is_wild) or (choice == 4 and is_wild):  # Run
                battle.execute_turn(BattleAction.RUN)

        # Battle ended
        self.display.clear_screen()
        self.display.show_battle_log(battle.log.get_recent(10))

        if battle.result == BattleResult.PLAYER_WIN:
            print("\n*** YOU WON! ***")
        elif battle.result == BattleResult.OPPONENT_WIN:
            print("\n*** YOU LOST! ***")
            # Heal team and return to town
            self.state.player_team.heal_all()
            self.state.current_location = "town_starter"
            start_loc = self.world.get_starting_location()
            self.state.player_x = start_loc.spawn_x
            self.state.player_y = start_loc.spawn_y
        elif battle.result == BattleResult.RAN_AWAY:
            print("\n*** Got away safely! ***")

        input("\nPress Enter to continue...")
        return battle.result

    def _use_item_in_battle(self, battle: Battle):
        """
        Handle item usage during battle.

        Args:
            battle: Current battle instance
        """
        from ..core.items import get_item

        # Show inventory
        self.display.show_inventory(self.state.items, show_descriptions=True)

        if not self.state.items:
            input("Press Enter to continue...")
            return

        # Get item choice
        print("Select item to use (or 0 to cancel):")
        item_list = list(self.state.items.keys())
        choice = int(input("> ").strip() or "0")

        if choice < 1 or choice > len(item_list):
            return  # Cancel

        item_id = item_list[choice - 1]
        item = get_item(item_id)

        if not item:
            print("\nItem not found!")
            input("Press Enter to continue...")
            return

        # For capture balls, special handling
        if item.item_type.value == 'capture':
            print("\nUse Capture Ball on the wild creature? (y/n)")
            confirm = input("> ").strip().lower()
            if confirm == 'y':
                if battle.is_wild:
                    # This will be handled by the capture choice in menu
                    print("\nUse the Capture option in the battle menu!")
                else:
                    print("\nCan't capture trainer creatures!")
                input("Press Enter to continue...")
            return

        # Select target creature (only from player's team in battle)
        print("\nUse on which creature?")
        self.display.show_team_summary(self.state.player_team)

        target_choice = int(input("> ").strip() or "0")

        if target_choice < 1 or target_choice > len(self.state.player_team.creatures):
            return  # Cancel

        target_creature = self.state.player_team.creatures[target_choice - 1]

        # Check if item can be used
        can_use, message = item.can_use_on(target_creature, in_battle=True)
        if not can_use:
            print(f"\n{message}")
            input("Press Enter to continue...")
            return

        # Use the item
        result_message = item.use(target_creature)
        print(f"\n{result_message}")

        # Deduct item from inventory
        self.state.items[item_id] -= 1
        if self.state.items[item_id] == 0:
            del self.state.items[item_id]

        # Log the item usage in battle
        battle.log.add(f"Used {item.name} on {target_creature.get_display_name()}!")
        battle.log.add(result_message)

        input("Press Enter to continue...")

        # Opponent takes a turn after item use
        battle.execute_turn(BattleAction.ITEM, None)

    def _show_team_menu(self):
        """Show team management menu."""
        self.display.clear_screen()
        self.display.show_team_summary(self.state.player_team)

        if not self.state.player_team.creatures:
            input("Press Enter to continue...")
            return

        print("Select a creature to view (or 0 to go back):")
        choice = int(input("> ").strip() or "0")

        if 1 <= choice <= len(self.state.player_team.creatures):
            creature = self.state.player_team.creatures[choice - 1]
            self.display.show_creature_summary(creature)
            input("Press Enter to continue...")

    def _show_items_menu(self):
        """Show items menu and allow usage outside of battle."""
        from ..core.items import get_item

        self.display.clear_screen()
        print(f"\n=== ITEMS ===")
        print(f"Money: ${self.state.money}\n")
        self.display.show_inventory(self.state.items, show_descriptions=True)

        if not self.state.items:
            input("Press Enter to continue...")
            return

        print("Select item to use (or 0 to go back):")
        item_list = list(self.state.items.keys())
        choice = int(input("> ").strip() or "0")

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
        self.display.show_team_summary(self.state.player_team)

        if not self.state.player_team.creatures:
            input("Press Enter to continue...")
            return

        target_choice = int(input("> ").strip() or "0")

        if target_choice < 1 or target_choice > len(self.state.player_team.creatures):
            return  # Cancel

        target_creature = self.state.player_team.creatures[target_choice - 1]

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
        self.state.items[item_id] -= 1
        if self.state.items[item_id] == 0:
            del self.state.items[item_id]

        input("Press Enter to continue...")

    def _shop_menu(self, npc: NPC):
        """
        Show shop menu and allow purchasing items.

        Args:
            npc: The shopkeeper NPC
        """
        from ..core.items import get_item

        while True:
            self.display.clear_screen()
            print(f"\n=== {npc.name}'s Shop ===")
            print(f"Your Money: ${self.state.money}\n")

            # Display shop inventory
            print("Available Items:")
            for i, item_id in enumerate(npc.shop_inventory, 1):
                item = get_item(item_id)
                if item:
                    owned = self.state.items.get(item_id, 0)
                    print(f"{i}. {item.name} - ${item.price} (Own: {owned})")
                    print(f"   {item.description}")

            print("\nSelect item to buy (or 0 to exit):")
            choice = int(input("> ").strip() or "0")

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
            try:
                quantity = int(input("> ").strip() or "0")
            except ValueError:
                quantity = 0

            if quantity < 1:
                continue

            total_cost = item.price * quantity

            # Check if player can afford
            if total_cost > self.state.money:
                print(f"\nYou don't have enough money! (Need: ${total_cost}, Have: ${self.state.money})")
                input("Press Enter to continue...")
                continue

            # Confirm purchase
            print(f"\nBuy {quantity}x {item.name} for ${total_cost}? (y/n)")
            confirm = input("> ").strip().lower()

            if confirm == 'y':
                # Deduct money
                self.state.money -= total_cost

                # Add items to inventory
                if item_id in self.state.items:
                    self.state.items[item_id] += quantity
                else:
                    self.state.items[item_id] = quantity

                print(f"\nPurchased {quantity}x {item.name}!")
                input("Press Enter to continue...")

    def _show_pokedex(self):
        """Show Pokedex."""
        self.display.clear_screen()
        print("\n=== POKEDEX ===")
        print(f"Seen: {len(self.state.pokedex_seen)}/151")
        print(f"Caught: {len(self.state.pokedex_caught)}/151\n")

        print("Enter creature number (1-151) or 0 to go back:")
        choice = int(input("> ").strip() or "0")

        if 1 <= choice <= 151:
            self.display.show_pokedex_entry(
                choice,
                self.state.species_dict,
                self.state.pokedex_seen,
                self.state.pokedex_caught
            )
            input("\nPress Enter to continue...")
