"""
Comprehensive tests for the trading system.

Tests cover:
- Trade package creation and serialization
- Creature export functionality
- Creature import functionality
- Trade history tracking
- Cross-save species handling
- Trade file management
"""

import unittest
import os
import shutil
import json
from datetime import datetime
from genemon.core.trading import TradeManager, TradePackage, TradeRecord
from genemon.core.creature import Creature, CreatureSpecies, Move, Ability, CreatureStats
from genemon.core.save_system import GameState, SaveManager


class TestTradeRecord(unittest.TestCase):
    """Test trade record functionality."""

    def test_trade_record_creation(self):
        """Test creating a trade record."""
        record = TradeRecord(
            trade_id="test_001",
            timestamp="2025-01-15T10:30:00",
            from_save="save1",
            to_save="save2",
            creature_name="Flamewing",
            creature_level=25,
            species_id=4
        )

        self.assertEqual(record.trade_id, "test_001")
        self.assertEqual(record.from_save, "save1")
        self.assertEqual(record.to_save, "save2")
        self.assertEqual(record.creature_name, "Flamewing")
        self.assertEqual(record.creature_level, 25)
        self.assertEqual(record.species_id, 4)

    def test_trade_record_serialization(self):
        """Test trade record to_dict and from_dict."""
        record = TradeRecord(
            trade_id="test_001",
            timestamp="2025-01-15T10:30:00",
            from_save="save1",
            to_save="save2",
            creature_name="Flamewing",
            creature_level=25,
            species_id=4
        )

        # Serialize
        data = record.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['trade_id'], "test_001")
        self.assertEqual(data['creature_name'], "Flamewing")

        # Deserialize
        restored = TradeRecord.from_dict(data)
        self.assertEqual(restored.trade_id, record.trade_id)
        self.assertEqual(restored.creature_name, record.creature_name)
        self.assertEqual(restored.creature_level, record.creature_level)

    def test_trade_record_string_representation(self):
        """Test trade record __str__ method."""
        record = TradeRecord(
            trade_id="test_001",
            timestamp="2025-01-15T10:30:00",
            from_save="save1",
            to_save="save2",
            creature_name="Flamewing",
            creature_level=25,
            species_id=4
        )

        str_repr = str(record)
        self.assertIn("Flamewing", str_repr)
        self.assertIn("25", str_repr)
        self.assertIn("save1", str_repr)
        self.assertIn("save2", str_repr)


class TestTradePackage(unittest.TestCase):
    """Test trade package functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test move
        test_move = Move("Ember", "Flame", 40, 100, 25, 25, "A flame attack")

        # Create a test ability
        test_ability = Ability("Blaze", "power_boost", 1.5)

        # Create a test species
        self.species = CreatureSpecies(
            id=25,
            name="Testimon",
            types=["Flame"],
            base_stats=CreatureStats(50, 60, 50, 70, 55),
            moves=[test_move],
            flavor_text="A test creature.",
            evolution_level=None,
            evolves_into=None,
            sprite_data=None,
            learnset={},
            tm_compatible=None,
            is_legendary=False,
            ability=test_ability
        )

        # Create a test creature
        self.creature = Creature(self.species, level=20)
        self.creature.nickname = "Testy"

    def test_trade_package_creation(self):
        """Test creating a trade package."""
        package = TradePackage(
            creature_data=self.creature.to_dict(),
            species_data=self.species.to_dict(),
            source_save="test_save",
            export_timestamp="2025-01-15T10:30:00"
        )

        self.assertEqual(package.source_save, "test_save")
        self.assertEqual(package.export_timestamp, "2025-01-15T10:30:00")
        self.assertIsInstance(package.creature_data, dict)
        self.assertIsInstance(package.species_data, dict)

    def test_trade_package_serialization(self):
        """Test trade package to_dict and from_dict."""
        package = TradePackage(
            creature_data=self.creature.to_dict(),
            species_data=self.species.to_dict(),
            source_save="test_save",
            export_timestamp="2025-01-15T10:30:00"
        )

        # Serialize
        data = package.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['version'], '1.0.0')
        self.assertIn('creature', data)
        self.assertIn('species', data)

        # Deserialize
        restored = TradePackage.from_dict(data)
        self.assertEqual(restored.source_save, package.source_save)
        self.assertEqual(restored.export_timestamp, package.export_timestamp)

    def test_trade_package_unpack(self):
        """Test unpacking a trade package."""
        package = TradePackage(
            creature_data=self.creature.to_dict(),
            species_data=self.species.to_dict(),
            source_save="test_save",
            export_timestamp="2025-01-15T10:30:00"
        )

        # Unpack with empty species dict
        species_dict = {}
        creature, species = package.unpack(species_dict)

        # Verify creature
        self.assertIsInstance(creature, Creature)
        self.assertEqual(creature.level, 20)
        self.assertEqual(creature.nickname, "Testy")

        # Verify species
        self.assertIsInstance(species, CreatureSpecies)
        self.assertEqual(species.id, 25)
        self.assertEqual(species.name, "Testimon")


class TestTradeManager(unittest.TestCase):
    """Test trade manager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = "test_trades"
        self.trade_manager = TradeManager(trade_dir=self.test_dir)

        # Create test move and ability
        test_move = Move("Ember", "Flame", 40, 100, 25, 25, "A flame attack")
        test_ability = Ability("Blaze", "power_boost", 1.5)

        # Create test species
        self.species = CreatureSpecies(
            id=25,
            name="Testimon",
            types=["Flame"],
            base_stats=CreatureStats(50, 60, 50, 70, 55),
            moves=[test_move],
            flavor_text="A test creature.",
            evolution_level=None,
            evolves_into=None,
            sprite_data=None,
            learnset={},
            tm_compatible=None,
            is_legendary=False,
            ability=test_ability
        )

        self.creature = Creature(self.species, level=20)
        self.creature.nickname = "Testy"

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_trade_directory_creation(self):
        """Test that trade directory is created."""
        self.assertTrue(os.path.exists(self.test_dir))

    def test_export_creature(self):
        """Test exporting a creature."""
        filepath = self.trade_manager.export_creature(
            self.creature,
            "test_save",
            "test_export"
        )

        # Verify file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.trade'))

        # Verify file contents
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['version'], '1.0.0')
        self.assertEqual(data['source_save'], 'test_save')
        self.assertIn('creature', data)
        self.assertIn('species', data)

    def test_export_creature_auto_filename(self):
        """Test exporting with automatic filename generation."""
        filepath = self.trade_manager.export_creature(
            self.creature,
            "test_save"
        )

        # Verify file was created with auto-generated name
        self.assertTrue(os.path.exists(filepath))
        self.assertIn("Testimon", filepath)
        self.assertIn("20", filepath)

    def test_import_creature(self):
        """Test importing a creature."""
        # First export a creature
        filepath = self.trade_manager.export_creature(
            self.creature,
            "source_save"
        )

        # Import the creature
        species_dict = {}
        creature, species = self.trade_manager.import_creature(
            filepath,
            species_dict,
            "target_save"
        )

        # Verify creature
        self.assertIsInstance(creature, Creature)
        self.assertEqual(creature.level, 20)
        self.assertEqual(creature.nickname, "Testy")

        # Verify species
        self.assertIsInstance(species, CreatureSpecies)
        self.assertEqual(species.name, "Testimon")

    def test_import_creature_creates_trade_record(self):
        """Test that importing creates a trade history record."""
        # Export and import
        filepath = self.trade_manager.export_creature(
            self.creature,
            "source_save"
        )

        species_dict = {}
        self.trade_manager.import_creature(
            filepath,
            species_dict,
            "target_save"
        )

        # Check trade history
        history = self.trade_manager.get_trade_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].creature_name, "Testimon")
        self.assertEqual(history[0].from_save, "source_save")
        self.assertEqual(history[0].to_save, "target_save")

    def test_import_nonexistent_file(self):
        """Test importing from nonexistent file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.trade_manager.import_creature(
                "nonexistent.trade",
                {},
                "target_save"
            )

    def test_list_trade_files(self):
        """Test listing available trade files."""
        # Export a couple creatures
        self.trade_manager.export_creature(
            self.creature,
            "save1"
        )

        creature2 = Creature(self.species, level=30)
        self.trade_manager.export_creature(
            creature2,
            "save2"
        )

        # List files
        files = self.trade_manager.list_trade_files()

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]['creature_name'], "Testimon")
        self.assertEqual(files[1]['creature_name'], "Testimon")

    def test_delete_trade_file(self):
        """Test deleting a trade file."""
        filepath = self.trade_manager.export_creature(
            self.creature,
            "test_save"
        )

        # Verify file exists
        self.assertTrue(os.path.exists(filepath))

        # Delete file
        result = self.trade_manager.delete_trade_file(filepath)
        self.assertTrue(result)

        # Verify file is gone
        self.assertFalse(os.path.exists(filepath))

    def test_delete_nonexistent_file(self):
        """Test deleting nonexistent file returns False."""
        result = self.trade_manager.delete_trade_file("nonexistent.trade")
        self.assertFalse(result)

    def test_get_trade_stats(self):
        """Test getting trade statistics."""
        # Initially no trades
        stats = self.trade_manager.get_trade_stats()
        self.assertEqual(stats['total_trades'], 0)

        # Export and import
        filepath = self.trade_manager.export_creature(
            self.creature,
            "save1"
        )

        self.trade_manager.import_creature(
            filepath,
            {},
            "save2"
        )

        # Check stats
        stats = self.trade_manager.get_trade_stats()
        self.assertEqual(stats['total_trades'], 1)
        self.assertEqual(stats['unique_saves'], 2)  # save1 and save2
        self.assertEqual(stats['unique_species'], 1)

    def test_trade_history_persistence(self):
        """Test that trade history persists across manager instances."""
        # Create a trade
        filepath = self.trade_manager.export_creature(
            self.creature,
            "save1"
        )

        self.trade_manager.import_creature(
            filepath,
            {},
            "save2"
        )

        # Create new manager instance (should load history)
        new_manager = TradeManager(trade_dir=self.test_dir)
        history = new_manager.get_trade_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].creature_name, "Testimon")


class TestTradeIntegration(unittest.TestCase):
    """Integration tests for complete trading workflows."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = "test_trades_integration"
        self.trade_manager = TradeManager(trade_dir=self.test_dir)

        # Create two different species
        move1 = Move("Ember", "Flame", 40, 100, 25, 25, "A flame attack")
        move2 = Move("Bubble", "Aqua", 40, 100, 30, 30, "An aqua attack")
        ability1 = Ability("Blaze", "power_boost", 1.5)
        ability2 = Ability("Torrent", "power_boost", 1.5)

        self.species1 = CreatureSpecies(
            id=1,
            name="Flamewing",
            types=["Flame"],
            base_stats=CreatureStats(50, 60, 50, 70, 55),
            moves=[move1],
            flavor_text="A flame creature.",
            evolution_level=None,
            evolves_into=None,
            sprite_data=None,
            learnset={},
            tm_compatible=None,
            is_legendary=False,
            ability=ability1
        )

        self.species2 = CreatureSpecies(
            id=2,
            name="Aquafin",
            types=["Aqua"],
            base_stats=CreatureStats(55, 50, 60, 70, 50),
            moves=[move2],
            flavor_text="An aqua creature.",
            evolution_level=None,
            evolves_into=None,
            sprite_data=None,
            learnset={},
            tm_compatible=None,
            is_legendary=False,
            ability=ability2
        )

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_complete_trading_workflow(self):
        """Test complete export-import workflow."""
        # Create creature from save1
        creature1 = Creature(self.species1, level=25)
        creature1.nickname = "Blaze"

        # Export from save1
        filepath = self.trade_manager.export_creature(
            creature1,
            "save1",
            "blaze_trade"
        )

        # Import to save2 (which has different species)
        save2_species = {2: self.species2}
        imported_creature, imported_species = self.trade_manager.import_creature(
            filepath,
            save2_species,
            "save2"
        )

        # Verify creature maintains its properties
        self.assertEqual(imported_creature.level, 25)
        self.assertEqual(imported_creature.nickname, "Blaze")

        # Verify species is correctly reconstructed
        self.assertEqual(imported_species.id, 1)
        self.assertEqual(imported_species.name, "Flamewing")

    def test_multiple_trades_between_saves(self):
        """Test trading multiple creatures between saves."""
        # Create creatures
        creature1 = Creature(self.species1, level=20)
        creature2 = Creature(self.species2, level=25)

        # Export from different saves
        file1 = self.trade_manager.export_creature(creature1, "save1")
        file2 = self.trade_manager.export_creature(creature2, "save2")

        # Import to opposite saves
        c1_imported, s1 = self.trade_manager.import_creature(file1, {}, "save2")
        c2_imported, s2 = self.trade_manager.import_creature(file2, {}, "save1")

        # Verify trade history
        history = self.trade_manager.get_trade_history()
        self.assertEqual(len(history), 2)

        # Verify stats
        stats = self.trade_manager.get_trade_stats()
        self.assertEqual(stats['total_trades'], 2)
        self.assertEqual(stats['unique_species'], 2)


if __name__ == '__main__':
    unittest.main()
