"""
Save and load game state system.
"""

import json
import os
from typing import Optional, Dict
from datetime import datetime
from .creature import Team, CreatureSpecies, Creature
from ..creatures.generator import CreatureGenerator
from ..sprites.generator import SpriteGenerator


class GameState:
    """
    Complete game state for a save file.
    """

    def __init__(self):
        """Initialize a new game state."""
        self.save_name: str = "default"
        self.player_name: str = "Player"
        self.play_time: int = 0  # In seconds
        self.current_location: str = "town_starter"
        self.player_x: int = 10
        self.player_y: int = 10

        # Generated content for this save
        self.seed: int = 0
        self.species_dict: Dict[int, CreatureSpecies] = {}

        # Player's team and storage
        self.player_team: Team = Team()
        self.storage: list = []  # Stored creatures

        # Game progress flags
        self.badges: list = []
        self.flags: Dict[str, bool] = {}
        self.defeated_trainers: list = []
        self.pokedex_seen: set = set()
        self.pokedex_caught: set = set()

        # Trainer teams (npc_id -> Team) - fixed teams per save
        self.trainer_teams: Dict[str, Team] = {}

        # Inventory (item_id -> quantity)
        self.items: Dict[str, int] = {
            "potion": 5,
            "ether": 3,
            "capture_ball": 10
        }
        self.money: int = 1000  # Starting money for shops

    def to_dict(self) -> dict:
        """Serialize game state to dictionary."""
        return {
            'version': '0.1.0',
            'save_name': self.save_name,
            'player_name': self.player_name,
            'play_time': self.play_time,
            'current_location': self.current_location,
            'player_x': self.player_x,
            'player_y': self.player_y,
            'seed': self.seed,
            'species': {
                str(k): v.to_dict()
                for k, v in self.species_dict.items()
            },
            'player_team': self.player_team.to_dict(),
            'storage': [c.to_dict() for c in self.storage],
            'badges': self.badges,
            'flags': self.flags,
            'defeated_trainers': self.defeated_trainers,
            'pokedex_seen': list(self.pokedex_seen),
            'pokedex_caught': list(self.pokedex_caught),
            'trainer_teams': {
                npc_id: team.to_dict()
                for npc_id, team in self.trainer_teams.items()
            },
            'items': self.items,
            'money': self.money
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Deserialize game state from dictionary."""
        state = cls()

        state.save_name = data.get('save_name', 'default')
        state.player_name = data.get('player_name', 'Player')
        state.play_time = data.get('play_time', 0)
        state.current_location = data.get('current_location', 'town_starter')
        state.player_x = data.get('player_x', 10)
        state.player_y = data.get('player_y', 10)
        state.seed = data.get('seed', 0)

        # Reconstruct species dictionary
        species_data = data.get('species', {})
        state.species_dict = {
            int(k): CreatureSpecies.from_dict(v)
            for k, v in species_data.items()
        }

        # Reconstruct team
        team_data = data.get('player_team', {'creatures': []})
        state.player_team = Team.from_dict(team_data, state.species_dict)

        # Reconstruct storage
        storage_data = data.get('storage', [])
        for creature_data in storage_data:
            species = state.species_dict[creature_data['species_id']]
            creature = Creature.from_dict(creature_data, species)
            state.storage.append(creature)

        # Game progress
        state.badges = data.get('badges', [])
        state.flags = data.get('flags', {})
        state.defeated_trainers = data.get('defeated_trainers', [])
        state.pokedex_seen = set(data.get('pokedex_seen', []))
        state.pokedex_caught = set(data.get('pokedex_caught', []))

        # Reconstruct trainer teams
        trainer_teams_data = data.get('trainer_teams', {})
        state.trainer_teams = {
            npc_id: Team.from_dict(team_data, state.species_dict)
            for npc_id, team_data in trainer_teams_data.items()
        }

        state.items = data.get('items', {"potion": 5, "ether": 3, "capture_ball": 10})
        state.money = data.get('money', 1000)

        return state


class SaveManager:
    """Manages saving and loading game states."""

    def __init__(self, save_dir: str = "saves"):
        """
        Initialize save manager.

        Args:
            save_dir: Directory to store save files
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def create_new_game(
        self,
        save_name: str,
        player_name: str,
        starter_choice: int = 0
    ) -> GameState:
        """
        Create a new game with generated creatures.

        Args:
            save_name: Name for the save file
            player_name: Player's name
            starter_choice: Index of starter (0-2)

        Returns:
            New GameState with generated creatures
        """
        state = GameState()
        state.save_name = save_name
        state.player_name = player_name

        # Generate unique seed for this save
        import random
        state.seed = random.randint(0, 999999)

        # Generate all 151 creatures for this save
        print(f"Generating 151 unique creatures (seed: {state.seed})...")
        generator = CreatureGenerator(state.seed)
        all_species = generator.generate_all_creatures()

        # Generate sprites for all creatures
        print("Generating sprites...")
        sprite_gen = SpriteGenerator(state.seed)

        for species in all_species:
            # Determine archetype based on types and stats
            archetype = self._determine_archetype(species)
            sprites = sprite_gen.generate_creature_sprites(
                species.id,
                species.types,
                archetype
            )
            species.sprite_data = sprites

        # Build species dictionary
        state.species_dict = {s.id: s for s in all_species}

        # Give player their starter
        starter_id = starter_choice + 1  # IDs 1, 2, 3 are starters
        starter_species = state.species_dict[starter_id]
        starter = Creature(
            species=starter_species,
            level=5,
            current_hp=0  # Will be set in __post_init__
        )

        state.player_team.add_creature(starter)
        state.pokedex_seen.add(starter_id)
        state.pokedex_caught.add(starter_id)

        print(f"Game created! You chose {starter_species.name}!")

        return state

    def _determine_archetype(self, species: CreatureSpecies) -> str:
        """Determine visual archetype for sprite generation."""
        # Simple heuristic based on types and stats
        types = species.types
        stats = species.base_stats

        if "Gale" in types or stats.speed > 80:
            return "bird"
        elif "Aqua" in types:
            return "fish"
        elif "Insect" in types:
            return "insect"
        elif "Toxin" in types or "Spirit" in types:
            return "serpent"
        elif stats.defense > stats.attack:
            return "quadruped"
        else:
            return "biped"

    def save_game(self, state: GameState) -> bool:
        """
        Save game state to file.

        Args:
            state: GameState to save

        Returns:
            True if successful
        """
        try:
            save_path = os.path.join(self.save_dir, f"{state.save_name}.json")
            data = state.to_dict()

            # Add metadata
            data['saved_at'] = datetime.now().isoformat()

            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Game saved to {save_path}")
            return True

        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[GameState]:
        """
        Load game state from file.

        Args:
            save_name: Name of save file to load

        Returns:
            GameState if successful, None otherwise
        """
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")

            if not os.path.exists(save_path):
                print(f"Save file not found: {save_path}")
                return None

            with open(save_path, 'r') as f:
                data = json.load(f)

            state = GameState.from_dict(data)
            print(f"Game loaded from {save_path}")
            return state

        except Exception as e:
            print(f"Error loading game: {e}")
            return None

    def list_saves(self) -> list:
        """
        List all available save files.

        Returns:
            List of save file names (without .json extension)
        """
        try:
            saves = []
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    saves.append(filename[:-5])  # Remove .json
            return saves
        except Exception as e:
            print(f"Error listing saves: {e}")
            return []

    def delete_save(self, save_name: str) -> bool:
        """
        Delete a save file.

        Args:
            save_name: Name of save to delete

        Returns:
            True if successful
        """
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Deleted save: {save_name}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False

    def export_creatures(
        self,
        state: GameState,
        export_path: str
    ) -> bool:
        """
        Export creature roster to a separate file.

        Args:
            state: GameState to export from
            export_path: Path to export file

        Returns:
            True if successful
        """
        try:
            export_data = {
                'seed': state.seed,
                'species': {
                    str(k): v.to_dict()
                    for k, v in state.species_dict.items()
                }
            }

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"Creatures exported to {export_path}")
            return True

        except Exception as e:
            print(f"Error exporting creatures: {e}")
            return False

    def import_creatures(
        self,
        import_path: str
    ) -> Optional[Dict[int, CreatureSpecies]]:
        """
        Import creature roster from file.

        Args:
            import_path: Path to import file

        Returns:
            Dictionary of creatures if successful
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)

            species_dict = {
                int(k): CreatureSpecies.from_dict(v)
                for k, v in data['species'].items()
            }

            print(f"Imported {len(species_dict)} creatures")
            return species_dict

        except Exception as e:
            print(f"Error importing creatures: {e}")
            return None
