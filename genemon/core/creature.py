"""
Creature data model and related classes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json


@dataclass
class Move:
    """Represents a move/ability that a creature can use."""

    name: str
    type: str
    power: int
    accuracy: int
    pp: int
    max_pp: int
    description: str

    def to_dict(self) -> dict:
        """Convert move to dictionary for serialization."""
        return {
            'name': self.name,
            'type': self.type,
            'power': self.power,
            'accuracy': self.accuracy,
            'pp': self.pp,
            'max_pp': self.max_pp,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Move':
        """Create move from dictionary."""
        return cls(**data)


@dataclass
class CreatureStats:
    """Base stats for a creature species."""

    hp: int
    attack: int
    defense: int
    special: int
    speed: int

    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        return {
            'hp': self.hp,
            'attack': self.attack,
            'defense': self.defense,
            'special': self.special,
            'speed': self.speed
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CreatureStats':
        """Create stats from dictionary."""
        return cls(**data)


@dataclass
class CreatureSpecies:
    """
    Defines a species of creature (e.g., one of the 151 generated creatures).
    This is the template that individual creature instances are based on.
    """

    id: int
    name: str
    types: List[str]
    base_stats: CreatureStats
    moves: List[Move]
    flavor_text: str
    evolution_level: Optional[int] = None
    evolves_into: Optional[int] = None  # ID of evolved form
    sprite_data: Optional[Dict[str, any]] = None  # Contains front, back, mini sprites

    def to_dict(self) -> dict:
        """Convert species to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'types': self.types,
            'base_stats': self.base_stats.to_dict(),
            'moves': [m.to_dict() for m in self.moves],
            'flavor_text': self.flavor_text,
            'evolution_level': self.evolution_level,
            'evolves_into': self.evolves_into,
            'sprite_data': self.sprite_data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CreatureSpecies':
        """Create species from dictionary."""
        data['base_stats'] = CreatureStats.from_dict(data['base_stats'])
        data['moves'] = [Move.from_dict(m) for m in data['moves']]
        return cls(**data)


@dataclass
class Creature:
    """
    An individual creature instance owned by a player or NPC.
    Has level, experience, current stats, etc.
    """

    species: CreatureSpecies
    level: int
    current_hp: int = 0  # 0 means will be set to max_hp in __post_init__
    max_hp: int = field(init=False)
    exp: int = 0
    nickname: Optional[str] = None

    # Current battle stats (can be modified by stat changes)
    attack: int = field(init=False)
    defense: int = field(init=False)
    special: int = field(init=False)
    speed: int = field(init=False)

    def __post_init__(self):
        """Calculate initial stats based on level and base stats."""
        self._calculate_stats()

    def _calculate_stats(self):
        """Calculate stats based on level and base stats (simplified formula)."""
        base = self.species.base_stats

        # Simplified stat calculation (similar to Pokemon Gen 1)
        # HP has a different formula
        self.max_hp = int(((base.hp * 2 * self.level) / 100) + self.level + 10)

        # Other stats
        self.attack = int(((base.attack * 2 * self.level) / 100) + 5)
        self.defense = int(((base.defense * 2 * self.level) / 100) + 5)
        self.special = int(((base.special * 2 * self.level) / 100) + 5)
        self.speed = int(((base.speed * 2 * self.level) / 100) + 5)

        # Set current HP to max if this is a new calculation
        if self.current_hp == 0 or self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def get_display_name(self) -> str:
        """Get the display name (nickname or species name)."""
        return self.nickname if self.nickname else self.species.name

    def is_fainted(self) -> bool:
        """Check if creature has fainted."""
        return self.current_hp <= 0

    def heal(self, amount: int = None):
        """Heal creature by amount, or fully heal if no amount specified."""
        if amount is None:
            self.current_hp = self.max_hp
        else:
            self.current_hp = min(self.current_hp + amount, self.max_hp)

    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage dealt."""
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        return actual_damage

    def gain_exp(self, amount: int) -> bool:
        """
        Gain experience points. Returns True if leveled up.
        Uses a simplified leveling formula.
        """
        self.exp += amount
        exp_needed = self._exp_for_next_level()

        if self.exp >= exp_needed and self.level < 100:
            self.level += 1
            self._calculate_stats()
            self.current_hp = self.max_hp  # Heal on level up
            return True

        return False

    def _exp_for_next_level(self) -> int:
        """Calculate experience needed for next level (medium-fast growth)."""
        return int((self.level + 1) ** 3)

    def can_evolve(self) -> bool:
        """Check if creature can evolve."""
        return (self.species.evolution_level is not None and
                self.level >= self.species.evolution_level and
                self.species.evolves_into is not None)

    def to_dict(self) -> dict:
        """Convert creature to dictionary for serialization."""
        return {
            'species_id': self.species.id,
            'level': self.level,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'exp': self.exp,
            'nickname': self.nickname
        }

    @classmethod
    def from_dict(cls, data: dict, species: CreatureSpecies) -> 'Creature':
        """Create creature from dictionary and species reference."""
        creature = cls(
            species=species,
            level=data['level'],
            current_hp=data['current_hp'],
            exp=data.get('exp', 0),
            nickname=data.get('nickname')
        )
        # Override max_hp from saved data if needed
        if 'max_hp' in data and data['max_hp'] != creature.max_hp:
            creature.max_hp = data['max_hp']
        return creature


@dataclass
class Team:
    """A team of up to 6 creatures."""

    creatures: List[Creature] = field(default_factory=list)
    max_size: int = 6

    def add_creature(self, creature: Creature) -> bool:
        """Add a creature to the team. Returns True if successful."""
        if len(self.creatures) < self.max_size:
            self.creatures.append(creature)
            return True
        return False

    def remove_creature(self, index: int) -> Optional[Creature]:
        """Remove and return a creature at the given index."""
        if 0 <= index < len(self.creatures):
            return self.creatures.pop(index)
        return None

    def swap_creatures(self, index1: int, index2: int):
        """Swap two creatures in the team."""
        if (0 <= index1 < len(self.creatures) and
            0 <= index2 < len(self.creatures)):
            self.creatures[index1], self.creatures[index2] = \
                self.creatures[index2], self.creatures[index1]

    def get_first_active(self) -> Optional[Creature]:
        """Get the first non-fainted creature."""
        for creature in self.creatures:
            if not creature.is_fainted():
                return creature
        return None

    def has_active_creatures(self) -> bool:
        """Check if team has any non-fainted creatures."""
        return self.get_first_active() is not None

    def heal_all(self):
        """Fully heal all creatures in the team."""
        for creature in self.creatures:
            creature.heal()

    def to_dict(self) -> dict:
        """Convert team to dictionary for serialization."""
        return {
            'creatures': [c.to_dict() for c in self.creatures],
            'max_size': self.max_size
        }

    @classmethod
    def from_dict(cls, data: dict, species_dict: Dict[int, CreatureSpecies]) -> 'Team':
        """Create team from dictionary and species lookup."""
        team = cls(max_size=data.get('max_size', 6))
        for creature_data in data['creatures']:
            species = species_dict[creature_data['species_id']]
            creature = Creature.from_dict(creature_data, species)
            team.add_creature(creature)
        return team
