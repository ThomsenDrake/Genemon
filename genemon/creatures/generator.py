"""
Procedural creature generation system.
Generates 151 unique creatures with stats, moves, types, and names.
"""

import random
from typing import List, Dict, Tuple
from ..core.creature import CreatureSpecies, CreatureStats, Move
from .types import TYPES


# Name generation components
PREFIXES = [
    "Bur", "Flar", "Spar", "Glim", "Zap", "Bolt", "Aquo", "Frost",
    "Thorn", "Vine", "Petal", "Bloom", "Terra", "Rock", "Grav",
    "Aero", "Gale", "Zeph", "Venom", "Toxic", "Psy", "Myst",
    "Shade", "Umbra", "Lux", "Bright", "Mag", "Ferro", "Crystal",
    "Ember", "Blaze", "Infern", "Hydro", "Aqua", "Splash",
    "Volt", "Thunder", "Spark", "Ice", "Cryo", "Glaci",
    "Stone", "Boulder", "Quake", "Sky", "Cloud", "Storm",
    "Morph", "Proto", "Nova", "Stellar", "Cosmo", "Void"
]

MIDDLES = [
    "ra", "lo", "ni", "ma", "ko", "ri", "tu", "ve",
    "do", "fi", "gu", "ho", "ji", "ka", "lu", "mo",
    "na", "po", "qu", "ru", "si", "ta", "wu", "xi",
    "ya", "zu", "la", "ba", "ce", "de", "eo", "fa"
]

SUFFIXES = [
    "x", "on", "us", "is", "os", "ax", "ex", "ix",
    "ant", "ent", "ion", "tor", "dor", "kor", "mor",
    "ra", "ro", "ri", "ta", "to", "ti", "la", "lo",
    "wing", "claw", "fang", "tail", "shell", "scale",
    "fin", "horn", "spike", "blade"
]

# Creature archetypes for conceptual generation
ARCHETYPES = [
    "bird", "fish", "quadruped", "biped", "serpent",
    "insect", "amphibian", "reptile", "mammal", "dragon",
    "elemental", "humanoid", "plant", "mineral", "hybrid"
]

# Move name components
MOVE_PREFIXES = [
    "Swift", "Power", "Mega", "Hyper", "Super", "Ultra",
    "Quick", "Rapid", "Fury", "Raging", "Mighty", "Grand",
    "Sacred", "Dark", "Light", "Shadow", "Flame", "Frost",
    "Thunder", "Aqua", "Gale", "Terra", "Toxic", "Mind",
    "Spirit", "Metal", "Mystic", "Void", "Cosmic", "Ancient"
]

MOVE_SUFFIXES = [
    "Strike", "Blast", "Beam", "Wave", "Pulse", "Storm",
    "Burst", "Barrage", "Slash", "Crush", "Impact", "Force",
    "Ray", "Bolt", "Shock", "Fang", "Claw", "Wing",
    "Tail", "Horn", "Edge", "Fury", "Rage", "Wrath"
]


class CreatureGenerator:
    """Generates a complete set of 151 unique creatures for a save file."""

    def __init__(self, seed: int = None):
        """
        Initialize generator with optional seed for reproducibility.

        Args:
            seed: Random seed for generation. If None, uses random seed.
        """
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.generated_names = set()
        self.generated_species = []

    def generate_all_creatures(self) -> List[CreatureSpecies]:
        """
        Generate all 151 creatures for a save file.

        Returns:
            List of CreatureSpecies in order (1-151)
        """
        self.generated_names.clear()
        self.generated_species.clear()

        # Generate starters (3)
        starters = self._generate_starter_trio()
        self.generated_species.extend(starters)

        # Generate early-game creatures (IDs 4-20)
        for i in range(4, 21):
            creature = self._generate_creature(
                creature_id=i,
                power_level="basic",
                stage=1
            )
            self.generated_species.append(creature)

        # Generate mid-game creatures (IDs 21-100)
        for i in range(21, 101):
            stage = 1 if i % 3 == 1 else 2  # Mix of base and evolved forms
            power = "intermediate" if i < 60 else "advanced"
            creature = self._generate_creature(
                creature_id=i,
                power_level=power,
                stage=stage
            )
            self.generated_species.append(creature)

        # Generate late-game and legendary creatures (IDs 101-151)
        for i in range(101, 152):
            if i >= 146:  # Last 5 are legendary
                creature = self._generate_creature(
                    creature_id=i,
                    power_level="legendary",
                    stage=1
                )
            else:
                stage = self.rng.choice([1, 2, 3])
                creature = self._generate_creature(
                    creature_id=i,
                    power_level="advanced",
                    stage=stage
                )
            self.generated_species.append(creature)

        # Set up some evolution chains
        self._create_evolution_chains()

        return self.generated_species

    def _generate_starter_trio(self) -> List[CreatureSpecies]:
        """Generate the three starter creatures."""
        starters = []
        starter_types = [
            ["Flame"],  # Fire starter
            ["Aqua"],   # Water starter
            ["Leaf"]    # Grass starter
        ]

        for i, types in enumerate(starter_types, start=1):
            creature = self._generate_creature(
                creature_id=i,
                power_level="starter",
                stage=1,
                types=types
            )
            starters.append(creature)

        return starters

    def _generate_creature(
        self,
        creature_id: int,
        power_level: str,
        stage: int,
        types: List[str] = None
    ) -> CreatureSpecies:
        """Generate a single creature."""

        # Generate name
        name = self._generate_name()

        # Determine types
        if types is None:
            types = self._select_types()

        # Generate stats based on power level and stage
        base_stats = self._generate_stats(power_level, stage)

        # Generate moves
        moves = self._generate_moves(types, power_level)

        # Generate flavor text
        flavor_text = self._generate_flavor_text(name, types)

        # Create species
        species = CreatureSpecies(
            id=creature_id,
            name=name,
            types=types,
            base_stats=base_stats,
            moves=moves,
            flavor_text=flavor_text,
            evolution_level=None,  # Set later in evolution chain creation
            evolves_into=None,
            sprite_data=None  # Will be generated separately
        )

        return species

    def _generate_name(self) -> str:
        """Generate a unique, pronounceable creature name."""
        max_attempts = 100
        for _ in range(max_attempts):
            # Choose length (2-3 syllables)
            syllables = self.rng.randint(2, 3)

            if syllables == 2:
                name = (self.rng.choice(PREFIXES) +
                       self.rng.choice(SUFFIXES))
            else:
                name = (self.rng.choice(PREFIXES) +
                       self.rng.choice(MIDDLES) +
                       self.rng.choice(SUFFIXES))

            # Capitalize properly
            name = name.capitalize()

            # Ensure uniqueness
            if name not in self.generated_names:
                self.generated_names.add(name)
                return name

        # Fallback: add number
        base_name = self.rng.choice(PREFIXES).capitalize()
        counter = 1
        while f"{base_name}{counter}" in self.generated_names:
            counter += 1
        name = f"{base_name}{counter}"
        self.generated_names.add(name)
        return name

    def _select_types(self) -> List[str]:
        """Select 1 or 2 types for a creature."""
        # 60% chance of single type, 40% chance of dual type
        if self.rng.random() < 0.6:
            return [self.rng.choice(TYPES)]
        else:
            type1 = self.rng.choice(TYPES)
            type2 = self.rng.choice([t for t in TYPES if t != type1])
            return [type1, type2]

    def _generate_stats(self, power_level: str, stage: int) -> CreatureStats:
        """Generate base stats based on power level and evolution stage."""

        # Base stat ranges by power level
        ranges = {
            "basic": (30, 50),
            "starter": (40, 60),
            "intermediate": (50, 75),
            "advanced": (65, 95),
            "legendary": (90, 120)
        }

        base_min, base_max = ranges.get(power_level, (40, 60))

        # Evolution stage multiplier
        stage_multiplier = 1.0 + (stage - 1) * 0.3

        def gen_stat():
            base = self.rng.randint(base_min, base_max)
            return int(base * stage_multiplier)

        # Generate stats with some variation
        hp = gen_stat() + self.rng.randint(-5, 15)  # HP tends to be higher
        attack = gen_stat()
        defense = gen_stat()
        special = gen_stat()
        speed = gen_stat()

        # Ensure minimum values
        hp = max(20, hp)
        attack = max(15, attack)
        defense = max(15, defense)
        special = max(15, special)
        speed = max(15, speed)

        return CreatureStats(
            hp=hp,
            attack=attack,
            defense=defense,
            special=special,
            speed=speed
        )

    def _generate_moves(self, types: List[str], power_level: str) -> List[Move]:
        """Generate 4-6 moves for a creature."""
        num_moves = self.rng.randint(4, 6)
        moves = []

        # At least 2 moves should match creature's type
        type_moves = min(num_moves - 1, 3)

        for i in range(type_moves):
            move_type = self.rng.choice(types)
            move = self._generate_move(move_type, power_level)
            moves.append(move)

        # Rest can be random or Beast type
        for i in range(num_moves - type_moves):
            move_type = self.rng.choice(TYPES + ["Beast"] * 3)  # Favor Beast
            move = self._generate_move(move_type, power_level)
            moves.append(move)

        return moves

    def _generate_move(self, move_type: str, power_level: str) -> Move:
        """Generate a single move."""
        from ..core.creature import StatusEffect

        # Generate name
        prefix = self.rng.choice(MOVE_PREFIXES)
        suffix = self.rng.choice(MOVE_SUFFIXES)
        name = f"{prefix} {suffix}"

        # Power ranges
        power_ranges = {
            "basic": (20, 50),
            "starter": (30, 60),
            "intermediate": (40, 80),
            "advanced": (50, 100),
            "legendary": (70, 120)
        }

        min_power, max_power = power_ranges.get(power_level, (30, 60))
        power = self.rng.randint(min_power, max_power)

        # Accuracy (higher power = lower accuracy generally)
        if power > 80:
            accuracy = self.rng.randint(70, 90)
        else:
            accuracy = self.rng.randint(85, 100)

        # PP based on power
        if power > 70:
            max_pp = self.rng.randint(5, 10)
        else:
            max_pp = self.rng.randint(10, 25)

        description = f"A {move_type}-type attack."

        # 30% chance to have a status effect (type-appropriate)
        status_effect = None
        status_chance = 0

        if self.rng.random() < 0.30:
            # Map types to appropriate status effects
            type_to_status = {
                "Flame": StatusEffect.BURN,
                "Frost": StatusEffect.FROZEN,
                "Volt": StatusEffect.PARALYSIS,
                "Toxin": StatusEffect.POISON,
                "Mind": StatusEffect.SLEEP,
                "Spirit": StatusEffect.SLEEP,
                "Shadow": StatusEffect.POISON,
            }

            status_effect = type_to_status.get(move_type)
            if status_effect:
                # Lower power moves have higher status chance
                if power < 40:
                    status_chance = self.rng.randint(20, 40)
                elif power < 70:
                    status_chance = self.rng.randint(10, 25)
                else:
                    status_chance = self.rng.randint(5, 15)

                # Update description
                status_name = status_effect.value.capitalize()
                description = f"A {move_type}-type attack that may inflict {status_name}."

        return Move(
            name=name,
            type=move_type,
            power=power,
            accuracy=accuracy,
            pp=max_pp,
            max_pp=max_pp,
            description=description,
            status_effect=status_effect,
            status_chance=status_chance
        )

    def _generate_flavor_text(self, name: str, types: List[str]) -> str:
        """Generate flavor text for a creature."""
        templates = [
            f"A {types[0]}-type creature known for its fierce nature.",
            f"This {name} is rarely seen in the wild.",
            f"Legends say {name} can control the elements.",
            f"A mysterious creature with {types[0]} powers.",
            f"Found in remote areas, {name} is highly territorial.",
            f"Its {types[0]} abilities make it a formidable opponent.",
            f"Ancient texts describe {name} as a guardian spirit.",
            f"This creature has adapted to harsh environments.",
            f"Known for its incredible speed and agility.",
            f"A rare specimen with unique {types[0]} characteristics."
        ]

        return self.rng.choice(templates)

    def _create_evolution_chains(self):
        """Set up evolution relationships between creatures."""
        # Create some 2-stage and 3-stage evolution chains

        # Starters evolve at level 16 and 32
        for i in range(3):
            if i * 3 + 1 < len(self.generated_species):
                base_id = i * 3 + 1
                # First evolution
                if base_id < len(self.generated_species):
                    self.generated_species[base_id - 1].evolution_level = 16
                    self.generated_species[base_id - 1].evolves_into = base_id + 1

        # Create some random evolution chains for early creatures
        chain_starts = [4, 7, 10, 13, 16, 19, 22, 25, 28]
        for start_id in chain_starts:
            if start_id < len(self.generated_species) - 1:
                # Two-stage evolution
                self.generated_species[start_id - 1].evolution_level = self.rng.randint(14, 20)
                self.generated_species[start_id - 1].evolves_into = start_id + 1

                # Some have three stages
                if self.rng.random() < 0.3 and start_id < len(self.generated_species) - 2:
                    self.generated_species[start_id].evolution_level = self.rng.randint(28, 36)
                    self.generated_species[start_id].evolves_into = start_id + 2

    def get_species_dict(self) -> Dict[int, CreatureSpecies]:
        """Get dictionary of species indexed by ID."""
        return {species.id: species for species in self.generated_species}
