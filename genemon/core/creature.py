"""
Creature data model and related classes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json


class StatusEffect(Enum):
    """Status effects that can afflict creatures."""
    NONE = "none"
    BURN = "burn"        # Deals damage each turn, reduces attack
    POISON = "poison"    # Deals damage each turn
    PARALYSIS = "paralysis"  # May prevent movement, reduces speed
    SLEEP = "sleep"      # Cannot move for several turns
    FROZEN = "frozen"    # Cannot move until thawed


@dataclass
class Badge:
    """Represents a gym badge earned by the player."""

    badge_id: str
    name: str
    type: str  # Type specialty of the gym
    gym_leader: str
    description: str

    def to_dict(self) -> dict:
        """Convert badge to dictionary for serialization."""
        return {
            'badge_id': self.badge_id,
            'name': self.name,
            'type': self.type,
            'gym_leader': self.gym_leader,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Badge':
        """Deserialize badge from dictionary."""
        return cls(
            badge_id=data['badge_id'],
            name=data['name'],
            type=data['type'],
            gym_leader=data['gym_leader'],
            description=data['description']
        )


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
    status_effect: Optional[StatusEffect] = None  # Status effect inflicted
    status_chance: int = 0  # Chance (0-100) to inflict status
    crit_rate: int = 0  # Critical hit stage (0 = normal, 1 = high, 2 = always)
    multi_hit: Tuple[int, int] = (1, 1)  # Multi-hit range (min, max) - (2, 5) for multi-hit moves
    recoil_percent: int = 0  # Recoil damage as % of damage dealt (e.g., 25 = 25% recoil)
    priority: int = 0  # Priority level (-7 to +7, higher goes first)
    stat_changes: Optional[Dict[str, int]] = None  # Stat stage changes: {"attack": 2, "defense": 1}
    stat_change_target: str = "self"  # "self" or "opponent" - who gets the stat changes
    stat_change_chance: int = 100  # Chance (0-100) to apply stat changes

    def to_dict(self) -> dict:
        """Convert move to dictionary for serialization."""
        return {
            'name': self.name,
            'type': self.type,
            'power': self.power,
            'accuracy': self.accuracy,
            'pp': self.pp,
            'max_pp': self.max_pp,
            'description': self.description,
            'status_effect': self.status_effect.value if self.status_effect else None,
            'status_chance': self.status_chance,
            'crit_rate': self.crit_rate,
            'multi_hit': list(self.multi_hit),
            'recoil_percent': self.recoil_percent,
            'priority': self.priority,
            'stat_changes': self.stat_changes,
            'stat_change_target': self.stat_change_target,
            'stat_change_chance': self.stat_change_chance
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Move':
        """Create move from dictionary."""
        status_effect_val = data.get('status_effect')
        if status_effect_val:
            data['status_effect'] = StatusEffect(status_effect_val)
        # Default values for backward compatibility
        if 'crit_rate' not in data:
            data['crit_rate'] = 0
        if 'multi_hit' not in data:
            data['multi_hit'] = [1, 1]
        if 'recoil_percent' not in data:
            data['recoil_percent'] = 0
        if 'priority' not in data:
            data['priority'] = 0
        if 'stat_changes' not in data:
            data['stat_changes'] = None
        if 'stat_change_target' not in data:
            data['stat_change_target'] = "self"
        if 'stat_change_chance' not in data:
            data['stat_change_chance'] = 100
        # Convert list back to tuple for multi_hit
        if isinstance(data.get('multi_hit'), list):
            data['multi_hit'] = tuple(data['multi_hit'])
        return cls(**data)


@dataclass
class Ability:
    """Represents a creature's passive ability."""

    name: str
    description: str
    effect_type: str  # e.g., "stat_boost", "weather", "status_immune", "type_boost"

    def to_dict(self) -> dict:
        """Convert ability to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'effect_type': self.effect_type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Ability':
        """Create ability from dictionary."""
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
    learnset: Optional[Dict[int, Move]] = None  # Level -> Move mapping for level-up moves
    tm_compatible: Optional[List[str]] = None  # List of TM move names this species can learn
    is_legendary: bool = False  # Marks rare, powerful creatures (IDs 146-151)
    ability: Optional[Ability] = None  # Passive ability for this species

    def to_dict(self) -> dict:
        """Convert species to dictionary for serialization."""
        result = {
            'id': self.id,
            'name': self.name,
            'types': self.types,
            'base_stats': self.base_stats.to_dict(),
            'moves': [m.to_dict() for m in self.moves],
            'flavor_text': self.flavor_text,
            'evolution_level': self.evolution_level,
            'evolves_into': self.evolves_into,
            'sprite_data': self.sprite_data,
            'is_legendary': self.is_legendary
        }
        # Add learnset if present
        if self.learnset:
            result['learnset'] = {str(level): move.to_dict() for level, move in self.learnset.items()}
        # Add TM compatibility if present
        if self.tm_compatible:
            result['tm_compatible'] = self.tm_compatible
        # Add ability if present
        if self.ability:
            result['ability'] = self.ability.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict) -> 'CreatureSpecies':
        """Create species from dictionary."""
        data['base_stats'] = CreatureStats.from_dict(data['base_stats'])
        data['moves'] = [Move.from_dict(m) for m in data['moves']]
        # Deserialize learnset if present
        if 'learnset' in data and data['learnset']:
            data['learnset'] = {int(level): Move.from_dict(move) for level, move in data['learnset'].items()}
        # Deserialize ability if present
        if 'ability' in data and data['ability']:
            data['ability'] = Ability.from_dict(data['ability'])
        # TM compatibility is already a list, no conversion needed
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

    # Individual move instances (separate from species moves for PP tracking)
    moves: List[Move] = field(default_factory=list, init=False)

    # Status effect
    status: StatusEffect = StatusEffect.NONE
    status_turns: int = 0  # Number of turns status has been active (for sleep, etc.)

    # Current battle stats (can be modified by stat changes)
    attack: int = field(init=False)
    defense: int = field(init=False)
    special: int = field(init=False)
    speed: int = field(init=False)

    def __post_init__(self):
        """Calculate initial stats based on level and base stats."""
        # Copy moves from species if not already set
        if not self.moves:
            import copy
            self.moves = [copy.deepcopy(move) for move in self.species.moves]
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

    def get_learnable_move(self) -> Optional[Move]:
        """
        Check if creature can learn a new move at current level.

        Returns:
            Move object if a move can be learned, None otherwise
        """
        if not self.species.learnset:
            return None

        if self.level in self.species.learnset:
            return self.species.learnset[self.level]

        return None

    def learn_move(self, move: Move, replace_index: Optional[int] = None) -> bool:
        """
        Learn a new move. If creature already has 4 moves, must specify which to replace.

        Args:
            move: The move to learn
            replace_index: Index (0-3) of move to replace, or None to add to empty slot

        Returns:
            True if move was learned successfully, False otherwise
        """
        import copy

        # If creature has fewer than 4 moves, just add it
        if len(self.moves) < 4:
            self.moves.append(copy.deepcopy(move))
            return True

        # If creature already has 4 moves, need to replace one
        if replace_index is not None and 0 <= replace_index < len(self.moves):
            self.moves[replace_index] = copy.deepcopy(move)
            return True

        return False

    def can_learn_tm(self, tm_move_name: str) -> bool:
        """
        Check if creature can learn a TM move.

        Args:
            tm_move_name: Name of the TM move

        Returns:
            True if compatible, False otherwise
        """
        if not self.species.tm_compatible:
            return False

        return tm_move_name in self.species.tm_compatible

    def restore_pp(self, amount: int = None):
        """Restore PP for all moves. If amount is None, fully restores all PP."""
        for move in self.moves:
            if amount is None:
                move.pp = move.max_pp
            else:
                move.pp = min(move.pp + amount, move.max_pp)

    def has_usable_moves(self) -> bool:
        """Check if creature has any moves with PP remaining."""
        return any(move.pp > 0 for move in self.moves)

    def apply_status(self, status: StatusEffect, turns: int = 0):
        """Apply a status effect to the creature."""
        if self.status == StatusEffect.NONE:
            self.status = status
            self.status_turns = turns

    def cure_status(self):
        """Cure the creature's status effect."""
        self.status = StatusEffect.NONE
        self.status_turns = 0

    def has_status(self) -> bool:
        """Check if creature has a status effect."""
        return self.status != StatusEffect.NONE

    def process_status_damage(self) -> int:
        """
        Process end-of-turn status damage.

        Returns:
            Damage dealt by status effect
        """
        damage = 0
        if self.status == StatusEffect.BURN:
            damage = max(1, self.max_hp // 16)  # 1/16 of max HP
            self.take_damage(damage)
        elif self.status == StatusEffect.POISON:
            damage = max(1, self.max_hp // 8)   # 1/8 of max HP
            self.take_damage(damage)
        return damage

    def can_move(self) -> tuple[bool, str]:
        """
        Check if creature can move this turn based on status.

        Returns:
            (can_move, message) tuple
        """
        if self.status == StatusEffect.SLEEP:
            self.status_turns += 1
            if self.status_turns >= 3:  # Wake up after 2-3 turns
                self.cure_status()
                return True, f"{self.get_display_name()} woke up!"
            return False, f"{self.get_display_name()} is asleep!"

        elif self.status == StatusEffect.PARALYSIS:
            import random
            if random.random() < 0.25:  # 25% chance to be fully paralyzed
                return False, f"{self.get_display_name()} is paralyzed and can't move!"

        elif self.status == StatusEffect.FROZEN:
            import random
            if random.random() < 0.20:  # 20% chance to thaw
                self.cure_status()
                return True, f"{self.get_display_name()} thawed out!"
            return False, f"{self.get_display_name()} is frozen solid!"

        return True, ""

    def to_dict(self) -> dict:
        """Convert creature to dictionary for serialization."""
        return {
            'species_id': self.species.id,
            'level': self.level,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'exp': self.exp,
            'nickname': self.nickname,
            'moves': [m.to_dict() for m in self.moves],
            'status': self.status.value,
            'status_turns': self.status_turns
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

        # Restore moves with their PP if saved
        if 'moves' in data:
            creature.moves = [Move.from_dict(m) for m in data['moves']]

        # Restore status effect
        if 'status' in data:
            creature.status = StatusEffect(data['status'])
            creature.status_turns = data.get('status_turns', 0)

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
        """Fully heal all creatures in the team and restore their PP."""
        for creature in self.creatures:
            creature.heal()
            creature.restore_pp()

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
