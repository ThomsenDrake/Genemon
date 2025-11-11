#!/usr/bin/env python3
"""
Quick test script to verify core Genemon functionality.
"""

import sys
import os

# Add the loop directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from genemon.core.creature import Creature, CreatureSpecies, Move, CreatureStats, Team
        print("  ✓ creature module")

        from genemon.creatures.generator import CreatureGenerator
        print("  ✓ creature generator")

        from genemon.creatures.types import TYPES, get_effectiveness
        print("  ✓ type system")

        from genemon.sprites.generator import SpriteGenerator
        print("  ✓ sprite generator")

        from genemon.battle.engine import Battle, BattleAction, BattleResult
        print("  ✓ battle engine")

        from genemon.world.map import World, Location
        print("  ✓ world map")

        from genemon.world.npc import NPC, NPCRegistry
        print("  ✓ NPC system")

        from genemon.core.save_system import GameState, SaveManager
        print("  ✓ save system")

        from genemon.ui.display import Display
        print("  ✓ UI display")

        from genemon.core.game import Game
        print("  ✓ game engine")

        print("✓ All imports successful!\n")
        return True

    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_creature_generation():
    """Test creature generation."""
    print("Testing creature generation...")

    try:
        from genemon.creatures.generator import CreatureGenerator

        gen = CreatureGenerator(seed=12345)
        creatures = gen.generate_all_creatures()

        assert len(creatures) == 151, f"Expected 151 creatures, got {len(creatures)}"
        print(f"  ✓ Generated {len(creatures)} creatures")

        # Check first few creatures
        for i in range(3):
            c = creatures[i]
            assert c.id == i + 1, f"Creature {i} has wrong ID"
            assert c.name, f"Creature {i} has no name"
            assert c.types, f"Creature {i} has no types"
            assert c.base_stats, f"Creature {i} has no stats"
            assert c.moves, f"Creature {i} has no moves"
            print(f"  ✓ Creature #{c.id}: {c.name} ({'/'.join(c.types)})")

        print("✓ Creature generation successful!\n")
        return True

    except Exception as e:
        print(f"✗ Creature generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sprite_generation():
    """Test sprite generation."""
    print("Testing sprite generation...")

    try:
        from genemon.sprites.generator import SpriteGenerator

        sprite_gen = SpriteGenerator(seed=12345)
        sprites = sprite_gen.generate_creature_sprites(
            creature_id=1,
            types=["Flame"],
            archetype="quadruped"
        )

        assert 'front' in sprites, "Missing front sprite"
        assert 'back' in sprites, "Missing back sprite"
        assert 'mini' in sprites, "Missing mini sprite"

        # Check dimensions
        front = sprites['front']
        assert len(front) == 56, f"Front sprite wrong height: {len(front)}"
        assert len(front[0]) == 56, f"Front sprite wrong width: {len(front[0])}"

        mini = sprites['mini']
        assert len(mini) == 16, f"Mini sprite wrong height: {len(mini)}"
        assert len(mini[0]) == 16, f"Mini sprite wrong width: {len(mini[0])}"

        print(f"  ✓ Front sprite: {len(front)}x{len(front[0])}")
        print(f"  ✓ Back sprite: {len(sprites['back'])}x{len(sprites['back'][0])}")
        print(f"  ✓ Mini sprite: {len(mini)}x{len(mini[0])}")

        print("✓ Sprite generation successful!\n")
        return True

    except Exception as e:
        print(f"✗ Sprite generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_type_system():
    """Test type effectiveness."""
    print("Testing type system...")

    try:
        from genemon.creatures.types import get_effectiveness, TYPES

        # Test super effective
        eff = get_effectiveness("Flame", ["Leaf"])
        assert eff == 2.0, f"Flame vs Leaf should be 2.0, got {eff}"
        print(f"  ✓ Flame vs Leaf: {eff}x (super effective)")

        # Test not very effective
        eff = get_effectiveness("Flame", ["Aqua"])
        assert eff == 0.5, f"Flame vs Aqua should be 0.5, got {eff}"
        print(f"  ✓ Flame vs Aqua: {eff}x (not very effective)")

        # Test neutral
        eff = get_effectiveness("Flame", ["Beast"])
        assert eff == 1.0, f"Flame vs Beast should be 1.0, got {eff}"
        print(f"  ✓ Flame vs Beast: {eff}x (neutral)")

        print(f"  ✓ Total types: {len(TYPES)}")

        print("✓ Type system successful!\n")
        return True

    except Exception as e:
        print(f"✗ Type system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_battle_system():
    """Test battle mechanics."""
    print("Testing battle system...")

    try:
        from genemon.core.creature import Creature, CreatureSpecies, Move, CreatureStats, Team
        from genemon.battle.engine import Battle, BattleAction

        # Create test creatures
        move = Move("Test Attack", "Beast", 40, 100, 20, 20, "A test move")

        species1 = CreatureSpecies(
            id=1,
            name="Testmon",
            types=["Beast"],
            base_stats=CreatureStats(50, 50, 50, 50, 50),
            moves=[move],
            flavor_text="A test creature"
        )

        species2 = CreatureSpecies(
            id=2,
            name="Opponent",
            types=["Beast"],
            base_stats=CreatureStats(40, 40, 40, 40, 40),
            moves=[move],
            flavor_text="An opponent"
        )

        creature1 = Creature(species=species1, level=10, current_hp=0)
        creature2 = Creature(species=species2, level=10, current_hp=0)

        team1 = Team()
        team1.add_creature(creature1)

        team2 = Team()
        team2.add_creature(creature2)

        battle = Battle(team1, team2, is_wild=True)

        print(f"  ✓ Battle created")
        print(f"  ✓ Player: {battle.player_active.species.name} (HP: {battle.player_active.current_hp})")
        print(f"  ✓ Opponent: {battle.opponent_active.species.name} (HP: {battle.opponent_active.current_hp})")

        # Execute one attack
        result = battle.execute_turn(BattleAction.ATTACK, 0)
        print(f"  ✓ Turn executed, result: {result.value}")

        print("✓ Battle system successful!\n")
        return True

    except Exception as e:
        print(f"✗ Battle system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_world_system():
    """Test world and map."""
    print("Testing world system...")

    try:
        from genemon.world.map import World
        from genemon.world.npc import NPCRegistry

        world = World()
        assert len(world.locations) > 0, "World has no locations"
        print(f"  ✓ World created with {len(world.locations)} locations")

        starter = world.get_starting_location()
        assert starter is not None, "No starting location"
        print(f"  ✓ Starting location: {starter.name}")

        npc_registry = NPCRegistry()
        assert len(npc_registry.npcs) > 0, "No NPCs"
        print(f"  ✓ NPCs created: {len(npc_registry.npcs)}")

        print("✓ World system successful!\n")
        return True

    except Exception as e:
        print(f"✗ World system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("GENEMON TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        test_imports,
        test_creature_generation,
        test_sprite_generation,
        test_type_system,
        test_battle_system,
        test_world_system
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
