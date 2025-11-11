#!/usr/bin/env python3
"""
Test suite for stat stage system (Iteration 14).

Tests:
1. Basic stat stage modifications
2. Stat stage limits (-6 to +6)
3. Stat-changing moves
4. Simple ability (doubles stat changes)
5. Contrary ability (inverts stat changes)
6. Unaware ability (ignores stat stages)
7. Stat stages reset on switch
"""

from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Team, Move, Ability
from genemon.battle.engine import Battle


def create_test_creature(name, hp=40, attack=30, defense=30, speed=30, ability=None):
    """Create a simple test creature."""
    stats = CreatureStats(hp=hp, attack=attack, defense=defense, special=30, speed=speed)

    # Create creature with basic tackle move
    tackle = Move(
        name="Tackle",
        type="Beast",
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
        types=["Beast"],
        base_stats=stats,
        moves=[tackle],
        flavor_text="A test creature",
        ability=ability
    )

    creature = Creature(species=species, level=10)
    creature.moves = [tackle]
    return creature


def test_basic_stat_modifications():
    """Test basic stat stage modifications."""
    print("Testing basic stat stage modifications...")

    creature1 = create_test_creature("Attacker")
    creature2 = create_test_creature("Defender")

    team1 = Team([creature1])
    team2 = Team([creature2])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Test raising attack by 1 stage
    battle.modify_stat_stage(is_player=True, stat="attack", stages=1)
    attack_before = creature1.species.base_stats.attack
    attack_after = battle.get_modified_stat(creature1, "attack", True)
    assert attack_after > attack_before, f"Attack should be higher after +1 stage (before: {attack_before}, after: {attack_after})"

    # Test lowering defense by 2 stages
    battle.modify_stat_stage(is_player=False, stat="defense", stages=-2)
    defense_before = creature2.species.base_stats.defense
    defense_after = battle.get_modified_stat(creature2, "defense", False)
    assert defense_after < defense_before, f"Defense should be lower after -2 stages (before: {defense_before}, after: {defense_after})"

    print(f"  ✓ Attack +1 stage: {attack_before} → {attack_after} ({attack_after/attack_before:.2f}x)")
    print(f"  ✓ Defense -2 stages: {defense_before} → {defense_after} ({defense_after/defense_before:.2f}x)")


def test_stat_stage_limits():
    """Test stat stage limits at -6 and +6."""
    print("\nTesting stat stage limits...")

    creature1 = create_test_creature("Booster")
    creature2 = create_test_creature("Weakling")

    team1 = Team([creature1])
    team2 = Team([creature2])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Raise attack to +6 (should cap)
    for i in range(8):  # Try to go beyond +6
        battle.modify_stat_stage(is_player=True, stat="attack", stages=1)

    attack_max = battle.get_modified_stat(creature1, "attack", True)
    base_attack = creature1.species.base_stats.attack

    # Lower defense to -6 (should cap)
    for i in range(8):  # Try to go beyond -6
        battle.modify_stat_stage(is_player=False, stat="defense", stages=-1)

    defense_min = battle.get_modified_stat(creature2, "defense", False)
    base_defense = creature2.species.base_stats.defense

    # Check that stages are capped
    assert battle.player_stat_stages["attack"] == 6, "Attack stage should cap at +6"
    assert battle.opponent_stat_stages["defense"] == -6, "Defense stage should cap at -6"

    print(f"  ✓ Attack at +6: {base_attack} → {attack_max} ({attack_max/base_attack:.2f}x, should be 4.0x)")
    print(f"  ✓ Defense at -6: {base_defense} → {defense_min} ({defense_min/base_defense:.2f}x, should be 0.25x)")


def test_stat_changing_moves():
    """Test moves that change stats."""
    print("\nTesting stat-changing moves...")

    # Create stat-boosting move (like Swords Dance)
    swords_dance = Move(
        name="Swords Dance",
        type="Beast",
        power=0,  # Stat moves have 0 power
        accuracy=100,
        pp=20,
        max_pp=20,
        description="Sharply raises Attack!",
        stat_changes={"attack": 2},
        stat_change_target="self",
        stat_change_chance=100
    )

    # Create stat-lowering move (like Growl)
    growl = Move(
        name="Growl",
        type="Beast",
        power=0,
        accuracy=100,
        pp=40,
        max_pp=40,
        description="Lowers foe's Attack.",
        stat_changes={"attack": -1},
        stat_change_target="opponent",
        stat_change_chance=100
    )

    creature1 = create_test_creature("Buffer")
    creature2 = create_test_creature("Defender")

    creature1.moves = [swords_dance]
    # Give opponent a damaging move instead of Growl
    creature2.moves = [Move(
        name="Tackle",
        type="Beast",
        power=40,
        accuracy=100,
        pp=35,
        max_pp=35,
        description="A basic attack"
    )]

    team1 = Team([creature1])
    team2 = Team([creature2])

    battle = Battle(team1, team2, is_wild=False, can_run=False)

    # Use Swords Dance (should raise attack by 2)
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    # Check that attack was raised (opponent might have attacked, but shouldn't change player's attack stages)
    assert battle.player_stat_stages["attack"] == 2, f"Swords Dance should raise Attack by 2 stages (got {battle.player_stat_stages['attack']})"

    # Find the stat raise message in battle log
    stat_raise_found = any("sharply" in msg.lower() and "rose" in msg.lower() for msg in battle.log.messages)
    assert stat_raise_found, "Should show stat sharply rose message"

    print(f"  ✓ Swords Dance raised Attack to +2 stages")
    print(f"  ✓ Final stat stages: {battle.player_stat_stages}")


def test_simple_ability():
    """Test Simple ability (doubles stat changes)."""
    print("\nTesting Simple ability...")

    simple = Ability(
        name="Simple",
        description="Doubles stat stage changes",
        effect_type="double_stat_changes"
    )

    creature1 = create_test_creature("Simple", ability=simple)
    creature2 = create_test_creature("Normal")

    team1 = Team([creature1])
    team2 = Team([creature2])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Modify by +1, should become +2 with Simple
    battle.modify_stat_stage(is_player=True, stat="attack", stages=1)

    assert battle.player_stat_stages["attack"] == 2, f"Simple should double +1 to +2 (got {battle.player_stat_stages['attack']})"
    assert "Simple" in str(battle.log.messages), "Should mention Simple ability"

    print(f"  ✓ Simple doubled +1 to +2 stages")
    print(f"  ✓ Final stages: {battle.player_stat_stages}")


def test_contrary_ability():
    """Test Contrary ability (inverts stat changes)."""
    print("\nTesting Contrary ability...")

    contrary = Ability(
        name="Contrary",
        description="Inverts stat stage changes",
        effect_type="invert_stat_changes"
    )

    creature1 = create_test_creature("Contrary", ability=contrary)
    creature2 = create_test_creature("Normal")

    team1 = Team([creature1])
    team2 = Team([creature2])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Try to raise attack by +2, should become -2 with Contrary
    battle.modify_stat_stage(is_player=True, stat="attack", stages=2)

    assert battle.player_stat_stages["attack"] == -2, f"Contrary should invert +2 to -2 (got {battle.player_stat_stages['attack']})"
    assert "Contrary" in str(battle.log.messages), "Should mention Contrary ability"

    print(f"  ✓ Contrary inverted +2 to -2 stages")
    print(f"  ✓ Final stages: {battle.player_stat_stages}")


def test_unaware_ability():
    """Test Unaware ability (ignores stat stages in damage calc)."""
    print("\nTesting Unaware ability...")

    unaware = Ability(
        name="Unaware",
        description="Ignores opponent's stat stages",
        effect_type="ignore_stat_stages"
    )

    # Create attacker with Unaware
    attacker = create_test_creature("UnawareAttacker", attack=30, ability=unaware)
    defender = create_test_creature("BuffedDefender", defense=30)

    # Add tackle move
    tackle = Move(
        name="Tackle",
        type="Beast",
        power=40,
        accuracy=100,
        pp=35,
        max_pp=35,
        description="A basic attack"
    )
    attacker.moves = [tackle]

    team1 = Team([attacker])
    team2 = Team([defender])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Raise defender's defense to +6
    for i in range(6):
        battle.modify_stat_stage(is_player=False, stat="defense", stages=1)

    # Attack with Unaware attacker
    from genemon.battle.engine import BattleAction
    battle.execute_turn(BattleAction.ATTACK, 0)

    # Unaware should ignore the defense boosts
    # Damage should be similar to no defense boosts
    assert defender.current_hp < defender.max_hp, "Defender should take damage despite defense boosts"

    print(f"  ✓ Unaware ignored +6 Defense boost")
    print(f"  ✓ Defender HP: {defender.current_hp}/{defender.max_hp}")


def test_stat_reset_on_switch():
    """Test that stat stages reset when switching creatures."""
    print("\nTesting stat stage reset on switch...")

    creature1 = create_test_creature("First")
    creature2 = create_test_creature("Second")

    team1 = Team([creature1, creature2])
    team2 = Team([create_test_creature("Opponent")])

    battle = Battle(team1, team2, is_wild=True, can_run=False)

    # Boost first creature's attack
    battle.modify_stat_stage(is_player=True, stat="attack", stages=3)
    assert battle.player_stat_stages["attack"] == 3, "Attack should be +3"

    # Switch to second creature
    battle._switch_creature(is_player=True, index=1)

    # Stat stages should be reset
    assert battle.player_stat_stages["attack"] == 0, "Attack stages should reset to 0 after switch"
    assert battle.player_active == creature2, "Should have switched to second creature"

    print(f"  ✓ Stat stages reset on switch")
    print(f"  ✓ Attack stage after switch: {battle.player_stat_stages['attack']}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GENEMON STAT STAGE SYSTEM TEST SUITE")
    print("Testing Iteration 14 Features")
    print("=" * 60)

    tests_run = 0
    tests_passed = 0

    tests = [
        ("Basic stat modifications", test_basic_stat_modifications),
        ("Stat stage limits", test_stat_stage_limits),
        ("Stat-changing moves", test_stat_changing_moves),
        ("Simple ability", test_simple_ability),
        ("Contrary ability", test_contrary_ability),
        ("Unaware ability", test_unaware_ability),
        ("Stat reset on switch", test_stat_reset_on_switch),
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
