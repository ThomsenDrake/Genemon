#!/usr/bin/env python3
"""
Iteration 22 Test Suite - Game Functionality Verification

Tests all major systems to ensure they work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from genemon.core.creature import Creature, Move, Team, CreatureSpecies, CreatureStats, StatusEffect, Ability
from genemon.battle.engine import Battle, Weather
from genemon.creatures.generator import CreatureGenerator
from genemon.sprites.generator import SpriteGenerator
from genemon.world.map import World
from genemon.world.npc import NPCRegistry


class TestIteration22(unittest.TestCase):
    """Test suite for Iteration 22 functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test move first
        self.test_move = Move(
            name="Ember",
            type="Flame",
            power=40,
            accuracy=100,
            pp=25,
            max_pp=25,
            description="A flame attack"
        )

        # Create a simple test creature species with moves
        self.test_species = CreatureSpecies(
            id=1,
            name="Testmon",
            types=["Flame"],
            base_stats=CreatureStats(hp=45, attack=49, defense=49, special=65, speed=45),
            moves=[self.test_move],  # Species must have at least one move
            flavor_text="A test creature",
            evolution_level=None,
            evolves_into=None,
            ability=Ability(name="Blaze", description="Powers up Flame moves", effect_type="type_boost")
        )

        self.test_creature = Creature(self.test_species, level=5)

    def test_imports(self):
        """Test that all modules import successfully."""
        try:
            from genemon.core.game import Game
            from genemon.core.save_system import SaveSystem
            from genemon.battle.calculator import BattleCalculator
            from genemon.battle.status import StatusManager
            from genemon.battle.weather import WeatherManager
            from genemon.core.exceptions import GenemonError
            from genemon.core.input_validator import InputValidator, MenuBuilder
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_creature_creation(self):
        """Test creature creation."""
        self.assertEqual(self.test_creature.level, 5)
        self.assertEqual(self.test_creature.species.name, "Testmon")
        self.assertGreater(self.test_creature.max_hp, 0)
        self.assertEqual(len(self.test_creature.moves), 1)

    def test_creature_generator(self):
        """Test creature generation system."""
        generator = CreatureGenerator(seed=12345)
        creatures = generator.generate_creatures(count=10)

        self.assertEqual(len(creatures), 10)
        for creature_species in creatures:
            self.assertIsNotNone(creature_species.name)
            self.assertGreater(len(creature_species.types), 0)
            self.assertGreater(creature_species.base_hp, 0)
            self.assertGreater(creature_species.base_attack, 0)

    def test_sprite_generator(self):
        """Test sprite generation."""
        sprite_gen = SpriteGenerator(seed=12345)
        front_sprite = sprite_gen.generate_sprite(self.test_species, sprite_type="front")

        self.assertIsNotNone(front_sprite)
        self.assertEqual(len(front_sprite), sprite_gen.sprite_size)
        self.assertEqual(len(front_sprite[0]), sprite_gen.sprite_size)

    def test_battle_system(self):
        """Test basic battle functionality."""
        # Create two test creatures
        player_creature = Creature(self.test_species, level=5)
        player_creature.moves = [self.test_move]
        player_team = Team()
        player_team.add_creature(player_creature)

        opponent_creature = Creature(self.test_species, level=5)
        opponent_creature.moves = [self.test_move]
        opponent_team = Team()
        opponent_team.add_creature(opponent_creature)

        # Create battle
        battle = Battle(player_team, opponent_team, is_wild=True)

        self.assertIsNotNone(battle.player_active)
        self.assertIsNotNone(battle.opponent_active)
        self.assertEqual(battle.weather, Weather.NONE)

    def test_damage_calculation(self):
        """Test damage calculation in battle."""
        player_creature = Creature(self.test_species, level=10)
        player_creature.moves = [self.test_move]
        player_team = Team()
        player_team.add_creature(player_creature)

        opponent_creature = Creature(self.test_species, level=10)
        opponent_creature.moves = [self.test_move]
        opponent_team = Team()
        opponent_team.add_creature(opponent_creature)

        battle = Battle(player_team, opponent_team, is_wild=True)

        # Calculate damage using battle engine
        damage = battle._calculate_damage(
            player_creature,
            opponent_creature,
            self.test_move,
            is_critical=False
        )

        self.assertGreater(damage, 0)
        self.assertLess(damage, opponent_creature.max_hp)

    def test_status_effects(self):
        """Test status effect application."""
        creature = Creature(self.test_species, level=10)

        # Test paralysis
        creature.apply_status(StatusEffect.PARALYSIS)
        self.assertEqual(creature.status, StatusEffect.PARALYSIS)

        # Test status cure
        creature.cure_status()
        self.assertEqual(creature.status, StatusEffect.NONE)

    def test_weather_system(self):
        """Test weather functionality."""
        player_creature = Creature(self.test_species, level=10)
        player_creature.moves = [self.test_move]
        player_team = Team()
        player_team.add_creature(player_creature)

        opponent_creature = Creature(self.test_species, level=10)
        opponent_creature.moves = [self.test_move]
        opponent_team = Team()
        opponent_team.add_creature(opponent_creature)

        battle = Battle(player_team, opponent_team, is_wild=True)

        # Test weather setting
        battle.set_weather(Weather.RAIN, turns=5)
        self.assertEqual(battle.weather, Weather.RAIN)
        self.assertEqual(battle.weather_turns, 5)

    def test_world_system(self):
        """Test world map functionality."""
        world = World()

        self.assertIsNotNone(world.current_location)
        self.assertTrue(len(world.locations) > 0)

    def test_npc_registry(self):
        """Test NPC system."""
        npc_registry = NPCRegistry()

        # Check that gym leaders exist
        gym_leaders = npc_registry.get_gym_leaders()
        self.assertEqual(len(gym_leaders), 8)

        # Check that each gym leader has a team
        for leader in gym_leaders:
            self.assertIsNotNone(leader.name)
            self.assertIsNotNone(leader.team)

    def test_type_effectiveness(self):
        """Test type effectiveness calculations."""
        from genemon.creatures.types import get_effectiveness

        # Test super effective
        effectiveness = get_effectiveness("Aqua", ["Flame"])
        self.assertEqual(effectiveness, 2.0)

        # Test not very effective
        effectiveness = get_effectiveness("Flame", ["Aqua"])
        self.assertEqual(effectiveness, 0.5)

        # Test neutral
        effectiveness = get_effectiveness("Neutral", ["Neutral"])
        self.assertEqual(effectiveness, 1.0)

    def test_evolution_system(self):
        """Test evolution mechanics."""
        # Create a creature that can evolve
        evolving_species = CreatureSpecies(
            id=1,
            name="Testmon",
            types=["Flame"],
            base_stats=CreatureStats(hp=45, attack=49, defense=49, special=65, speed=45),
            moves=[self.test_move],  # Species must have at least one move
            flavor_text="A test creature",
            evolution_level=16,  # Evolves at level 16
            evolves_into=2,
            ability=Ability(name="Blaze", description="Powers up Flame moves", effect_type="type_boost")
        )

        creature = Creature(evolving_species, level=15)
        self.assertFalse(creature.can_evolve())

        creature.level = 16
        self.assertTrue(creature.can_evolve())

    def test_team_management(self):
        """Test team operations."""
        team = Team()

        # Add creatures
        for i in range(3):
            creature = Creature(self.test_species, level=5)
            team.add_creature(creature)

        self.assertEqual(len(team.creatures), 3)
        self.assertTrue(team.has_active_creatures())

        # Test team capacity
        self.assertTrue(team.has_space())

    def test_critical_hits(self):
        """Test critical hit system."""
        player_creature = Creature(self.test_species, level=10)
        player_creature.moves = [self.test_move]
        player_team = Team()
        player_team.add_creature(player_creature)

        opponent_creature = Creature(self.test_species, level=10)
        opponent_creature.moves = [self.test_move]
        opponent_team = Team()
        opponent_team.add_creature(opponent_creature)

        battle = Battle(player_team, opponent_team, is_wild=True)

        # Test critical hit check (returns bool)
        is_crit = battle._check_critical_hit(
            player_creature,
            opponent_creature,
            self.test_move,
            True
        )

        self.assertIsInstance(is_crit, bool)


def run_tests():
    """Run all tests and print results."""
    print("=" * 70)
    print(" Iteration 22 - Game Functionality Test Suite")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIteration22)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print(f" Test Results: {result.testsRun} tests")
    print(f" ✓ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures:
        print(f" ✗ Failed: {len(result.failures)}")
    if result.errors:
        print(f" ✗ Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
