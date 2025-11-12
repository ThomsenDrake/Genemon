"""
NPC Data Loader - Loads NPC data from JSON files.

This module provides utilities for loading and managing NPC data from external
JSON files, enabling easier modding and data management.
"""

import json
import os
from typing import List, Dict, Optional
from ..world.npc import NPC, Dialogue


class NPCLoader:
    """
    Utility class for loading NPC data from JSON files.

    This class handles:
    - Loading NPC data from JSON files
    - Converting JSON data to NPC objects
    - Validation of NPC data
    - Error handling for malformed data
    """

    def __init__(self, data_file: str = None):
        """
        Initialize NPC loader.

        Args:
            data_file: Path to JSON file containing NPC data.
                      Defaults to 'genemon/data/npcs.json'
        """
        if data_file is None:
            # Default to npcs.json in the same directory as this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, 'npcs.json')

        self.data_file = data_file
        self._npc_data: Optional[Dict] = None

    def load_npc_data(self) -> Dict[str, Dict]:
        """
        Load NPC data from JSON file.

        Returns:
            Dictionary mapping NPC IDs to NPC data dictionaries

        Raises:
            FileNotFoundError: If the NPC data file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"NPC data file not found: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert list to dictionary keyed by NPC ID
        npc_dict = {}
        for npc_data in data.get('npcs', []):
            npc_id = npc_data.get('id')
            if npc_id:
                npc_dict[npc_id] = npc_data

        self._npc_data = npc_dict
        return npc_dict

    def create_npc_from_data(self, npc_data: Dict) -> NPC:
        """
        Create an NPC object from JSON data dictionary.

        Args:
            npc_data: Dictionary containing NPC data

        Returns:
            NPC object initialized with the provided data
        """
        # Convert dialogue dictionaries to Dialogue objects
        dialogues = []
        for dialogue_data in npc_data.get('dialogues', []):
            dialogues.append(Dialogue(
                text=dialogue_data['text'],
                condition=dialogue_data.get('condition')
            ))

        # Create NPC with all fields
        npc = NPC(
            id=npc_data['id'],
            name=npc_data['name'],
            location_id=npc_data['location_id'],
            x=npc_data['x'],
            y=npc_data['y'],
            sprite=npc_data.get('sprite', '@'),
            dialogues=dialogues,
            is_trainer=npc_data.get('is_trainer', False),
            is_shopkeeper=npc_data.get('is_shopkeeper', False),
            shop_inventory=npc_data.get('shop_inventory', []),
            is_healer=npc_data.get('is_healer', False),
            specialty_type=npc_data.get('specialty_type'),
            is_gym_leader=npc_data.get('is_gym_leader', False),
            badge_id=npc_data.get('badge_id'),
            badge_name=npc_data.get('badge_name'),
            badge_description=npc_data.get('badge_description')
        )

        return npc

    def load_all_npcs(self) -> Dict[str, NPC]:
        """
        Load all NPCs from the JSON file and create NPC objects.

        Returns:
            Dictionary mapping NPC IDs to NPC objects

        Raises:
            FileNotFoundError: If the NPC data file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        npc_data_dict = self.load_npc_data()

        npcs = {}
        for npc_id, npc_data in npc_data_dict.items():
            npcs[npc_id] = self.create_npc_from_data(npc_data)

        return npcs

    def get_npcs_by_location(self, location_id: str) -> List[NPC]:
        """
        Get all NPCs at a specific location.

        Args:
            location_id: ID of the location

        Returns:
            List of NPC objects at the specified location
        """
        if self._npc_data is None:
            self.load_npc_data()

        npcs = []
        for npc_data in self._npc_data.values():
            if npc_data.get('location_id') == location_id:
                npcs.append(self.create_npc_from_data(npc_data))

        return npcs

    def get_gym_leaders(self) -> List[NPC]:
        """
        Get all gym leader NPCs.

        Returns:
            List of gym leader NPC objects
        """
        if self._npc_data is None:
            self.load_npc_data()

        gym_leaders = []
        for npc_data in self._npc_data.values():
            if npc_data.get('is_gym_leader', False):
                gym_leaders.append(self.create_npc_from_data(npc_data))

        return gym_leaders

    def get_trainers(self) -> List[NPC]:
        """
        Get all trainer NPCs.

        Returns:
            List of trainer NPC objects
        """
        if self._npc_data is None:
            self.load_npc_data()

        trainers = []
        for npc_data in self._npc_data.values():
            if npc_data.get('is_trainer', False):
                trainers.append(self.create_npc_from_data(npc_data))

        return trainers

    def get_shopkeepers(self) -> List[NPC]:
        """
        Get all shopkeeper NPCs.

        Returns:
            List of shopkeeper NPC objects
        """
        if self._npc_data is None:
            self.load_npc_data()

        shopkeepers = []
        for npc_data in self._npc_data.values():
            if npc_data.get('is_shopkeeper', False):
                shopkeepers.append(self.create_npc_from_data(npc_data))

        return shopkeepers

    def get_healers(self) -> List[NPC]:
        """
        Get all healer NPCs.

        Returns:
            List of healer NPC objects
        """
        if self._npc_data is None:
            self.load_npc_data()

        healers = []
        for npc_data in self._npc_data.values():
            if npc_data.get('is_healer', False):
                healers.append(self.create_npc_from_data(npc_data))

        return healers

    def validate_npc_data(self) -> List[str]:
        """
        Validate loaded NPC data for common issues.

        Returns:
            List of validation error messages (empty if all valid)
        """
        if self._npc_data is None:
            self.load_npc_data()

        errors = []

        for npc_id, npc_data in self._npc_data.items():
            # Check required fields
            required_fields = ['id', 'name', 'location_id', 'x', 'y']
            for field in required_fields:
                if field not in npc_data:
                    errors.append(f"NPC {npc_id}: Missing required field '{field}'")

            # Check gym leader data
            if npc_data.get('is_gym_leader'):
                gym_fields = ['specialty_type', 'badge_id', 'badge_name', 'badge_description']
                for field in gym_fields:
                    if not npc_data.get(field):
                        errors.append(f"Gym Leader {npc_id}: Missing field '{field}'")

            # Check shopkeeper data
            if npc_data.get('is_shopkeeper'):
                if not npc_data.get('shop_inventory'):
                    errors.append(f"Shopkeeper {npc_id}: Missing shop_inventory")

        return errors
