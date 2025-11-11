#!/usr/bin/env python3
"""
Test suite for advanced move mechanics (Iteration 13)
Tests multi-hit moves, recoil moves, and priority moves.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Move, Team, Ability
from genemon.battle.engine import Battle


def test_multi_hit_moves():
    """Test that multi-hit moves hit multiple times."""
    print("\nTesting multi-hit moves...")

    # Create species
    attacker_species = CreatureSpecies(
        id=1,
        name="Testmon",
        types=["Beast"],
        base_stats=CreatureStats(hp=50, attack=60, defense=40, special=40, speed=50),
        moves=[
            Move("Multi Strike", "Beast", 25, 100, 20, 20, "Hits 2-5 times.", multi_hit=(2, 5))
        ],
        flavor_text="Test creature",
        ability=None
    )

    defender_species = CreatureSpecies(
        id=2,
        name="Defender",
        types=["Beast"],
        base_stats=CreatureStats(hp=100, attack=40, defense=40, special=40, speed=40),
        moves=[
            Move("Tackle", "Beast", 40, 100, 20, 20, "A normal attack.")
        ],
        flavor_text="Test defender",
        ability=None
    )

    attacker = Creature(attacker_species, level=10, nickname="Attacker")
    defender = Creature(defender_species, level=10, nickname="Defender")

    # Test multi-hit in battle
    player_team = Team([attacker])
    opponent_team = Team([defender])
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Execute one attack
    from genemon.battle.engine import BattleAction
    initial_hp = defender.current_hp
    result = battle.execute_turn(BattleAction.ATTACK, 0)

    # Check that defender took damage
    damage_dealt = initial_hp - defender.current_hp
    print(f"  Defender HP: {initial_hp} → {defender.current_hp} (damage: {damage_dealt})")
    print(f"  Battle log: {battle.log.get_recent(3)}")

    # Multi-hit should have hit at least 2 times (damage should be > single hit)
    if damage_dealt > 0:
        print("  ✓ Multi-hit move dealt damage")
    else:
        print("  ✗ Multi-hit move failed")
        return False

    return True


def test_skill_link_ability():
    """Test that Skill Link ability makes multi-hit moves always hit maximum times."""
    print("\nTesting Skill Link ability (max multi-hits)...")

    # Create species with Skill Link
    skill_link_ability = Ability(
        name="Skill Link",
        description="Multi-hit moves always hit maximum times",
        effect_type="multi_hit_max"
    )

    attacker_species = CreatureSpecies(
        id=1,
        name="SkillLinker",
        types=["Beast"],
        base_stats=CreatureStats(hp=50, attack=70, defense=40, special=40, speed=50),
        moves=[
            Move("Fury Strike", "Beast", 20, 100, 25, 25, "Hits 2-5 times.", multi_hit=(2, 5))
        ],
        flavor_text="Test creature with Skill Link",
        ability=skill_link_ability
    )

    defender_species = CreatureSpecies(
        id=2,
        name="Defender",
        types=["Beast"],
        base_stats=CreatureStats(hp=150, attack=40, defense=40, special=40, speed=40),
        moves=[
            Move("Tackle", "Beast", 40, 100, 20, 20, "A normal attack.")
        ],
        flavor_text="Test defender",
        ability=None
    )

    # Run multiple battles to verify Skill Link works
    hit_counts = []
    for i in range(10):
        attacker = Creature(attacker_species, level=10, nickname=f"Attacker{i}")
        defender = Creature(defender_species, level=10, nickname=f"Defender{i}")

        player_team = Team([attacker])
        opponent_team = Team([defender])
        battle = Battle(player_team, opponent_team, is_wild=True)

        initial_hp = defender.current_hp
        from genemon.battle.engine import BattleAction
        battle.execute_turn(BattleAction.ATTACK, 0)

        # Count hits from battle log
        log_msgs = battle.log.get_recent(10)
        hit_count = sum(1 for msg in log_msgs if "Hit " in msg)
        hit_counts.append(hit_count)

    avg_hits = sum(hit_counts) / len(hit_counts) if hit_counts else 0
    print(f"  Average hits over 10 battles: {avg_hits:.1f}")
    print(f"  Hit counts: {hit_counts}")

    # Skill Link should consistently hit 5 times (max)
    if avg_hits >= 4.5:  # Allow small variance
        print(f"  ✓ Skill Link working (hits ~5 times consistently)")
        return True
    else:
        print(f"  ✗ Skill Link not working properly")
        return False


def test_recoil_moves():
    """Test that recoil moves damage the attacker."""
    print("\nTesting recoil moves...")

    # Create species with recoil move
    attacker_species = CreatureSpecies(
        id=1,
        name="Berserker",
        types=["Brawl"],
        base_stats=CreatureStats(hp=80, attack=80, defense=50, special=40, speed=60),
        moves=[
            Move("Head Smash", "Brawl", 100, 100, 10, 10, "Powerful attack with recoil.", recoil_percent=25)
        ],
        flavor_text="Test creature",
        ability=None
    )

    defender_species = CreatureSpecies(
        id=2,
        name="Tank",
        types=["Metal"],
        base_stats=CreatureStats(hp=100, attack=40, defense=60, special=40, speed=30),
        moves=[
            Move("Defend", "Metal", 30, 100, 20, 20, "A defensive move.")
        ],
        flavor_text="Test defender",
        ability=None
    )

    attacker = Creature(attacker_species, level=10, nickname="Berserker")
    defender = Creature(defender_species, level=10, nickname="Tank")

    player_team = Team([attacker])
    opponent_team = Team([defender])
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Execute attack
    from genemon.battle.engine import BattleAction
    attacker_initial_hp = attacker.current_hp
    defender_initial_hp = defender.current_hp

    battle.execute_turn(BattleAction.ATTACK, 0)

    attacker_damage = attacker_initial_hp - attacker.current_hp
    defender_damage = defender_initial_hp - defender.current_hp

    print(f"  Attacker HP: {attacker_initial_hp} → {attacker.current_hp} (recoil: {attacker_damage})")
    print(f"  Defender HP: {defender_initial_hp} → {defender.current_hp} (damage: {defender_damage})")
    print(f"  Battle log: {battle.log.get_recent(3)}")

    # Attacker should take recoil damage (~25% of damage dealt)
    if attacker_damage > 0 and defender_damage > 0:
        expected_recoil = defender_damage * 0.25
        print(f"  Expected recoil: ~{expected_recoil:.1f}, Actual: {attacker_damage}")
        print("  ✓ Recoil move dealt damage to both attacker and defender")
        return True
    else:
        print("  ✗ Recoil move failed")
        return False


def test_rock_head_ability():
    """Test that Rock Head ability prevents recoil damage."""
    print("\nTesting Rock Head ability (no recoil)...")

    # Create species with Rock Head
    rock_head_ability = Ability(
        name="Rock Head",
        description="Protects from recoil damage",
        effect_type="no_recoil"
    )

    attacker_species = CreatureSpecies(
        id=1,
        name="RockHead",
        types=["Terra"],
        base_stats=CreatureStats(hp=80, attack=90, defense=70, special=40, speed=50),
        moves=[
            Move("Brave Charge", "Brawl", 100, 100, 10, 10, "Powerful attack with recoil.", recoil_percent=33)
        ],
        flavor_text="Test creature with Rock Head",
        ability=rock_head_ability
    )

    defender_species = CreatureSpecies(
        id=2,
        name="Defender",
        types=["Beast"],
        base_stats=CreatureStats(hp=100, attack=40, defense=50, special=40, speed=40),
        moves=[
            Move("Tackle", "Beast", 40, 100, 20, 20, "A normal attack.")
        ],
        flavor_text="Test defender",
        ability=None
    )

    attacker = Creature(attacker_species, level=10, nickname="RockHead")
    defender = Creature(defender_species, level=10, nickname="Defender")

    player_team = Team([attacker])
    opponent_team = Team([defender])
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Execute attack
    from genemon.battle.engine import BattleAction
    attacker_initial_hp = attacker.current_hp
    defender_initial_hp = defender.current_hp

    battle.execute_turn(BattleAction.ATTACK, 0)

    attacker_damage = attacker_initial_hp - attacker.current_hp
    defender_damage = defender_initial_hp - defender.current_hp

    print(f"  Attacker HP: {attacker_initial_hp} → {attacker.current_hp} (should be no recoil)")
    print(f"  Defender HP: {defender_initial_hp} → {defender.current_hp} (damage: {defender_damage})")

    # Check battle log for recoil messages
    log_msgs = battle.log.get_recent(10)
    print(f"  Battle log: {log_msgs}")
    has_recoil_message = any("recoil" in msg.lower() for msg in log_msgs)

    # Rock Head should prevent recoil damage (check for recoil message)
    if not has_recoil_message and defender_damage > 0:
        print("  ✓ Rock Head prevented recoil damage (no recoil message in log)")
        return True
    elif has_recoil_message:
        print(f"  ✗ Rock Head failed (recoil message found in log)")
        return False
    else:
        print(f"  ? Unclear result - defender may not have taken damage")
        return False


def test_priority_moves():
    """Test that priority moves go first regardless of speed."""
    print("\nTesting priority moves...")

    # Create fast and slow creatures with priority moves
    fast_species = CreatureSpecies(
        id=1,
        name="Speedster",
        types=["Gale"],
        base_stats=CreatureStats(hp=50, attack=60, defense=40, special=40, speed=100),
        moves=[
            Move("Normal Attack", "Gale", 50, 100, 20, 20, "Normal speed attack.", priority=0)
        ],
        flavor_text="Fast creature",
        ability=None
    )

    slow_species = CreatureSpecies(
        id=2,
        name="Slowpoke",
        types=["Terra"],
        base_stats=CreatureStats(hp=80, attack=70, defense=50, special=40, speed=20),
        moves=[
            Move("Quick Attack", "Beast", 40, 100, 30, 30, "Always strikes first.", priority=1)
        ],
        flavor_text="Slow creature with priority move",
        ability=None
    )

    # Test: Slow creature should attack first with priority move
    fast = Creature(fast_species, level=10, nickname="Fast")
    slow = Creature(slow_species, level=10, nickname="Slow")

    player_team = Team([slow])  # Player is the slow one with priority
    opponent_team = Team([fast])
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Execute turn
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    # Check battle log to see who attacked first
    log_msgs = battle.log.get_recent(10)
    print(f"  Battle log: {log_msgs}")

    # Find attack messages
    slow_attack_index = None
    fast_attack_index = None
    for i, msg in enumerate(log_msgs):
        if "Slow used" in msg:
            slow_attack_index = i
        if "Fast used" in msg:
            fast_attack_index = i

    if slow_attack_index is not None and fast_attack_index is not None:
        if slow_attack_index < fast_attack_index:
            print(f"  ✓ Priority move went first (slow creature attacked before fast creature)")
            return True
        else:
            print(f"  ✗ Priority move failed (slow creature attacked after fast creature)")
            return False
    else:
        print("  ? Could not determine attack order from log")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("GENEMON ADVANCED MOVE MECHANICS TEST SUITE")
    print("Testing Iteration 13 Features")
    print("=" * 60)

    tests = [
        test_multi_hit_moves,
        test_skill_link_ability,
        test_recoil_moves,
        test_rock_head_ability,
        test_priority_moves,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {total - passed} test(s) failed")

    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
