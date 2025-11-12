"""
Trading system for exchanging creatures between save files.

This module allows players to:
- Export creatures from their team or storage
- Import creatures from other save files
- Trade creatures between different save files
- Track trade history
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .creature import Creature, CreatureSpecies


class TradeRecord:
    """
    Record of a single trade transaction.
    """

    def __init__(
        self,
        trade_id: str,
        timestamp: str,
        from_save: str,
        to_save: str,
        creature_name: str,
        creature_level: int,
        species_id: int
    ):
        """
        Initialize a trade record.

        Args:
            trade_id: Unique identifier for this trade
            timestamp: ISO format timestamp of when trade occurred
            from_save: Name of save file creature came from
            to_save: Name of save file creature went to
            creature_name: Name of the traded creature
            creature_level: Level of the traded creature
            species_id: Species ID of the traded creature
        """
        self.trade_id = trade_id
        self.timestamp = timestamp
        self.from_save = from_save
        self.to_save = to_save
        self.creature_name = creature_name
        self.creature_level = creature_level
        self.species_id = species_id

    def to_dict(self) -> dict:
        """Serialize trade record to dictionary."""
        return {
            'trade_id': self.trade_id,
            'timestamp': self.timestamp,
            'from_save': self.from_save,
            'to_save': self.to_save,
            'creature_name': self.creature_name,
            'creature_level': self.creature_level,
            'species_id': self.species_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TradeRecord':
        """Deserialize trade record from dictionary."""
        return cls(
            trade_id=data['trade_id'],
            timestamp=data['timestamp'],
            from_save=data['from_save'],
            to_save=data['to_save'],
            creature_name=data['creature_name'],
            creature_level=data['creature_level'],
            species_id=data['species_id']
        )

    def __str__(self) -> str:
        """String representation of trade record."""
        return (
            f"{self.timestamp}: {self.creature_name} (Lv.{self.creature_level}) "
            f"from {self.from_save} to {self.to_save}"
        )


class TradePackage:
    """
    A packaged creature ready for export/import.

    Contains all necessary data to reconstruct a creature in a different save file,
    even if the species don't match between saves.
    """

    def __init__(
        self,
        creature_data: dict,
        species_data: dict,
        source_save: str,
        export_timestamp: str
    ):
        """
        Initialize a trade package.

        Args:
            creature_data: Serialized creature data
            species_data: Serialized species data
            source_save: Name of the save file this creature came from
            export_timestamp: ISO timestamp of when creature was exported
        """
        self.creature_data = creature_data
        self.species_data = species_data
        self.source_save = source_save
        self.export_timestamp = export_timestamp

    def to_dict(self) -> dict:
        """Serialize trade package to dictionary."""
        return {
            'version': '1.0.0',
            'creature': self.creature_data,
            'species': self.species_data,
            'source_save': self.source_save,
            'export_timestamp': self.export_timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TradePackage':
        """Deserialize trade package from dictionary."""
        return cls(
            creature_data=data['creature'],
            species_data=data['species'],
            source_save=data['source_save'],
            export_timestamp=data['export_timestamp']
        )

    def unpack(self, target_species_dict: Dict[int, CreatureSpecies]) -> Tuple[Creature, CreatureSpecies]:
        """
        Unpack the trade package into a creature and species.

        Args:
            target_species_dict: Species dictionary from target save file

        Returns:
            Tuple of (Creature instance, CreatureSpecies instance)
        """
        # Reconstruct species from packaged data
        species = CreatureSpecies.from_dict(self.species_data)

        # Reconstruct creature using the species
        creature = Creature.from_dict(self.creature_data, species)

        return creature, species


class TradeManager:
    """
    Manages creature trading between save files.
    """

    def __init__(self, trade_dir: str = "saves/trades"):
        """
        Initialize trade manager.

        Args:
            trade_dir: Directory to store trade files and history
        """
        self.trade_dir = trade_dir
        self.trade_history_path = os.path.join(trade_dir, "trade_history.json")
        os.makedirs(trade_dir, exist_ok=True)

        # Load trade history
        self.trade_history: List[TradeRecord] = self._load_trade_history()

    def _load_trade_history(self) -> List[TradeRecord]:
        """Load trade history from file."""
        if not os.path.exists(self.trade_history_path):
            return []

        try:
            with open(self.trade_history_path, 'r') as f:
                data = json.load(f)
                return [TradeRecord.from_dict(record) for record in data.get('trades', [])]
        except (json.JSONDecodeError, KeyError, IOError):
            return []

    def _save_trade_history(self):
        """Save trade history to file."""
        data = {
            'version': '1.0.0',
            'trades': [record.to_dict() for record in self.trade_history]
        }
        with open(self.trade_history_path, 'w') as f:
            json.dump(data, f, indent=2)

    def export_creature(
        self,
        creature: Creature,
        source_save_name: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Export a creature to a trade file.

        Args:
            creature: The creature to export
            source_save_name: Name of the save file creature is from
            filename: Optional custom filename (without extension)

        Returns:
            Path to the created trade file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{creature.species.name}_{creature.level}_{timestamp}"

        # Ensure .trade extension
        if not filename.endswith('.trade'):
            filename += '.trade'

        filepath = os.path.join(self.trade_dir, filename)

        # Create trade package
        package = TradePackage(
            creature_data=creature.to_dict(),
            species_data=creature.species.to_dict(),
            source_save=source_save_name,
            export_timestamp=datetime.now().isoformat()
        )

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(package.to_dict(), f, indent=2)

        return filepath

    def import_creature(
        self,
        trade_filepath: str,
        target_species_dict: Dict[int, CreatureSpecies],
        target_save_name: str
    ) -> Tuple[Creature, CreatureSpecies]:
        """
        Import a creature from a trade file.

        Args:
            trade_filepath: Path to the .trade file
            target_species_dict: Species dictionary from target save
            target_save_name: Name of the save file importing to

        Returns:
            Tuple of (Creature instance, CreatureSpecies instance)

        Raises:
            FileNotFoundError: If trade file doesn't exist
            ValueError: If trade file is invalid
        """
        if not os.path.exists(trade_filepath):
            raise FileNotFoundError(f"Trade file not found: {trade_filepath}")

        try:
            with open(trade_filepath, 'r') as f:
                data = json.load(f)

            # Load trade package
            package = TradePackage.from_dict(data)

            # Unpack creature and species
            creature, species = package.unpack(target_species_dict)

            # Record trade in history
            trade_record = TradeRecord(
                trade_id=f"{package.source_save}_{target_save_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                from_save=package.source_save,
                to_save=target_save_name,
                creature_name=creature.species.name,
                creature_level=creature.level,
                species_id=creature.species.id
            )
            self.trade_history.append(trade_record)
            self._save_trade_history()

            return creature, species

        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid trade file format: {e}")

    def list_trade_files(self) -> List[Dict[str, str]]:
        """
        List all available trade files.

        Returns:
            List of dictionaries with trade file information
        """
        trade_files = []

        if not os.path.exists(self.trade_dir):
            return trade_files

        for filename in os.listdir(self.trade_dir):
            if not filename.endswith('.trade'):
                continue

            filepath = os.path.join(self.trade_dir, filename)

            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                package = TradePackage.from_dict(data)
                creature_data = package.creature_data
                species_data = package.species_data

                trade_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'creature_name': species_data['name'],
                    'level': creature_data['level'],
                    'source_save': package.source_save,
                    'export_date': package.export_timestamp
                })
            except (json.JSONDecodeError, KeyError):
                # Skip invalid trade files
                continue

        return sorted(trade_files, key=lambda x: x['export_date'], reverse=True)

    def get_trade_history(self, limit: Optional[int] = None) -> List[TradeRecord]:
        """
        Get trade history.

        Args:
            limit: Maximum number of records to return (None for all)

        Returns:
            List of trade records, most recent first
        """
        history = sorted(self.trade_history, key=lambda x: x.timestamp, reverse=True)

        if limit is not None:
            return history[:limit]

        return history

    def delete_trade_file(self, filepath: str) -> bool:
        """
        Delete a trade file.

        Args:
            filepath: Path to the trade file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except OSError:
            return False

    def get_trade_stats(self) -> Dict[str, int]:
        """
        Get statistics about trades.

        Returns:
            Dictionary with trade statistics
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'unique_saves': 0,
                'unique_species': 0
            }

        unique_saves = set()
        unique_species = set()

        for record in self.trade_history:
            unique_saves.add(record.from_save)
            unique_saves.add(record.to_save)
            unique_species.add(record.species_id)

        return {
            'total_trades': len(self.trade_history),
            'unique_saves': len(unique_saves),
            'unique_species': len(unique_species)
        }
