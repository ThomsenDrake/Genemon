"""
Test suite for critical hit system.
"""

import random
from genemon.core.creature import Creature, CreatureSpecies, CreatureStats, Move, Ability
from genemon.battle.engine import Battle
from genemon.core.creature import Team


def test_critical_hit_system():
    """Test critical hit mechanics."""
    print("=" * 60)
    print("GENEMON CRITICAL HIT SYSTEM TEST SUITE")
    print("=" * 60)
    print()

    tests_passed = 0
    tests_failed = 0

    # Test 1: Base critical hit chance (should happen roughly 6.25% of the time)
    print("Testing base critical hit rate...")

    # Create a simple creature with normal moves
    species = CreatureSpecies(
        id=1,
        name="TestCreature",
        types=["Beast"],
        base_stats=CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50),
        moves=[Move("Normal Attack", "Beast", 40, 100, 20, 20, "A normal attack", crit_rate=0)],
        flavor_text="Test creature",
        ability=None
    )

    creature1 = Creature(species=species, level=10)
    creature2 = Creature(species=species, level=10)

    team1 = Team(max_size=1)
    team2 = Team(max_size=1)
    team1.add_creature(creature1)
    team2.add_creature(creature2)

    # Run many battles to check crit rate
    crits = 0
    total_attacks = 1000

    for _ in range(total_attacks):
        battle = Battle(team1, team2, is_wild=True, can_run=False)
        # Force a critical hit check
        is_crit = battle._check_critical_hit(creature1, creature2, creature1.moves[0], True)
        if is_crit:
            crits += 1

    crit_rate = (crits / total_attacks) * 100
    expected_rate = 6.25

    # Allow for some variance (between 4% and 9%)
    if 4.0 <= crit_rate <= 9.0:
        print(f"  ✓ Base crit rate: {crit_rate:.2f}% (expected ~{expected_rate}%)")
        tests_passed += 1
    else:
        print(f"  ✗ Base crit rate: {crit_rate:.2f}% (expected ~{expected_rate}%)")
        tests_failed += 1

    # Test 2: High crit rate moves (should be roughly 12.5%)
    print("\nTesting high crit rate moves...")

    high_crit_move = Move("Slash", "Beast", 40, 100, 20, 20, "High crit ratio", crit_rate=1)
    creature1.moves = [high_crit_move]

    crits = 0
    for _ in range(total_attacks):
        battle = Battle(team1, team2, is_wild=True, can_run=False)
        is_crit = battle._check_critical_hit(creature1, creature2, creature1.moves[0], True)
        if is_crit:
            crits += 1

    high_crit_rate = (crits / total_attacks) * 100
    expected_high_rate = 12.5

    if 10.0 <= high_crit_rate <= 16.0:
        print(f"  ✓ High crit rate: {high_crit_rate:.2f}% (expected ~{expected_high_rate}%)")
        tests_passed += 1
    else:
        print(f"  ✗ High crit rate: {high_crit_rate:.2f}% (expected ~{expected_high_rate}%)")
        tests_failed += 1

    # Test 3: Super Luck ability (increases crit stage)
    print("\nTesting Super Luck ability...")

    super_luck_ability = Ability("Super Luck", "Heightens critical hit ratio", "boost_crit")
    species_lucky = CreatureSpecies(
        id=2,
        name="LuckyCreature",
        types=["Beast"],
        base_stats=CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50),
        moves=[Move("Normal Attack", "Beast", 40, 100, 20, 20, "A normal attack", crit_rate=0)],
        flavor_text="Lucky creature",
        ability=super_luck_ability
    )

    lucky_creature = Creature(species=species_lucky, level=10)
    team1_lucky = Team(max_size=1)
    team1_lucky.add_creature(lucky_creature)

    crits = 0
    for _ in range(total_attacks):
        battle = Battle(team1_lucky, team2, is_wild=True, can_run=False)
        is_crit = battle._check_critical_hit(lucky_creature, creature2, lucky_creature.moves[0], True)
        if is_crit:
            crits += 1

    lucky_crit_rate = (crits / total_attacks) * 100

    # Super Luck should increase base rate from 6.25% to 12.5%
    if 10.0 <= lucky_crit_rate <= 16.0:
        print(f"  ✓ Super Luck crit rate: {lucky_crit_rate:.2f}% (expected ~12.5%)")
        tests_passed += 1
    else:
        print(f"  ✗ Super Luck crit rate: {lucky_crit_rate:.2f}% (expected ~12.5%)")
        tests_failed += 1

    # Test 4: Battle Armor prevents crits
    print("\nTesting Battle Armor ability...")

    battle_armor = Ability("Battle Armor", "Blocks critical hits", "no_crits")
    species_armored = CreatureSpecies(
        id=3,
        name="ArmoredCreature",
        types=["Metal"],
        base_stats=CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50),
        moves=[Move("Normal Attack", "Metal", 40, 100, 20, 20, "A normal attack")],
        flavor_text="Armored creature",
        ability=battle_armor
    )

    armored_creature = Creature(species=species_armored, level=10)
    team2_armored = Team(max_size=1)
    team2_armored.add_creature(armored_creature)

    crits = 0
    for _ in range(total_attacks):
        battle = Battle(team1, team2_armored, is_wild=True, can_run=False)
        is_crit = battle._check_critical_hit(creature1, armored_creature, creature1.moves[0], True)
        if is_crit:
            crits += 1

    if crits == 0:
        print(f"  ✓ Battle Armor blocked all crits (0/{total_attacks})")
        tests_passed += 1
    else:
        print(f"  ✗ Battle Armor failed to block some crits ({crits}/{total_attacks})")
        tests_failed += 1

    # Test 5: Critical hit damage (2x multiplier)
    print("\nTesting critical hit damage multiplier...")

    creature1.current_hp = creature1.max_hp
    creature2.current_hp = creature2.max_hp

    # Run multiple trials to account for random factor
    battle = Battle(team1, team2, is_wild=True, can_run=False)
    total_normal = 0
    total_crit = 0
    trials = 100

    for _ in range(trials):
        normal_damage = battle._calculate_damage(creature1, creature2, creature1.moves[0], is_critical=False)
        crit_damage = battle._calculate_damage(creature1, creature2, creature1.moves[0], is_critical=True)
        total_normal += normal_damage
        total_crit += crit_damage

    avg_normal = total_normal / trials
    avg_crit = total_crit / trials
    damage_ratio = avg_crit / avg_normal

    if 1.9 <= damage_ratio <= 2.1:
        print(f"  ✓ Crit damage multiplier: {damage_ratio:.2f}x (expected ~2.0x)")
        print(f"    Avg Normal: {avg_normal:.1f} damage, Avg Crit: {avg_crit:.1f} damage")
        tests_passed += 1
    else:
        print(f"  ✗ Crit damage multiplier: {damage_ratio:.2f}x (expected ~2.0x)")
        tests_failed += 1

    # Test 6: Sniper ability (3x crit damage)
    print("\nTesting Sniper ability (3x crit damage)...")

    sniper_ability = Ability("Sniper", "Boosts critical hit power", "crit_power_boost")
    species_sniper = CreatureSpecies(
        id=4,
        name="SniperCreature",
        types=["Beast"],
        base_stats=CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50),
        moves=[Move("Normal Attack", "Beast", 40, 100, 20, 20, "A normal attack")],
        flavor_text="Sniper creature",
        ability=sniper_ability
    )

    sniper_creature = Creature(species=species_sniper, level=10)
    team1_sniper = Team(max_size=1)
    team1_sniper.add_creature(sniper_creature)

    battle = Battle(team1_sniper, team2, is_wild=True, can_run=False)

    # Run multiple trials to account for random factor
    total_normal = 0
    total_crit = 0
    trials = 100

    for _ in range(trials):
        normal_sniper_damage = battle._calculate_damage(sniper_creature, creature2, sniper_creature.moves[0], is_critical=False)
        crit_sniper_damage = battle._calculate_damage(sniper_creature, creature2, sniper_creature.moves[0], is_critical=True)
        total_normal += normal_sniper_damage
        total_crit += crit_sniper_damage

    avg_normal = total_normal / trials
    avg_crit = total_crit / trials
    sniper_ratio = avg_crit / avg_normal

    if 2.7 <= sniper_ratio <= 3.3:
        print(f"  ✓ Sniper crit multiplier: {sniper_ratio:.2f}x (expected ~3.0x)")
        print(f"    Avg Normal: {avg_normal:.1f} damage, Avg Crit: {avg_crit:.1f} damage")
        tests_passed += 1
    else:
        print(f"  ✗ Sniper crit multiplier: {sniper_ratio:.2f}x (expected ~3.0x)")
        tests_failed += 1

    # Test 7: Shell Armor also prevents crits
    print("\nTesting Shell Armor ability...")

    shell_armor = Ability("Shell Armor", "Blocks critical hits", "no_crits")
    species_shell = CreatureSpecies(
        id=5,
        name="ShellCreature",
        types=["Aqua"],
        base_stats=CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50),
        moves=[Move("Normal Attack", "Aqua", 40, 100, 20, 20, "A normal attack")],
        flavor_text="Shell creature",
        ability=shell_armor
    )

    shell_creature = Creature(species=species_shell, level=10)
    team2_shell = Team(max_size=1)
    team2_shell.add_creature(shell_creature)

    crits = 0
    for _ in range(total_attacks):
        battle = Battle(team1, team2_shell, is_wild=True, can_run=False)
        is_crit = battle._check_critical_hit(creature1, shell_creature, creature1.moves[0], True)
        if is_crit:
            crits += 1

    if crits == 0:
        print(f"  ✓ Shell Armor blocked all crits (0/{total_attacks})")
        tests_passed += 1
    else:
        print(f"  ✗ Shell Armor failed to block some crits ({crits}/{total_attacks})")
        tests_failed += 1

    # Print summary
    print()
    print("=" * 60)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("=" * 60)

    return tests_passed, tests_failed


if __name__ == "__main__":
    test_critical_hit_system()
