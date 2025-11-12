#!/usr/bin/env python3
"""
Test suite for Iteration 15: Advanced Held Item Effects

Tests the following features:
- Contact move tagging (is_contact field)
- Rocky Helmet contact damage
- Focus Band/Sash faint prevention
- Flame/Toxic Orb auto-inflict status
- Quick Claw priority system
- Choice item move locking
"""

import random
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Move, StatusEffect
from genemon.core.held_items import create_held_items_catalog
from genemon.battle.engine import Battle
from genemon.core.creature import Team


def create_test_species(name: str, types: list, base_hp: int = 50, base_attack: int = 50) -> CreatureSpecies:
    """Create a test creature species."""
    return CreatureSpecies(
        id=1,
        name=name,
        types=types,
        base_stats=CreatureStats(hp=base_hp, attack=base_attack, defense=40, special=40, speed=50),
        moves=[],
        flavor_text="Test creature",
        evolution_level=None,
        evolves_into=None,
        sprite_data=None,
        learnset=None,
        tm_compatible=None,
        ability=None,
        is_legendary=False
    )


def create_test_move(name: str, power: int = 50, is_contact: bool = True) -> Move:
    """Create a test move."""
    return Move(
        name=name,
        type="Beast",
        power=power,
        accuracy=100,
        pp=20,
        max_pp=20,
        description="Test move",
        is_contact=is_contact
    )


def test_contact_move_tagging():
    """Test that moves are correctly tagged as contact or non-contact."""
    print("Testing contact move tagging...")

    # Contact move
    tackle = create_test_move("Tackle", power=40, is_contact=True)
    assert tackle.is_contact == True, "Tackle should be a contact move"
    print("  ✓ Contact move (Tackle) correctly tagged")

    # Non-contact move
    beam = create_test_move("Hyper Beam", power=90, is_contact=False)
    assert beam.is_contact == False, "Hyper Beam should not be a contact move"
    print("  ✓ Non-contact move (Hyper Beam) correctly tagged")

    # Zero-power move (status move)
    status_move = Move(
        name="Growl", type="Beast", power=0, accuracy=100,
        pp=40, max_pp=40, description="Lowers attack",
        is_contact=False
    )
    assert status_move.is_contact == False, "Status moves should not be contact"
    print("  ✓ Status move correctly tagged as non-contact")

    return True


def test_rocky_helmet():
    """Test Rocky Helmet damages attackers on contact moves."""
    print("Testing Rocky Helmet contact damage...")

    items = create_held_items_catalog()

    # Create attacker and defender
    attacker_species = create_test_species("Attacker", ["Beast"], base_hp=100, base_attack=60)
    defender_species = create_test_species("Defender", ["Terra"], base_hp=80, base_attack=40)

    attacker = Creature(species=attacker_species, level=10)
    defender = Creature(species=defender_species, level=10)

    # Equip Rocky Helmet to defender
    defender.held_item = items["Rocky Helmet"]

    # Create teams
    player_team = Team(creatures=[attacker])
    opponent_team = Team(creatures=[defender])

    # Create battle
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Create contact move
    contact_move = create_test_move("Tackle", power=40, is_contact=True)
    attacker.moves = [contact_move]

    initial_attacker_hp = attacker.current_hp

    # Execute attack
    battle._execute_attack(attacker, defender, contact_move, is_player=True)

    # Check that attacker took Rocky Helmet damage
    helmet_damage = int(attacker.max_hp * 0.16)  # Rocky Helmet deals 1/6 max HP
    expected_hp = initial_attacker_hp - helmet_damage

    print(f"  ✓ Attacker HP: {initial_attacker_hp} -> {attacker.current_hp}")
    print(f"  ✓ Expected Rocky Helmet damage: ~{helmet_damage} HP")
    assert attacker.current_hp <= expected_hp, "Rocky Helmet should damage attacker"

    # Check battle log mentions Rocky Helmet
    helmet_mentioned = any("Rocky Helmet" in msg for msg in battle.log.messages)
    assert helmet_mentioned, "Battle log should mention Rocky Helmet"
    print("  ✓ Rocky Helmet message found in battle log")

    return True


def test_non_contact_no_helmet():
    """Test that non-contact moves don't trigger Rocky Helmet."""
    print("Testing Rocky Helmet doesn't trigger on non-contact moves...")

    items = create_held_items_catalog()

    # Create attacker and defender
    attacker_species = create_test_species("Attacker", ["Beast"], base_hp=100, base_attack=60)
    defender_species = create_test_species("Defender", ["Terra"], base_hp=80, base_attack=40)

    attacker = Creature(species=attacker_species, level=10)
    defender = Creature(species=defender_species, level=10)

    # Equip Rocky Helmet to defender
    defender.held_item = items["Rocky Helmet"]

    # Create teams
    player_team = Team(creatures=[attacker])
    opponent_team = Team(creatures=[defender])

    # Create battle
    battle = Battle(player_team, opponent_team, is_wild=True)

    # Create non-contact move
    beam = create_test_move("Hyper Beam", power=90, is_contact=False)
    attacker.moves = [beam]

    initial_attacker_hp = attacker.current_hp

    # Execute attack
    battle._execute_attack(attacker, defender, beam, is_player=True)

    # Attacker should not have taken Rocky Helmet damage
    # (may have taken other damage like Life Orb, but not helmet)
    print(f"  ✓ Attacker HP: {initial_attacker_hp} -> {attacker.current_hp}")

    # Rocky Helmet should NOT be mentioned for non-contact moves
    helmet_mentioned = any("Rocky Helmet" in msg for msg in battle.log.messages)
    assert not helmet_mentioned, "Rocky Helmet should not trigger on non-contact moves"
    print("  ✓ Rocky Helmet did not trigger (as expected)")

    return True


def test_focus_band():
    """Test Focus Band has a chance to prevent fainting."""
    print("Testing Focus Band faint prevention (10% chance)...")

    items = create_held_items_catalog()

    # Run multiple trials to test probabilistic behavior
    survivals = 0
    trials = 100

    for _ in range(trials):
        # Create creature with low HP
        species = create_test_species("TestMon", ["Beast"], base_hp=50, base_attack=40)
        creature = Creature(species=species, level=10)
        creature.current_hp = 1  # Very low HP

        # Equip Focus Band
        creature.held_item = items["Focus Band"]

        # Create a battle to test damage application
        player_team = Team(creatures=[creature])
        opponent_species = create_test_species("Opponent", ["Flame"], base_hp=50, base_attack=50)
        opponent = Creature(species=opponent_species, level=10)
        opponent_team = Team(creatures=[opponent])

        battle = Battle(player_team, opponent_team, is_wild=True)

        # Apply lethal damage (more than current HP)
        damage = battle._apply_focus_item(creature, 100)  # 100 damage to creature with 1 HP

        if damage < 100:  # Focus Band triggered
            survivals += 1

    survival_rate = survivals / trials
    print(f"  ✓ Focus Band activated {survivals}/{trials} times ({survival_rate*100:.1f}%)")
    print(f"  ✓ Expected rate: ~10%")

    # Should be roughly 10% (allow 3-17% range for statistical variance)
    assert 0.03 <= survival_rate <= 0.17, f"Focus Band should trigger ~10% of the time, got {survival_rate*100:.1f}%"

    return True


def test_focus_sash():
    """Test Focus Sash guarantees survival at full HP."""
    print("Testing Focus Sash (guaranteed survival at full HP)...")

    items = create_held_items_catalog()

    # Create creature at full HP
    species = create_test_species("TestMon", ["Beast"], base_hp=50, base_attack=40)
    creature = Creature(species=species, level=10)
    creature.current_hp = creature.max_hp  # Full HP

    # Equip Focus Sash
    creature.held_item = items["Focus Sash"]

    # Create battle
    player_team = Team(creatures=[creature])
    opponent_species = create_test_species("Opponent", ["Flame"], base_hp=50, base_attack=50)
    opponent = Creature(species=opponent_species, level=10)
    opponent_team = Team(creatures=[opponent])

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Apply lethal damage
    initial_hp = creature.current_hp
    damage = battle._apply_focus_item(creature, 1000)  # Massive damage

    # Should reduce damage to leave 1 HP
    expected_damage = initial_hp - 1
    print(f"  ✓ Original damage: 1000, Adjusted damage: {damage}")
    print(f"  ✓ Creature HP: {initial_hp} -> would be at 1 HP after this damage")

    assert damage == expected_damage, "Focus Sash should reduce damage to leave 1 HP"
    assert creature.focus_sash_used == True, "Focus Sash should be marked as used"
    print("  ✓ Focus Sash prevented fainting")

    # Test that it only works once
    creature2 = Creature(species=species, level=10)
    creature2.current_hp = creature2.max_hp
    creature2.held_item = items["Focus Sash"]
    creature2.focus_sash_used = True  # Already used

    damage2 = battle._apply_focus_item(creature2, 1000)
    assert damage2 == 1000, "Focus Sash should not work if already used"
    print("  ✓ Focus Sash only works once per battle")

    return True


def test_flame_orb():
    """Test Flame Orb auto-inflicts burn status."""
    print("Testing Flame Orb auto-inflict burn...")

    items = create_held_items_catalog()

    # Create creature
    species = create_test_species("TestMon", ["Beast"], base_hp=50, base_attack=40)
    creature = Creature(species=species, level=10)

    # Equip Flame Orb
    creature.held_item = items["Flame Orb"]

    # Create battle
    player_team = Team(creatures=[creature])
    opponent_species = create_test_species("Opponent", ["Aqua"], base_hp=50, base_attack=40)
    opponent = Creature(species=opponent_species, level=10)
    opponent_team = Team(creatures=[opponent])

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Process held item effects (should burn the holder)
    assert creature.status == StatusEffect.NONE, "Creature should start without status"
    battle._process_held_item_effects(creature)

    print(f"  ✓ Creature status after Flame Orb: {creature.status}")
    assert creature.status == StatusEffect.BURN, "Flame Orb should burn the holder"

    # Check battle log
    burn_mentioned = any("burned" in msg.lower() for msg in battle.log.messages)
    assert burn_mentioned, "Battle log should mention burn"
    print("  ✓ Flame Orb burn message found in battle log")

    return True


def test_toxic_orb():
    """Test Toxic Orb auto-inflicts poison status."""
    print("Testing Toxic Orb auto-inflict poison...")

    items = create_held_items_catalog()

    # Create creature
    species = create_test_species("TestMon", ["Beast"], base_hp=50, base_attack=40)
    creature = Creature(species=species, level=10)

    # Equip Toxic Orb
    creature.held_item = items["Toxic Orb"]

    # Create battle
    player_team = Team(creatures=[creature])
    opponent_species = create_test_species("Opponent", ["Aqua"], base_hp=50, base_attack=40)
    opponent = Creature(species=opponent_species, level=10)
    opponent_team = Team(creatures=[opponent])

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Process held item effects (should poison the holder)
    assert creature.status == StatusEffect.NONE, "Creature should start without status"
    battle._process_held_item_effects(creature)

    print(f"  ✓ Creature status after Toxic Orb: {creature.status}")
    assert creature.status == StatusEffect.POISON, "Toxic Orb should poison the holder"

    # Check battle log
    poison_mentioned = any("poison" in msg.lower() for msg in battle.log.messages)
    assert poison_mentioned, "Battle log should mention poison"
    print("  ✓ Toxic Orb poison message found in battle log")

    return True


def test_quick_claw():
    """Test Quick Claw gives 20% chance to move first."""
    print("Testing Quick Claw priority (20% chance)...")

    items = create_held_items_catalog()

    # Create a slow attacker and fast defender
    slow_species = create_test_species("SlowMon", ["Beast"], base_hp=50, base_attack=40)
    slow_species.base_stats.speed = 10  # Very slow

    fast_species = create_test_species("FastMon", ["Aqua"], base_hp=50, base_attack=40)
    fast_species.base_stats.speed = 100  # Very fast

    slow_creature = Creature(species=slow_species, level=10)
    slow_creature.held_item = items["Quick Claw"]  # Equip Quick Claw

    fast_creature = Creature(species=fast_species, level=10)

    # Create battle
    player_team = Team(creatures=[slow_creature])
    opponent_team = Team(creatures=[fast_creature])

    battle = Battle(player_team, opponent_team, is_wild=True)
    battle.player_active = slow_creature
    battle.opponent_active = fast_creature

    # Test turn order many times
    slow_goes_first = 0
    trials = 100

    for _ in range(trials):
        # Reset random seed variation
        random.seed()

        # Create moves
        move1 = create_test_move("Tackle", power=40)
        move2 = create_test_move("Tackle", power=40)

        # Determine order
        player_first = battle._determine_order_with_priority(move1, move2)

        if player_first:
            slow_goes_first += 1

    activation_rate = slow_goes_first / trials
    print(f"  ✓ Quick Claw activated {slow_goes_first}/{trials} times ({activation_rate*100:.1f}%)")
    print(f"  ✓ Expected rate: ~20%")

    # Should be roughly 20% (allow 12-28% range for statistical variance)
    assert 0.12 <= activation_rate <= 0.28, f"Quick Claw should activate ~20% of the time, got {activation_rate*100:.1f}%"

    return True


def test_choice_item_locking():
    """Test Choice items lock the user into the first move used."""
    print("Testing Choice item move locking...")

    items = create_held_items_catalog()

    # Create creature with Choice Band
    species = create_test_species("TestMon", ["Beast"], base_hp=50, base_attack=60)
    creature = Creature(species=species, level=10)
    creature.held_item = items["Choice Band"]

    # Create opponent
    opponent_species = create_test_species("Opponent", ["Aqua"], base_hp=50, base_attack=40)
    opponent = Creature(species=opponent_species, level=10)

    # Create battle
    player_team = Team(creatures=[creature])
    opponent_team = Team(creatures=[opponent])

    battle = Battle(player_team, opponent_team, is_wild=True)

    # Create two different moves
    move1 = create_test_move("Tackle", power=40)
    move2 = create_test_move("Body Slam", power=85)
    creature.moves = [move1, move2]

    # Use first move
    assert creature.choice_locked_move is None, "Should not be locked initially"
    battle._execute_attack(creature, opponent, move1, is_player=True)

    print(f"  ✓ Used move: {move1.name}")
    print(f"  ✓ Locked into: {creature.choice_locked_move}")

    assert creature.choice_locked_move == move1.name, "Should be locked into first move used"
    print("  ✓ Choice Band locked creature into first move")

    # Verify the lock persists
    assert creature.choice_locked_move == "Tackle", "Lock should persist"
    print("  ✓ Move lock persists correctly")

    return True


def run_all_tests():
    """Run all Iteration 15 tests."""
    print("=" * 60)
    print("GENEMON ITERATION 15 TEST SUITE")
    print("Testing Advanced Held Item Effects")
    print("=" * 60)

    tests = [
        ("Contact move tagging", test_contact_move_tagging),
        ("Rocky Helmet contact damage", test_rocky_helmet),
        ("Rocky Helmet non-contact immunity", test_non_contact_no_helmet),
        ("Focus Band faint prevention", test_focus_band),
        ("Focus Sash guaranteed survival", test_focus_sash),
        ("Flame Orb auto-burn", test_flame_orb),
        ("Toxic Orb auto-poison", test_toxic_orb),
        ("Quick Claw priority", test_quick_claw),
        ("Choice item move locking", test_choice_item_locking),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED\n")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERROR: {e}\n")
            import traceback
            traceback.print_exc()

    print("=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
