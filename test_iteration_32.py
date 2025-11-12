"""
Test suite for Iteration 32 - Code Quality & Performance Improvements

Tests:
1. Bare except clause fix in colors.py
2. CreatureSpecies primary_type and secondary_type properties
3. Type effectiveness caching
4. Color support error handling
5. NPC JSON loading system
6. Performance improvements validation
"""

import unittest
import sys
import os
from unittest.mock import patch, mock_open

# Add genemon to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'genemon'))

from genemon.core.creature import CreatureSpecies, CreatureStats, Move, Ability
from genemon.creatures.types import get_effectiveness, calculate_type_effectiveness, TYPES
from genemon.ui.colors import TerminalColors, ColorSupport
from genemon.data.npc_loader import NPCLoader


class TestBareExceptFix(unittest.TestCase):
    """Test that bare except clause has been fixed in colors.py"""

    def test_colors_no_bare_except(self):
        """Verify that colors.py doesn't contain bare except clauses"""
        colors_path = os.path.join(os.path.dirname(__file__), 'genemon', 'ui', 'colors.py')
        with open(colors_path, 'r') as f:
            content = f.read()

        # Check that there are no bare except clauses
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('except:'):
                self.fail(f"Bare except clause found at line {i+1}: {line}")

    def test_colors_specific_exceptions(self):
        """Verify that specific exceptions are caught"""
        colors_path = os.path.join(os.path.dirname(__file__), 'genemon', 'ui', 'colors.py')
        with open(colors_path, 'r') as f:
            content = f.read()

        # Should contain specific exception handling
        self.assertTrue('except (AttributeError, OSError)' in content or 'except AttributeError' in content)


class TestCreatureTypeProperties(unittest.TestCase):
    """Test primary_type and secondary_type properties"""

    def test_primary_type_single_type(self):
        """Test primary_type for single-type creature"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=1,
            name="TestMon",
            types=["Flame"],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        self.assertTrue(species.primary_type == "Flame"

    def test_primary_type_dual_type(self):
        """Test primary_type for dual-type creature"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=2,
            name="TestMon2",
            types=["Aqua", "Gale"],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        self.assertTrue(species.primary_type == "Aqua"

    def test_secondary_type_single_type(self):
        """Test secondary_type for single-type creature"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=1,
            name="TestMon",
            types=["Flame"],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        self.assertTrue(species.secondary_type is None

    def test_secondary_type_dual_type(self):
        """Test secondary_type for dual-type creature"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=2,
            name="TestMon2",
            types=["Aqua", "Gale"],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        self.assertTrue(species.secondary_type == "Gale"

    def test_primary_type_no_types(self):
        """Test primary_type when types list is empty"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=3,
            name="TestMon3",
            types=[],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        self.assertTrue(species.primary_type is None
        self.assertTrue(species.secondary_type is None


class TestTypeEffectivenessCaching(unittest.TestCase):
    """Test type effectiveness caching and performance"""

    def test_get_effectiveness_tuple(self):
        """Test get_effectiveness with tuple input"""
        # Super effective
        effectiveness = get_effectiveness("Flame", ("Leaf",))
        self.assertTrue(effectiveness == 2.0

        # Not very effective
        effectiveness = get_effectiveness("Flame", ("Aqua",))
        self.assertTrue(effectiveness == 0.5

        # No effect
        effectiveness = get_effectiveness("Volt", ("Terra",))
        self.assertTrue(effectiveness == 0.0

        # Neutral
        effectiveness = get_effectiveness("Flame", ("Brawl",))
        self.assertTrue(effectiveness == 1.0

    def test_calculate_type_effectiveness_list(self):
        """Test convenience wrapper that accepts lists"""
        # Super effective
        effectiveness = calculate_type_effectiveness("Flame", ["Leaf"])
        self.assertTrue(effectiveness == 2.0

        # Dual type calculation
        effectiveness = calculate_type_effectiveness("Flame", ["Aqua", "Gale"])
        self.assertTrue(effectiveness == 0.5

    def test_effectiveness_caching(self):
        """Test that caching is working (repeated calls use cache)"""
        # First call - will cache result
        result1 = get_effectiveness("Flame", ("Leaf",))

        # Second call - should use cache
        result2 = get_effectiveness("Flame", ("Leaf",))

        self.assertTrue(result1 == result2 == 2.0

        # Check cache info
        cache_info = get_effectiveness.cache_info()
        self.assertTrue(cache_info.hits > 0 or cache_info.misses > 0

    def test_dual_type_effectiveness(self):
        """Test dual-type effectiveness calculations"""
        # 2.0 * 2.0 = 4.0
        effectiveness = get_effectiveness("Brawl", ("Frost", "Shadow"))
        self.assertTrue(effectiveness == 4.0

        # 0.5 * 0.5 = 0.25
        effectiveness = get_effectiveness("Flame", ("Flame", "Aqua"))
        self.assertTrue(effectiveness == 0.25


class TestColorSupport(unittest.TestCase):
    """Test color support and error handling"""

    def test_terminal_colors_constants_exist(self):
        """Verify that color constants are defined"""
        self.assertTrue(hasattr(TerminalColors, 'RED')
        self.assertTrue(hasattr(TerminalColors, 'GREEN')
        self.assertTrue(hasattr(TerminalColors, 'BLUE')
        self.assertTrue(hasattr(TerminalColors, 'RESET')

    def test_color_support_enable_disable(self):
        """Test enabling and disabling color support"""
        original_state = ColorSupport.is_enabled()

        ColorSupport.enable()
        self.assertTrue(ColorSupport.is_enabled() is True

        ColorSupport.disable()
        self.assertTrue(ColorSupport.is_enabled() is False

        # Restore original state
        if original_state:
            ColorSupport.enable()
        else:
            ColorSupport.disable()

    def test_colorize_when_enabled(self):
        """Test colorize function when colors are enabled"""
        ColorSupport.enable()
        result = ColorSupport.colorize("test", TerminalColors.RED)
        self.assertTrue("test" in result

        # Restore original state
        ColorSupport._enabled = None

    def test_colorize_when_disabled(self):
        """Test colorize function when colors are disabled"""
        ColorSupport.disable()
        result = ColorSupport.colorize("test", TerminalColors.RED)
        self.assertTrue(result == "test"

        # Restore original state
        ColorSupport._enabled = None


class TestNPCJSONLoading(unittest.TestCase):
    """Test NPC JSON loading system"""

    def test_npc_loader_initialization(self):
        """Test NPCLoader initialization"""
        loader = NPCLoader()
        self.assertTrue(loader.data_file is not None
        self.assertTrue(loader.data_file.endswith('npcs.json')

    def test_npc_loader_custom_path(self):
        """Test NPCLoader with custom data file path"""
        custom_path = "/tmp/test_npcs.json"
        loader = NPCLoader(data_file=custom_path)
        self.assertTrue(loader.data_file == custom_path

    def test_npc_data_file_exists(self):
        """Verify that npcs.json exists"""
        loader = NPCLoader()
        self.assertTrue(os.path.exists(loader.data_file), f"NPC data file not found: {loader.data_file}"

    def test_load_npc_data(self):
        """Test loading NPC data from JSON"""
        loader = NPCLoader()
        npc_data = loader.load_npc_data()

        self.assertTrue(isinstance(npc_data, dict)
        self.assertTrue(len(npc_data) > 0

    def test_npc_data_structure(self):
        """Test that loaded NPC data has correct structure"""
        loader = NPCLoader()
        npc_data = loader.load_npc_data()

        # Check that at least one NPC has required fields
        if npc_data:
            first_npc = next(iter(npc_data.values()))
            self.assertTrue('id' in first_npc
            self.assertTrue('name' in first_npc
            self.assertTrue('type' in first_npc


class TestPerformanceImprovements(unittest.TestCase):
    """Test performance improvements and optimizations"""

    def test_type_effectiveness_performance(self):
        """Test that type effectiveness calculations are fast"""
        import time

        # Warm up cache
        get_effectiveness("Flame", ("Leaf",))

        # Time 1000 cached lookups
        start = time.time()
        for _ in range(1000):
            get_effectiveness("Flame", ("Leaf",))
        duration = time.time() - start

        # Should complete in less than 10ms for 1000 cached lookups
        self.assertTrue(duration < 0.01, f"Type effectiveness too slow: {duration*1000:.2f}ms for 1000 lookups"

    def test_creature_type_properties_fast(self):
        """Test that type properties are fast to access"""
        stats = CreatureStats(hp=50, attack=50, defense=50, special=50, speed=50)
        species = CreatureSpecies(
            id=1,
            name="TestMon",
            types=["Flame", "Gale"],
            base_stats=stats,
            moves=[],
            flavor_text="Test"
        )

        import time
        start = time.time()
        for _ in range(10000):
            _ = species.primary_type
            _ = species.secondary_type
        duration = time.time() - start

        # Should complete in less than 10ms for 10000 property accesses
        self.assertTrue(duration < 0.01, f"Type properties too slow: {duration*1000:.2f}ms for 10000 accesses"


class TestCodeQuality(unittest.TestCase):
    """Test code quality improvements"""

    def test_no_todo_comments(self):
        """Verify that there are no TODO/FIXME/HACK comments in core modules"""
        core_files = [
            'genemon/core/creature.py',
            'genemon/creatures/types.py',
            'genemon/ui/colors.py',
        ]

        for file_path in core_files:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()
                    self.assertTrue('TODO' not in content, f"TODO found in {file_path}"
                    self.assertTrue('FIXME' not in content, f"FIXME found in {file_path}"
                    self.assertTrue('HACK' not in content, f"HACK found in {file_path}"

    def test_proper_docstrings(self):
        """Verify that key functions have docstrings"""
        # Check get_effectiveness has docstring
        self.assertTrue(get_effectiveness.__doc__ is not None
        self.assertTrue(len(get_effectiveness.__doc__.strip()) > 0

        # Check calculate_type_effectiveness has docstring
        self.assertTrue(calculate_type_effectiveness.__doc__ is not None
        self.assertTrue(len(calculate_type_effectiveness.__doc__.strip()) > 0


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing code"""

    def test_get_effectiveness_still_works(self):
        """Test that existing get_effectiveness usage still works"""
        # This should work with tuple
        result = get_effectiveness("Flame", ("Leaf",))
        self.assertTrue(result == 2.0

    def test_calculate_type_effectiveness_new_function(self):
        """Test that new convenience function works correctly"""
        result = calculate_type_effectiveness("Flame", ["Leaf"])
        self.assertTrue(result == 2.0

        result = calculate_type_effectiveness("Flame", ["Leaf", "Metal"])
        self.assertTrue(result == 4.0  # 2.0 * 2.0


if __name__ == "__main__":
    unittest.main([__file__, "-v", "--tb=short"])
