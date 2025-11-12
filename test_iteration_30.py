"""
Test Suite for Iteration 30 - NPC Data Externalization

This test suite validates the NPC data externalization system, including:
- NPCLoader functionality
- JSON data loading
- NPC object creation from JSON
- NPCRegistry integration
- Data validation
- Backward compatibility
"""

import unittest
import json
import os
from genemon.data.npc_loader import NPCLoader
from genemon.world.npc import NPCRegistry, NPC, Dialogue


class TestNPCLoader(unittest.TestCase):
    """Test NPCLoader class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = NPCLoader()

    def test_npc_loader_initialization(self):
        """Test that NPCLoader initializes correctly."""
        self.assertIsNotNone(self.loader)
        self.assertTrue(os.path.exists(self.loader.data_file))
        self.assertTrue(self.loader.data_file.endswith('npcs.json'))

    def test_load_npc_data(self):
        """Test loading NPC data from JSON file."""
        npc_data = self.loader.load_npc_data()

        self.assertIsInstance(npc_data, dict)
        self.assertGreater(len(npc_data), 0, "Should load at least one NPC")

        # Check that we loaded the expected number of NPCs (52)
        self.assertEqual(len(npc_data), 52, "Should load exactly 52 NPCs")

    def test_npc_data_structure(self):
        """Test that loaded NPC data has correct structure."""
        npc_data = self.loader.load_npc_data()

        # Test a specific NPC (Professor)
        prof = npc_data.get('prof_oak')
        self.assertIsNotNone(prof)
        self.assertEqual(prof['name'], 'Prof. Cypress')
        self.assertEqual(prof['location_id'], 'town_starter')
        self.assertEqual(prof['x'], 5)
        self.assertEqual(prof['y'], 5)
        self.assertEqual(prof['sprite'], 'P')
        self.assertIsInstance(prof['dialogues'], list)
        self.assertFalse(prof['is_trainer'])

    def test_create_npc_from_data(self):
        """Test creating NPC object from data dictionary."""
        npc_data = self.loader.load_npc_data()
        prof_data = npc_data['prof_oak']

        prof = self.loader.create_npc_from_data(prof_data)

        self.assertIsInstance(prof, NPC)
        self.assertEqual(prof.id, 'prof_oak')
        self.assertEqual(prof.name, 'Prof. Cypress')
        self.assertEqual(prof.location_id, 'town_starter')
        self.assertEqual(prof.x, 5)
        self.assertEqual(prof.y, 5)
        self.assertEqual(prof.sprite, 'P')
        self.assertFalse(prof.is_trainer)
        self.assertIsInstance(prof.dialogues, list)
        self.assertGreater(len(prof.dialogues), 0)
        self.assertIsInstance(prof.dialogues[0], Dialogue)

    def test_load_all_npcs(self):
        """Test loading all NPCs and creating NPC objects."""
        npcs = self.loader.load_all_npcs()

        self.assertIsInstance(npcs, dict)
        self.assertEqual(len(npcs), 52, "Should create 52 NPC objects")

        # All values should be NPC instances
        for npc_id, npc in npcs.items():
            self.assertIsInstance(npc, NPC, f"NPC {npc_id} should be an NPC instance")

    def test_get_gym_leaders(self):
        """Test filtering gym leader NPCs."""
        gym_leaders = self.loader.get_gym_leaders()

        self.assertIsInstance(gym_leaders, list)
        self.assertEqual(len(gym_leaders), 8, "Should have 8 gym leaders")

        # All should be gym leaders
        for leader in gym_leaders:
            self.assertTrue(leader.is_gym_leader)
            self.assertIsNotNone(leader.specialty_type)
            self.assertIsNotNone(leader.badge_id)
            self.assertIsNotNone(leader.badge_name)
            self.assertIsNotNone(leader.badge_description)

    def test_get_trainers(self):
        """Test filtering trainer NPCs."""
        trainers = self.loader.get_trainers()

        self.assertIsInstance(trainers, list)
        self.assertGreater(len(trainers), 0, "Should have at least one trainer")

        # All should be trainers
        for trainer in trainers:
            self.assertTrue(trainer.is_trainer)

    def test_get_shopkeepers(self):
        """Test filtering shopkeeper NPCs."""
        shopkeepers = self.loader.get_shopkeepers()

        self.assertIsInstance(shopkeepers, list)
        self.assertGreater(len(shopkeepers), 0, "Should have at least one shopkeeper")

        # All should be shopkeepers with inventory
        for shopkeeper in shopkeepers:
            self.assertTrue(shopkeeper.is_shopkeeper)
            self.assertIsInstance(shopkeeper.shop_inventory, list)
            self.assertGreater(len(shopkeeper.shop_inventory), 0)

    def test_get_healers(self):
        """Test filtering healer NPCs."""
        healers = self.loader.get_healers()

        self.assertIsInstance(healers, list)
        self.assertGreater(len(healers), 0, "Should have at least one healer")

        # All should be healers
        for healer in healers:
            self.assertTrue(healer.is_healer)

    def test_get_npcs_by_location(self):
        """Test filtering NPCs by location."""
        # Test starter town
        starter_npcs = self.loader.get_npcs_by_location('town_starter')
        self.assertGreater(len(starter_npcs), 0, "Starter town should have NPCs")

        # Test Elite Hall
        elite_npcs = self.loader.get_npcs_by_location('elite_hall')
        self.assertGreaterEqual(len(elite_npcs), 6, "Elite Hall should have Elite Four + Champion + Nurse")

    def test_validate_npc_data(self):
        """Test NPC data validation."""
        errors = self.loader.validate_npc_data()

        # Should have no validation errors
        if errors:
            print("\nValidation errors found:")
            for error in errors:
                print(f"  - {error}")

        self.assertEqual(len(errors), 0, "NPC data should pass validation")


class TestNPCRegistry(unittest.TestCase):
    """Test NPCRegistry with JSON loading."""

    def test_npc_registry_json_mode(self):
        """Test NPCRegistry loading from JSON."""
        registry = NPCRegistry(use_json=True)

        self.assertIsInstance(registry.npcs, dict)
        self.assertEqual(len(registry.npcs), 52, "Should load 52 NPCs from JSON")

    def test_npc_registry_legacy_mode(self):
        """Test NPCRegistry using legacy hardcoded mode."""
        registry = NPCRegistry(use_json=False)

        self.assertIsInstance(registry.npcs, dict)
        self.assertEqual(len(registry.npcs), 52, "Should create 52 NPCs from hardcoded data")

    def test_json_vs_legacy_consistency(self):
        """Test that JSON and legacy modes produce equivalent NPCs."""
        json_registry = NPCRegistry(use_json=True)
        legacy_registry = NPCRegistry(use_json=False)

        # Should have same number of NPCs
        self.assertEqual(len(json_registry.npcs), len(legacy_registry.npcs))

        # Check a few specific NPCs for consistency
        test_npc_ids = ['prof_oak', 'gym_leader_1', 'elite_1', 'champion']

        for npc_id in test_npc_ids:
            json_npc = json_registry.get_npc(npc_id)
            legacy_npc = legacy_registry.get_npc(npc_id)

            self.assertIsNotNone(json_npc, f"JSON NPC {npc_id} should exist")
            self.assertIsNotNone(legacy_npc, f"Legacy NPC {npc_id} should exist")

            # Compare basic attributes
            self.assertEqual(json_npc.id, legacy_npc.id)
            self.assertEqual(json_npc.name, legacy_npc.name)
            self.assertEqual(json_npc.location_id, legacy_npc.location_id)
            self.assertEqual(json_npc.x, legacy_npc.x)
            self.assertEqual(json_npc.y, legacy_npc.y)
            self.assertEqual(json_npc.sprite, legacy_npc.sprite)
            self.assertEqual(json_npc.is_trainer, legacy_npc.is_trainer)
            self.assertEqual(json_npc.is_shopkeeper, legacy_npc.is_shopkeeper)
            self.assertEqual(json_npc.is_healer, legacy_npc.is_healer)
            self.assertEqual(json_npc.is_gym_leader, legacy_npc.is_gym_leader)

    def test_get_npc_by_id(self):
        """Test retrieving specific NPC by ID."""
        registry = NPCRegistry(use_json=True)

        prof = registry.get_npc('prof_oak')
        self.assertIsNotNone(prof)
        self.assertEqual(prof.name, 'Prof. Cypress')

        # Test non-existent NPC
        fake = registry.get_npc('fake_npc')
        self.assertIsNone(fake)

    def test_get_npcs_at_location(self):
        """Test retrieving NPCs by location."""
        registry = NPCRegistry(use_json=True)

        # Test Elite Hall (should have Elite Four + Champion + Nurse = 6)
        elite_npcs = registry.get_npcs_at_location('elite_hall')
        self.assertEqual(len(elite_npcs), 6, "Elite Hall should have 6 NPCs")

        # Test Starter Town
        starter_npcs = registry.get_npcs_at_location('town_starter')
        self.assertGreater(len(starter_npcs), 0, "Starter town should have NPCs")


class TestNPCDataIntegrity(unittest.TestCase):
    """Test NPC data integrity and completeness."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = NPCLoader()
        self.npcs = self.loader.load_all_npcs()

    def test_all_gym_leaders_present(self):
        """Test that all 8 gym leaders are present."""
        gym_leader_ids = [
            'gym_leader_1', 'gym_leader_2', 'gym_leader_3', 'gym_leader_4',
            'gym_leader_5', 'gym_leader_6', 'gym_leader_7', 'gym_leader_8'
        ]

        for gym_id in gym_leader_ids:
            self.assertIn(gym_id, self.npcs, f"Gym leader {gym_id} should exist")
            gym_leader = self.npcs[gym_id]
            self.assertTrue(gym_leader.is_gym_leader)
            self.assertTrue(gym_leader.is_trainer)
            self.assertIsNotNone(gym_leader.specialty_type)
            self.assertIsNotNone(gym_leader.badge_id)

    def test_all_elite_four_present(self):
        """Test that all Elite Four members are present."""
        elite_ids = ['elite_1', 'elite_2', 'elite_3', 'elite_4']

        for elite_id in elite_ids:
            self.assertIn(elite_id, self.npcs, f"Elite Four member {elite_id} should exist")
            elite = self.npcs[elite_id]
            self.assertTrue(elite.is_trainer)

    def test_champion_present(self):
        """Test that Champion is present."""
        self.assertIn('champion', self.npcs)
        champion = self.npcs['champion']
        self.assertEqual(champion.name, 'Champion Aurora')
        self.assertTrue(champion.is_trainer)

    def test_legendary_encounters_present(self):
        """Test that all 6 legendary encounters are present."""
        legendary_ids = [
            'legendary_encounter_1', 'legendary_encounter_2', 'legendary_encounter_3',
            'legendary_encounter_4', 'legendary_encounter_5', 'legendary_encounter_6'
        ]

        for legendary_id in legendary_ids:
            self.assertIn(legendary_id, self.npcs, f"Legendary encounter {legendary_id} should exist")
            legendary = self.npcs[legendary_id]
            self.assertTrue(legendary.is_trainer)
            self.assertEqual(legendary.location_id, 'legendary_sanctuary')

    def test_all_npcs_have_dialogues(self):
        """Test that all NPCs have at least one dialogue."""
        for npc_id, npc in self.npcs.items():
            self.assertGreater(len(npc.dialogues), 0, f"NPC {npc_id} should have at least one dialogue")
            # Check that dialogues are properly formed
            for dialogue in npc.dialogues:
                self.assertIsInstance(dialogue, Dialogue)
                self.assertIsInstance(dialogue.text, str)
                self.assertGreater(len(dialogue.text), 0)

    def test_shopkeepers_have_inventory(self):
        """Test that all shopkeepers have shop inventory."""
        shopkeepers = self.loader.get_shopkeepers()

        for shopkeeper in shopkeepers:
            self.assertIsInstance(shopkeeper.shop_inventory, list)
            self.assertGreater(len(shopkeeper.shop_inventory), 0,
                             f"Shopkeeper {shopkeeper.id} should have inventory")


def run_tests():
    """Run all tests and print results."""
    print("\n" + "="*60)
    print("ITERATION 30 TEST SUITE - NPC DATA EXTERNALIZATION")
    print("="*60 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNPCLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestNPCRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestNPCDataIntegrity))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    total_tests = result.testsRun
    passed = total_tests - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    print(f"TOTAL: {passed}/{total_tests} tests passed ({(passed/total_tests*100):.1f}%)")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")

    print("="*60 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
