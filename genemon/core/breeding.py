"""
Creature breeding system.
Allows players to breed two creatures to produce an egg that hatches into a level 1 creature.
"""

import random
from typing import Optional, Tuple
from .creature import Creature, CreatureSpecies, Move
from .shiny import roll_shiny


class BreedingCenter:
    """Manages creature breeding operations."""

    def __init__(self):
        """Initialize the breeding center."""
        self.breeding_pairs = []  # List of (parent1, parent2) tuples currently breeding
        self.eggs = []  # List of eggs waiting to hatch

    def can_breed(self, parent1: Creature, parent2: Creature) -> Tuple[bool, str]:
        """
        Check if two creatures can breed together.

        Args:
            parent1: First parent creature
            parent2: Second parent creature

        Returns:
            (can_breed, reason) tuple
        """
        # Check if same species
        if parent1.species.id != parent2.species.id:
            return False, "Creatures must be the same species to breed."

        # Check if both are healthy
        if parent1.is_fainted() or parent2.is_fainted():
            return False, "Both creatures must be healthy to breed."

        # Check if either is too low level
        if parent1.level < 15 or parent2.level < 15:
            return False, "Both creatures must be at least level 15 to breed."

        # Check if they're the same creature instance
        if parent1 is parent2:
            return False, "A creature cannot breed with itself."

        return True, "These creatures can breed!"

    def start_breeding(self, parent1: Creature, parent2: Creature) -> Tuple[bool, str]:
        """
        Start breeding two creatures.

        Args:
            parent1: First parent creature
            parent2: Second parent creature

        Returns:
            (success, message) tuple
        """
        can_breed, reason = self.can_breed(parent1, parent2)

        if not can_breed:
            return False, reason

        # Create breeding pair
        self.breeding_pairs.append((parent1, parent2))

        return True, f"Breeding started! {parent1.get_display_name()} and {parent2.get_display_name()} are now at the breeding center."

    def generate_egg(self, parent1: Creature, parent2: Creature, rng: Optional[random.Random] = None) -> 'Egg':
        """
        Generate an egg from two parent creatures.

        Args:
            parent1: First parent creature
            parent2: Second parent creature
            rng: Optional random number generator

        Returns:
            Egg instance
        """
        if rng is None:
            rng = random

        # Egg inherits species from parents (same species required)
        species = parent1.species

        # Shiny chance is increased for breeding (1/512 instead of 1/4096)
        is_shiny = rng.randint(1, 512) == 1

        # Inherit up to 3 moves from parents
        inherited_moves = []
        parent_moves = parent1.moves + parent2.moves

        # Remove duplicates
        unique_moves = {}
        for move in parent_moves:
            if move.name not in unique_moves:
                unique_moves[move.name] = move

        # Pick up to 3 random moves
        available_moves = list(unique_moves.values())
        rng.shuffle(available_moves)
        inherited_moves = available_moves[:min(3, len(available_moves))]

        egg = Egg(
            species=species,
            is_shiny=is_shiny,
            inherited_moves=inherited_moves
        )

        return egg

    def collect_egg(self, pair_index: int) -> Optional['Egg']:
        """
        Collect an egg from a breeding pair.

        Args:
            pair_index: Index of the breeding pair

        Returns:
            Egg instance if successful, None otherwise
        """
        if 0 <= pair_index < len(self.breeding_pairs):
            parent1, parent2 = self.breeding_pairs[pair_index]
            egg = self.generate_egg(parent1, parent2)
            self.eggs.append(egg)
            # Remove breeding pair
            self.breeding_pairs.pop(pair_index)
            return egg

        return None

    def hatch_egg(self, egg_index: int) -> Optional[Creature]:
        """
        Hatch an egg into a level 1 creature.

        Args:
            egg_index: Index of the egg to hatch

        Returns:
            Newly hatched Creature instance if successful, None otherwise
        """
        if 0 <= egg_index < len(self.eggs):
            egg = self.eggs.pop(egg_index)
            return egg.hatch()

        return None


class Egg:
    """Represents an unhatched creature egg."""

    def __init__(
        self,
        species: CreatureSpecies,
        is_shiny: bool = False,
        inherited_moves: list[Move] = None
    ):
        """
        Initialize an egg.

        Args:
            species: The species that will hatch
            is_shiny: Whether the hatched creature will be shiny
            inherited_moves: Moves inherited from parents
        """
        self.species = species
        self.is_shiny = is_shiny
        self.inherited_moves = inherited_moves or []
        self.steps_to_hatch = 1000  # Steps needed to hatch

    def hatch(self) -> Creature:
        """
        Hatch the egg into a level 1 creature.

        Returns:
            Newly hatched Creature instance
        """
        import copy

        # Create level 1 creature
        creature = Creature(
            species=self.species,
            level=1,
            is_shiny=self.is_shiny
        )

        # Apply inherited moves (keep at most 4 moves total)
        if self.inherited_moves:
            # Start with species default moves
            default_moves = creature.moves[:1]  # Keep first default move

            # Add inherited moves
            all_moves = default_moves + [copy.deepcopy(m) for m in self.inherited_moves]

            # Limit to 4 moves
            creature.moves = all_moves[:4]

        return creature

    def to_dict(self) -> dict:
        """Convert egg to dictionary for serialization."""
        return {
            'species_id': self.species.id,
            'is_shiny': self.is_shiny,
            'inherited_moves': [m.to_dict() for m in self.inherited_moves],
            'steps_to_hatch': self.steps_to_hatch
        }

    @classmethod
    def from_dict(cls, data: dict, species: CreatureSpecies) -> 'Egg':
        """Create egg from dictionary."""
        inherited_moves = [Move.from_dict(m) for m in data.get('inherited_moves', [])]

        egg = cls(
            species=species,
            is_shiny=data.get('is_shiny', False),
            inherited_moves=inherited_moves
        )

        egg.steps_to_hatch = data.get('steps_to_hatch', 1000)

        return egg
