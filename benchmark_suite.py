"""
Comprehensive benchmark suite for Genemon performance testing.

This module benchmarks critical game systems to identify performance bottlenecks
and ensure optimizations don't cause regressions.
"""

import random
from genemon.utils.profiler import PerformanceProfiler
from genemon.creatures.generator import CreatureGenerator
from genemon.sprites.generator import SpriteGenerator
from genemon.battle.engine import Battle
from genemon.battle.damage_calculator import DamageCalculator
from genemon.core.creature import Team
from genemon.core.save_system import GameState, SaveManager
from genemon.world.npc import NPCRegistry
from genemon.data.npc_loader import NPCLoader


class BenchmarkSuite:
    """
    Comprehensive performance benchmark suite.

    Benchmarks:
    - Creature generation (1, 10, 151 creatures)
    - Sprite generation (front, back, mini)
    - Battle system (single turn, full battle)
    - Damage calculation
    - Save/load system
    - NPC data loading
    """

    def __init__(self):
        """Initialize benchmark suite."""
        self.profiler = PerformanceProfiler()
        self.results = []

    def run_all(self, verbose: bool = True):
        """
        Run all benchmarks.

        Args:
            verbose: Whether to print progress
        """
        if verbose:
            print("\n" + "=" * 70)
            print("GENEMON PERFORMANCE BENCHMARK SUITE")
            print("=" * 70 + "\n")

        # Run benchmarks
        self.benchmark_creature_generation(verbose)
        self.benchmark_sprite_generation(verbose)
        self.benchmark_battle_system(verbose)
        self.benchmark_damage_calculation(verbose)
        self.benchmark_save_load(verbose)
        self.benchmark_npc_loading(verbose)

        # Print results
        if verbose:
            self.profiler.print_results()

        return self.profiler.get_results()

    def benchmark_creature_generation(self, verbose: bool = True):
        """Benchmark creature generation performance."""
        if verbose:
            print("Benchmarking creature generation...")

        seed = 12345

        # Single creature
        with self.profiler.measure("creature_gen_single"):
            for _ in range(10):
                generator = CreatureGenerator(seed)
                generator._generate_creature(
                    creature_id=1,
                    power_level="basic",
                    stage=1
                )

        # Full roster (151 creatures)
        with self.profiler.measure("creature_gen_full_roster"):
            generator = CreatureGenerator(seed)
            generator.generate_all_creatures()

        self.profiler.add_metadata("creature_gen_full_roster", {"creatures": 151})

        if verbose:
            print("  ✓ Creature generation benchmarks complete")

    def benchmark_sprite_generation(self, verbose: bool = True):
        """Benchmark sprite generation performance."""
        if verbose:
            print("Benchmarking sprite generation...")

        sprite_gen = SpriteGenerator()

        # Front sprite (56x56)
        with self.profiler.measure("sprite_gen_front"):
            for _ in range(20):
                sprite_gen.generate_front_sprite(
                    archetype="quadruped",
                    primary_color=(200, 100, 50),
                    secondary_color=(100, 50, 200)
                )

        # Back sprite (56x56)
        with self.profiler.measure("sprite_gen_back"):
            for _ in range(20):
                sprite_gen.generate_back_sprite(
                    archetype="quadruped",
                    primary_color=(200, 100, 50),
                    secondary_color=(100, 50, 200)
                )

        # Mini sprite (16x16)
        with self.profiler.measure("sprite_gen_mini"):
            for _ in range(20):
                sprite_gen.generate_mini_sprite(
                    archetype="quadruped",
                    primary_color=(200, 100, 50)
                )

        if verbose:
            print("  ✓ Sprite generation benchmarks complete")

    def benchmark_battle_system(self, verbose: bool = True):
        """Benchmark battle system performance."""
        if verbose:
            print("Benchmarking battle system...")

        # Create test creatures
        generator = CreatureGenerator(12345)
        species_list = generator.generate(10)

        # Create teams
        team1 = Team()
        team2 = Team()

        for i in range(3):
            from genemon.core.creature import Creature
            team1.add(Creature(species_list[i], level=20))
            team2.add(Creature(species_list[i + 3], level=20))

        # Single battle turn
        with self.profiler.measure("battle_single_turn"):
            for _ in range(10):
                battle = Battle(team1, team2, is_wild=False)
                # Simulate one turn of battle
                move1 = team1.active.moves[0] if team1.active.moves else None
                move2 = team2.active.moves[0] if team2.active.moves else None
                if move1 and move2:
                    battle._execute_turn(move1, move2)

        # Full battle simulation
        with self.profiler.measure("battle_full_simulation"):
            battle = Battle(team1, team2, is_wild=False)
            turn_count = 0
            max_turns = 100  # Safety limit

            while not battle.is_over() and turn_count < max_turns:
                move1 = team1.active.moves[0] if team1.active.moves else None
                move2 = team2.active.moves[0] if team2.active.moves else None
                if move1 and move2:
                    battle._execute_turn(move1, move2)
                turn_count += 1

        self.profiler.add_metadata("battle_full_simulation", {"turns": turn_count})

        if verbose:
            print("  ✓ Battle system benchmarks complete")

    def benchmark_damage_calculation(self, verbose: bool = True):
        """Benchmark damage calculation performance."""
        if verbose:
            print("Benchmarking damage calculation...")

        # Create test creatures
        generator = CreatureGenerator(12345)
        species_list = generator.generate(2)

        from genemon.core.creature import Creature
        attacker = Creature(species_list[0], level=50)
        defender = Creature(species_list[1], level=50)

        calculator = DamageCalculator()

        # Damage calculation
        if attacker.moves:
            move = attacker.moves[0]
            with self.profiler.measure("damage_calculation"):
                for _ in range(1000):
                    calculator.calculate_damage(
                        attacker=attacker,
                        defender=defender,
                        move=move,
                        weather=None,
                        attacker_stat_stages={},
                        defender_stat_stages={}
                    )

        # Critical hit check
        with self.profiler.measure("critical_hit_check"):
            for _ in range(1000):
                calculator.check_critical_hit(attacker, move)

        if verbose:
            print("  ✓ Damage calculation benchmarks complete")

    def benchmark_save_load(self, verbose: bool = True):
        """Benchmark save/load system performance."""
        if verbose:
            print("Benchmarking save/load system...")

        save_manager = SaveManager()

        # Create test game state
        with self.profiler.measure("save_create_new_game"):
            state = save_manager.create_new_game(
                save_name="benchmark_test",
                player_name="Benchmark",
                starter_choice=0
            )

        # Save game
        with self.profiler.measure("save_game"):
            for _ in range(5):
                save_manager.save_game(state)

        # Load game
        with self.profiler.measure("load_game"):
            for _ in range(5):
                save_manager.load_game("benchmark_test")

        # Cleanup
        import os
        try:
            os.remove(save_manager._get_save_path("benchmark_test"))
        except:
            pass

        if verbose:
            print("  ✓ Save/load benchmarks complete")

    def benchmark_npc_loading(self, verbose: bool = True):
        """Benchmark NPC data loading performance."""
        if verbose:
            print("Benchmarking NPC data loading...")

        # JSON loading
        with self.profiler.measure("npc_json_load"):
            for _ in range(10):
                loader = NPCLoader()
                loader.load_npc_data()

        # Full NPC object creation
        with self.profiler.measure("npc_full_load"):
            for _ in range(10):
                loader = NPCLoader()
                loader.load_all_npcs()

        # NPCRegistry initialization (JSON mode)
        with self.profiler.measure("npc_registry_json_init"):
            for _ in range(10):
                NPCRegistry(use_json=True)

        # NPCRegistry initialization (legacy mode)
        with self.profiler.measure("npc_registry_legacy_init"):
            for _ in range(10):
                NPCRegistry(use_json=False)

        if verbose:
            print("  ✓ NPC loading benchmarks complete")


def main():
    """Run benchmark suite and print results."""
    print("\nStarting Genemon performance benchmarks...")
    print("This may take a minute...\n")

    suite = BenchmarkSuite()
    results = suite.run_all(verbose=True)

    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"\nTotal benchmarks: {len(results)}")
    print(f"Total time: {sum(r.duration for r in results):.2f}s")

    # Highlight slowest operations
    print("\nSlowest operations:")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result.name}: {result.duration:.4f}s ({result.iterations} iterations)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
