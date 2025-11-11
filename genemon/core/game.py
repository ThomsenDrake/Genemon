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
                self._show_pokedex()
            elif choice == 3:
                self.save_manager.save_game(self.state)
                print("\nGame saved!")
                input("Press Enter to continue...")
            elif choice == 4:
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

        if npc.is_trainer and not npc.has_been_defeated:
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
        # For now, use a random creature
        creature_id = random.randint(1, len(self.state.species_dict))
        species = self.state.species_dict[creature_id]
        level = random.randint(5, 12)

        trainer_creature = Creature(species=species, level=level, current_hp=0)
        trainer_team = Team()
        trainer_team.add_creature(trainer_creature)

        result = self._battle(trainer_team, is_wild=False)

        if result == BattleResult.PLAYER_WIN:
            npc.has_been_defeated = True
            self.state.defeated_trainers.append(npc.id)

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

            # Battle menu
            options = ["Attack", "Team", "Run"] if is_wild else ["Attack", "Team"]

            if is_wild:
                options.insert(2, "Capture")

            self.display.print_menu("Battle Menu", options)
            choice = self.display.get_menu_choice(len(options))

            if choice == 0:  # Attack
                self.display.show_moves(battle.player_active)
                move_choice = self.display.get_menu_choice(
                    len(battle.player_active.species.moves)
                )
                battle.execute_turn(BattleAction.ATTACK, move_choice)

            elif choice == 1:  # Team
                self.display.show_team_summary(self.state.player_team)
                if len(self.state.player_team.creatures) > 1:
                    print("Switch to which creature?")
                    switch_choice = self.display.get_menu_choice(
                        len(self.state.player_team.creatures)
                    )
                    battle.execute_turn(BattleAction.SWITCH, switch_choice)
                else:
                    input("No other creatures available! Press Enter...")

            elif choice == 2 and is_wild:  # Capture
                if battle.try_capture(ball_strength=1.0):
                    # Add to team or storage
                    captured = battle.opponent_active
                    if self.state.player_team.add_creature(captured):
                        print(f"\n{captured.species.name} was added to your team!")
                    else:
                        self.state.storage.append(captured)
                        print(f"\n{captured.species.name} was sent to storage!")

                    self.state.pokedex_caught.add(captured.species.id)
                    input("Press Enter to continue...")

            elif (choice == 2 and not is_wild) or (choice == 3 and is_wild):  # Run
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
