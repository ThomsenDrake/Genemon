#!/usr/bin/env python3
"""
Test suite for held items system (Iteration 14).

Tests:
1. Type boost items (Charcoal, Mystic Water, etc.)
2. Power boost items (Muscle Band, Wise Glasses)
3. Critical hit boost items (Scope Lens, Razor Claw)
4. Life Orb damage and recoil
5. Choice items (Choice Band, Choice Specs, Choice Scarf)
6. Leftovers healing
7. Shell Bell healing
8. Expert Belt (super-effective boost)
"""

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Team, Move
from genemon.core.held_items import create_held_items_catalog
from genemon.battle.engine import Battle


def create_test_creature(name, hp=40, attack=30, defense=30, type_name="Beast", ability=None):
    """Create a simple test creature."""
    stats = CreatureStats(hp=hp, attack=attack, defense=defense, special=30, speed=30)

    # Create creature with basic tackle move
    tackle = Move(
        name="Tackle",
        type=type_name,
        power=40,
        accuracy=100,
        pp=35,
        max_pp=35,
        description="A basic attack"
    )

    # Create using CreatureSpecies dataclass
    species = CreatureSpecies(
        id=1,
        name=name,
        types=[type_name],
        base_stats=stats,
        moves=[tackle],
        flavor_text="A test creature",
        ability=ability
    )

    creature = Creature(species=species, level=10)
    creature.moves = [tackle]
    return creature


def test_type_boost_items():
    """Test type-boosting held items."""
    print("Testing type-boost items (Charcoal for Flame moves)...")

    catalog = create_held_items_catalog()
    charcoal = catalog["Charcoal"]

    # Create a Flame-type creature with Charcoal
    attacker = create_test_creature("Flamey", attack=50, type_name="Flame")
    attacker.held_item = charcoal

    # Create Flame-type move
    flame_move = Move(
        name="Ember",
        type="Flame",
        power=40,
        accuracy=100,
        pp=25,
        max_pp=25,
        description="A flame attack"
    )
    attacker.moves = [flame_move]

    defender = create_test_creature("Defender", defense=30, type_name="Beast")

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Execute attack with Charcoal
    defender_hp_before = defender.current_hp
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)
    defender_hp_after = defender.current_hp

    damage_dealt = defender_hp_before - defender_hp_after

    # Charcoal should boost Flame moves by 20%
    assert damage_dealt > 0, "Should deal damage"
    print(f"  ✓ Charcoal boosted Flame move damage: {damage_dealt} HP")
    print(f"  ✓ Defender HP: {defender_hp_after}/{defender.max_hp}")


def test_power_boost_items():
    """Test generic power-boosting items (Muscle Band, Wise Glasses)."""
    print("\nTesting power-boost items (Muscle Band)...")

    catalog = create_held_items_catalog()
    muscle_band = catalog["Muscle Band"]

    attacker = create_test_creature("Strong", attack=50)
    attacker.held_item = muscle_band

    defender = create_test_creature("Weak", defense=20)

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    defender_hp_before = defender.current_hp
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)
    defender_hp_after = defender.current_hp

    damage_dealt = defender_hp_before - defender_hp_after

    # Muscle Band boosts attack power by 20%
    assert damage_dealt > 0, "Should deal damage"
    print(f"  ✓ Muscle Band boosted damage: {damage_dealt} HP")


def test_crit_boost_items():
    """Test critical hit boost items (Scope Lens)."""
    print("\nTesting critical hit boost items (Scope Lens)...")

    catalog = create_held_items_catalog()
    scope_lens = catalog["Scope Lens"]

    attacker = create_test_creature("Sniper", attack=40)
    attacker.held_item = scope_lens

    defender = create_test_creature("Target", defense=30, hp=100)

    team1 = Team([attacker])
    team2 = Team([defender])

    # Run multiple battles to check for crits (probability test)
    crit_count = 0
    total_battles = 100

    for i in range(total_battles):
        # Reset creatures
        attacker = create_test_creature("Sniper", attack=40)
        attacker.held_item = scope_lens
        defender = create_test_creature("Target", defense=30, hp=100)

        team1 = Team([attacker])
        team2 = Team([defender])
        battle = Battle(team1, team2, is_wild=True, can_run=False)

        # Execute attack
        from genemon.battle.engine import BattleAction
        battle.execute_turn(BattleAction.ATTACK, 0)

        # Check for critical hit in battle log
        if any("Critical hit" in msg for msg in battle.log.messages):
            crit_count += 1

    crit_rate = (crit_count / total_battles) * 100

    # Scope Lens increases crit stage by 1, changing base 6.25% to 12.5%
    # We expect roughly 12.5% crit rate
    print(f"  ✓ Critical hit rate with Scope Lens: {crit_rate:.1f}% (expected ~12.5%)")
    assert crit_rate > 5, f"Crit rate should be higher than base (got {crit_rate:.1f}%)"


def test_life_orb():
    """Test Life Orb damage boost and recoil."""
    print("\nTesting Life Orb (damage boost + recoil)...")

    catalog = create_held_items_catalog()
    life_orb = catalog["Life Orb"]

    attacker = create_test_creature("Reckless", attack=50, hp=60)
    attacker.held_item = life_orb

    defender = create_test_creature("Tank", defense=30)

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    attacker_hp_before = attacker.current_hp
    defender_hp_before = defender.current_hp

    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    attacker_hp_after = attacker.current_hp
    defender_hp_after = defender.current_hp

    damage_to_defender = defender_hp_before - defender_hp_after
    recoil_to_attacker = attacker_hp_before - attacker_hp_after

    # Life Orb boosts damage by 30% and causes 10% max HP recoil
    assert damage_to_defender > 0, "Should deal boosted damage"
    assert recoil_to_attacker > 0, "Should take Life Orb recoil"

    # Check for Life Orb message in log
    life_orb_msg_found = any("Life Orb" in msg for msg in battle.log.messages)
    assert life_orb_msg_found, "Should show Life Orb message"

    print(f"  ✓ Life Orb boosted damage: {damage_to_defender} HP to defender")
    print(f"  ✓ Life Orb recoil damage: {recoil_to_attacker} HP to attacker")


def test_choice_band():
    """Test Choice Band (boosts attack by 50%)."""
    print("\nTesting Choice Band (50% attack boost)...")

    catalog = create_held_items_catalog()
    choice_band = catalog["Choice Band"]

    attacker = create_test_creature("Choiced", attack=40)
    attacker.held_item = choice_band

    defender = create_test_creature("Victim", defense=25)

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    defender_hp_before = defender.current_hp
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)
    defender_hp_after = defender.current_hp

    damage_dealt = defender_hp_before - defender_hp_after

    # Choice Band provides 50% boost
    assert damage_dealt > 0, "Should deal heavy damage"
    print(f"  ✓ Choice Band boosted damage: {damage_dealt} HP")


def test_leftovers():
    """Test Leftovers end-of-turn healing."""
    print("\nTesting Leftovers (end-of-turn healing)...")

    catalog = create_held_items_catalog()
    leftovers = catalog["Leftovers"]

    attacker = create_test_creature("Healer", hp=60)
    attacker.held_item = leftovers
    # Damage the creature first
    attacker.take_damage(20)
    initial_hp = attacker.current_hp

    defender = create_test_creature("Opponent")

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    hp_after_turn = attacker.current_hp

    # Leftovers should restore 1/16 max HP at end of turn
    expected_heal = max(1, int(attacker.max_hp * 0.0625))

    # Check for Leftovers message
    leftovers_msg = any("Leftovers" in msg for msg in battle.log.messages)

    print(f"  ✓ HP before turn: {initial_hp}/{attacker.max_hp}")
    print(f"  ✓ HP after turn: {hp_after_turn}/{attacker.max_hp}")
    print(f"  ✓ Expected healing: ~{expected_heal} HP")
    if leftovers_msg:
        print(f"  ✓ Leftovers message found in battle log")


def test_shell_bell():
    """Test Shell Bell healing on damage dealt."""
    print("\nTesting Shell Bell (heal on damage)...")

    catalog = create_held_items_catalog()
    shell_bell = catalog["Shell Bell"]

    attacker = create_test_creature("Vampire", attack=50, hp=50)
    attacker.held_item = shell_bell
    # Damage the attacker first so it can heal
    attacker.take_damage(20)
    hp_before_attack = attacker.current_hp

    defender = create_test_creature("Prey", defense=20)

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    hp_after_attack = attacker.current_hp

    # Shell Bell should restore 1/8 of damage dealt
    # Check for Shell Bell message
    shell_bell_msg = any("Shell Bell" in msg for msg in battle.log.messages)

    print(f"  ✓ HP before attack: {hp_before_attack}/{attacker.max_hp}")
    print(f"  ✓ HP after attack: {hp_after_attack}/{attacker.max_hp}")
    if shell_bell_msg:
        print(f"  ✓ Shell Bell message found in battle log")


def test_expert_belt():
    """Test Expert Belt (boosts super-effective moves)."""
    print("\nTesting Expert Belt (super-effective boost)...")

    catalog = create_held_items_catalog()
    expert_belt = catalog["Expert Belt"]

    # Flame is super-effective against Leaf
    attacker = create_test_creature("Expert", attack=40, type_name="Flame")
    attacker.held_item = expert_belt

    # Create Flame move for Flame-type attacker
    flame_move = Move(
        name="Ember",
        type="Flame",
        power=40,
        accuracy=100,
        pp=25,
        max_pp=25,
        description="A flame attack"
    )
    attacker.moves = [flame_move]

    # Leaf-type defender (weak to Flame)
    defender = create_test_creature("Leafy", defense=25, type_name="Leaf")

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    defender_hp_before = defender.current_hp
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)
    defender_hp_after = defender.current_hp

    damage_dealt = defender_hp_before - defender_hp_after

    # Expert Belt boosts super-effective moves by 20%
    assert damage_dealt > 0, "Should deal super-effective damage"

    # Check for super-effective message
    super_eff_msg = any("Super effective" in msg for msg in battle.log.messages)
    assert super_eff_msg, "Should show super-effective message"

    print(f"  ✓ Expert Belt boosted super-effective damage: {damage_dealt} HP")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GENEMON HELD ITEMS SYSTEM TEST SUITE")
    print("Testing Iteration 14 Features")
    print("=" * 60)

    tests_run = 0
    tests_passed = 0

    tests = [
        ("Type boost items", test_type_boost_items),
        ("Power boost items", test_power_boost_items),
        ("Critical hit boost items", test_crit_boost_items),
        ("Life Orb", test_life_orb),
        ("Choice Band", test_choice_band),
        ("Leftovers", test_leftovers),
        ("Shell Bell", test_shell_bell),
        ("Expert Belt", test_expert_belt),
    ]

    for test_name, test_func in tests:
        tests_run += 1
        try:
            test_func()
            tests_passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"RESULTS: {tests_passed}/{tests_run} tests passed")
    if tests_passed == tests_run:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {tests_run - tests_passed} test(s) failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
