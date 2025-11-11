"""
Main game engine and game loop.
"""

import random
from typing import Optional
from .save_system import GameState, SaveManager
from .creature import Creature, Team, Badge
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
                "Badges",
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
                self._show_badges()
            elif choice == 4:
                self._show_pokedex()
            elif choice == 5:
                self.save_manager.save_game(self.state)
                print("\nGame saved!")
                input("Press Enter to continue...")
            elif choice == 6:
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
        elif npc.id == "move_relearner":
            # Special case for move relearner
            print("\nWould you like to relearn moves? (y/n)")
            choice = input("> ").strip().lower()
            if choice == 'y':
                self._move_relearner_menu()
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

            # Award badge if this is a gym leader
            if npc.is_gym_leader and npc.badge_id:
                self._award_badge(npc)

    def _award_badge(self, npc: NPC):
        """
        Award a badge to the player after defeating a gym leader.

        Args:
            npc: The gym leader NPC
        """
        # Check if player already has this badge
        if any(badge.badge_id == npc.badge_id for badge in self.state.badges):
            return

        # Create and add the badge
        badge = Badge(
            badge_id=npc.badge_id,
            name=npc.badge_name,
            type=npc.specialty_type,
            gym_leader=npc.name,
            description=npc.badge_description
        )
        self.state.badges.append(badge)

        # Celebratory message
        self.display.clear_screen()
        self.display.print_header("BADGE EARNED!")
        print(f"\nCongratulations! You earned the {badge.name}!")
        print(f"Type: {badge.type}")
        print(f"Gym Leader: {badge.gym_leader}")
        print(f"\n{badge.description}")
        print(f"\nTotal Badges: {len(self.state.badges)}")
        input("\nPress Enter to continue...")

    def _handle_evolution(self, creature: Creature):
        """
        Handle the evolution of a creature.

        Args:
            creature: The creature that can evolve
        """
        if not creature.can_evolve():
            return

        # Get the evolved form
        evolved_species_id = creature.species.evolves_into
        evolved_species = self.state.species_dict.get(evolved_species_id)

        if not evolved_species:
            return

        # Ask player if they want to evolve
        self.display.clear_screen()
        self.display.print_header("EVOLUTION!")
        print(f"\nYour {creature.species.name} is evolving!")
        print(f"\n{creature.species.name} → {evolved_species.name}")
        print(f"\nAllow evolution?")
        print("1. Yes")
        print("2. No")

        choice = self.display.get_menu_choice(2)

        if choice == 0:  # Yes, evolve
            old_name = creature.species.name
            old_hp = creature.current_hp
            old_max_hp = creature.max_hp

            # Evolve the creature
            creature.species = evolved_species
            creature._calculate_stats()

            # Maintain HP percentage
            hp_percentage = old_hp / old_max_hp if old_max_hp > 0 else 1.0
            creature.current_hp = int(creature.max_hp * hp_percentage)

            # Success message
            self.display.clear_screen()
            self.display.print_header("EVOLUTION COMPLETE!")
            print(f"\n{old_name} evolved into {evolved_species.name}!")
            print(f"\nNew stats:")
            print(f"  HP: {creature.max_hp}")
            print(f"  Attack: {creature.attack}")
            print(f"  Defense: {creature.defense}")
            print(f"  Special: {creature.special}")
            print(f"  Speed: {creature.speed}")
            input("\nPress Enter to continue...")

            # Mark as seen in pokedex
            self.state.pokedex_seen.add(evolved_species.id)

        else:
            print(f"\n{creature.species.name} did not evolve.")
            input("Press Enter to continue...")

    def _handle_move_learning(self, creature: Creature):
        """
        Handle a creature learning a new move.

        Args:
            creature: The creature that can learn a move
        """
        learnable_move = creature.get_learnable_move()
        if not learnable_move:
            return

        self.display.clear_screen()
        self.display.print_header("NEW MOVE!")
        print(f"\n{creature.get_display_name()} can learn {learnable_move.name}!")
        print(f"Type: {learnable_move.type} | Power: {learnable_move.power} | Accuracy: {learnable_move.accuracy}%")
        print(f"PP: {learnable_move.max_pp} | {learnable_move.description}")

        # Check if creature has room for the move
        if len(creature.moves) < 4:
            print(f"\nLearn {learnable_move.name}?")
            print("1. Yes")
            print("2. No")
            choice = self.display.get_menu_choice(2)

            if choice == 0:  # Yes
                creature.learn_move(learnable_move)
                print(f"\n{creature.get_display_name()} learned {learnable_move.name}!")
                input("Press Enter to continue...")
            else:
                print(f"\n{creature.get_display_name()} did not learn {learnable_move.name}.")
                input("Press Enter to continue...")

        else:
            # Need to replace a move
            print(f"\n{creature.get_display_name()} already knows 4 moves.")
            print(f"Replace a move with {learnable_move.name}?")
            print()

            # Show current moves
            for i, move in enumerate(creature.moves):
                print(f"{i+1}. {move.name} ({move.type}, {move.power} power, {move.pp}/{move.max_pp} PP)")
            print(f"{len(creature.moves)+1}. Don't learn {learnable_move.name}")

            choice = self.display.get_menu_choice(len(creature.moves) + 1)

            if choice < len(creature.moves):
                # Replace the chosen move
                old_move_name = creature.moves[choice].name
                creature.learn_move(learnable_move, replace_index=choice)
                print(f"\n{creature.get_display_name()} forgot {old_move_name} and learned {learnable_move.name}!")
                input("Press Enter to continue...")
            else:
                print(f"\n{creature.get_display_name()} did not learn {learnable_move.name}.")
                input("Press Enter to continue...")

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
        if npc.is_gym_leader:
            team_size = rng.randint(4, 6)  # Gym leaders have larger teams
            min_level = 14
            max_level = 20
        elif "rival" in npc.id:
            team_size = rng.randint(2, 4)
            min_level = 8
            max_level = 14
        else:
            # Regular trainers
            team_size = rng.randint(1, 3)
            min_level = 5
            max_level = 12

        # Filter creatures by type for gym leaders with specialty
        if npc.is_gym_leader and npc.specialty_type:
            # Get all creatures that match the gym leader's specialty type
            matching_species = []
            for species_id, species in self.state.species_dict.items():
                if (species.type1 == npc.specialty_type or
                    species.type2 == npc.specialty_type):
                    matching_species.append(species)

            # If we have enough matching creatures, use them
            if len(matching_species) >= team_size:
                selected_species = rng.sample(matching_species, team_size)
            else:
                # Not enough matching creatures, use what we have plus random ones
                selected_species = matching_species[:]
                remaining = team_size - len(selected_species)
                all_species = list(self.state.species_dict.values())
                selected_species.extend(rng.sample(all_species, remaining))
        else:
            # No type specialization, pick randomly
            selected_species = []
            for i in range(team_size):
                creature_id = rng.randint(1, len(self.state.species_dict))
                species = self.state.species_dict[creature_id]
                selected_species.append(species)

        # Generate team with selected species
        for species in selected_species:
            level = rng.randint(min_level, max_level)
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

            # Check for move learning and evolution after battle
            for creature in self.state.player_team.creatures:
                # Check if creature can learn a new move
                if creature.get_learnable_move():
                    self._handle_move_learning(creature)

                # Check for evolution
                if creature.can_evolve():
                    self._handle_evolution(creature)

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

    def _show_badges(self):
        """Show collected badges."""
        self.display.clear_screen()
        self.display.print_header("BADGE COLLECTION")

        if not self.state.badges:
            print("\nYou haven't earned any badges yet!")
            print("Defeat Gym Leaders to earn badges!")
        else:
            print(f"\nBadges Earned: {len(self.state.badges)}/8\n")

            for i, badge in enumerate(self.state.badges, 1):
                print(f"{i}. {badge.name}")
                print(f"   Type: {badge.type}")
                print(f"   Gym Leader: {badge.gym_leader}")
                print(f"   {badge.description}")
                print()

        input("\nPress Enter to continue...")

    def _move_relearner_menu(self):
        """
        Special menu for the Move Relearner NPC to reteach forgotten moves.
        """
        self.display.clear_screen()
        self.display.print_header("MOVE RELEARNER")

        if self.state.player_team.size() == 0:
            print("\nYou don't have any creatures to teach!")
            return

        # Select creature
        print("\nWhich creature should relearn moves?")
        self.display.show_team(self.state.player_team)
        print(f"{self.state.player_team.size() + 1}. Cancel")

        choice = self.display.get_menu_choice(self.state.player_team.size() + 1)

        if choice >= self.state.player_team.size():
            return

        creature = self.state.player_team.creatures[choice]
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

            # Replace the move
            old_move = creature.moves[replace_choice]
            creature.moves[replace_choice] = selected_move.copy()
            print(f"\n{creature.get_display_name()} forgot {old_move.name} and learned {selected_move.name}!")
        else:
            # Add the move
            creature.moves.append(selected_move.copy())
            print(f"\n{creature.get_display_name()} learned {selected_move.name}!")

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
