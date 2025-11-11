"""
Procedural creature generation system.
Generates 151 unique creatures with stats, moves, types, and names.
"""

import random
from typing import List, Dict, Tuple
from ..core.creature import CreatureSpecies, CreatureStats, Move, Ability
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
            if i >= 146:  # Last 6 are legendary (IDs 146-151)
                creature = self._generate_creature(
                    creature_id=i,
                    power_level="legendary",
                    stage=1
                )
                creature.is_legendary = True  # Mark as legendary
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

        # Generate learnset (moves that can be learned via level-up)
        learnset = self._generate_learnset(types, power_level)

        # Generate TM compatibility
        tm_compatible = self._generate_tm_compatibility(types)

        # Generate ability
        ability = self._generate_ability(types, power_level, base_stats)

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
            sprite_data=None,  # Will be generated separately
            learnset=learnset,
            tm_compatible=tm_compatible,
            ability=ability
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

        # Determine critical hit rate
        # Some moves have high crit rate (roughly 10-15% of moves)
        crit_rate = 0
        if "Slash" in name or "Claw" in name or "Strike" in name or "Razor" in name:
            crit_rate = 1  # High crit rate moves
            if "Critical" not in description and status_effect is None:
                description = f"A {move_type}-type attack with a high critical hit ratio."

        # Determine if multi-hit move (roughly 5% of moves)
        multi_hit = (1, 1)
        if self.rng.random() < 0.05 and power < 60:  # Multi-hit moves are weaker per hit
            multi_hit = (2, 5)
            power = max(15, power // 2)  # Reduce power per hit
            if status_effect is None:
                description = f"A {move_type}-type attack that hits 2-5 times."

        # Determine if recoil move (roughly 5% of moves, high power)
        recoil_percent = 0
        if self.rng.random() < 0.05 and power > 60 and multi_hit == (1, 1):
            recoil_percent = 25  # 25% recoil damage
            power = min(120, int(power * 1.2))  # Boost power by 20%
            if status_effect is None:
                description = f"A powerful {move_type}-type attack with recoil damage."

        # Determine priority (roughly 8% of moves)
        priority = 0
        if self.rng.random() < 0.08 and power < 70:
            # Priority moves are typically weaker
            if self.rng.random() < 0.7:
                priority = 1  # Standard priority (Quick Attack style)
                power = max(30, int(power * 0.8))  # Reduce power by 20%
                if status_effect is None and multi_hit == (1, 1) and recoil_percent == 0:
                    description = f"A quick {move_type}-type attack that strikes first."
            else:
                priority = 2  # High priority (Extreme Speed style)
                power = max(40, int(power * 0.7))  # Reduce power by 30%
                if status_effect is None and multi_hit == (1, 1) and recoil_percent == 0:
                    description = f"An extremely fast {move_type}-type attack that always strikes first."

        # Determine if stat-changing move (roughly 10% of moves)
        stat_changes = None
        stat_change_target = "self"
        stat_change_chance = 100

        if self.rng.random() < 0.10:
            # Determine if offensive stat boost or defensive stat drop
            move_style = self.rng.choice(["offensive_boost", "defensive_boost", "debuff", "mixed"])

            if move_style == "offensive_boost":
                # Boost own attack or special
                stat = self.rng.choice(["attack", "special"])
                stages = self.rng.choice([1, 2])  # +1 or +2 stages
                stat_changes = {stat: stages}
                power = 0  # Pure stat-boosting moves don't deal damage
                description = f"Sharply raises the user's {stat.capitalize()}!" if stages == 2 else f"Raises the user's {stat.capitalize()}."

            elif move_style == "defensive_boost":
                # Boost own defense or speed
                stat = self.rng.choice(["defense", "speed"])
                stages = self.rng.choice([1, 2])
                stat_changes = {stat: stages}
                power = 0
                description = f"Sharply raises the user's {stat.capitalize()}!" if stages == 2 else f"Raises the user's {stat.capitalize()}."

            elif move_style == "debuff":
                # Lower opponent's stats
                stat = self.rng.choice(["attack", "defense", "speed", "special"])
                stages = self.rng.choice([-1, -2])  # -1 or -2 stages
                stat_changes = {stat: stages}
                stat_change_target = "opponent"
                power = 0
                description = f"Harshly lowers the foe's {stat.capitalize()}!" if stages == -2 else f"Lowers the foe's {stat.capitalize()}."

            elif move_style == "mixed":
                # Stat change + damage (weaker effect or chance-based)
                if self.rng.random() < 0.5:
                    # Self-boost with damage (like Ancient Power)
                    stat_changes = {self.rng.choice(["attack", "defense", "speed"]): 1}
                    stat_change_chance = 10  # Low chance
                    description = f"A {move_type}-type attack that may raise the user's stats."
                else:
                    # Opponent debuff with damage (like Icy Wind)
                    stat = self.rng.choice(["attack", "speed"])
                    stat_changes = {stat: -1}
                    stat_change_target = "opponent"
                    stat_change_chance = 100  # Always applies
                    power = max(30, power // 2)  # Reduced damage
                    description = f"A {move_type}-type attack that lowers the foe's {stat.capitalize()}."

        return Move(
            name=name,
            type=move_type,
            power=power,
            accuracy=accuracy,
            pp=max_pp,
            max_pp=max_pp,
            description=description,
            status_effect=status_effect,
            status_chance=status_chance,
            crit_rate=crit_rate,
            multi_hit=multi_hit,
            recoil_percent=recoil_percent,
            priority=priority,
            stat_changes=stat_changes,
            stat_change_target=stat_change_target,
            stat_change_chance=stat_change_chance
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

    def _generate_learnset(self, types: List[str], power_level: str) -> Dict[int, Move]:
        """
        Generate a learnset of moves that can be learned via level-up.

        Args:
            types: Creature's type(s)
            power_level: Creature's power level

        Returns:
            Dictionary mapping level -> Move
        """
        learnset = {}

        # Determine level range based on power level
        level_ranges = {
            "basic": [(7, 12), (13, 18), (21, 26), (30, 35)],
            "starter": [(7, 12), (15, 20), (25, 30), (35, 40)],
            "intermediate": [(10, 15), (20, 25), (30, 35), (40, 45)],
            "advanced": [(12, 18), (25, 32), (38, 45), (50, 55)],
            "legendary": [(15, 20), (30, 35), (45, 50), (60, 65)]
        }

        ranges = level_ranges.get(power_level, [(10, 15), (20, 25), (30, 35), (40, 45)])

        # Generate 4-6 learnable moves
        num_learnable = self.rng.randint(4, 6)

        for i in range(num_learnable):
            # Pick a level from the appropriate range
            level_range = ranges[min(i, len(ranges) - 1)]
            learn_level = self.rng.randint(*level_range)

            # Skip if this level already has a move
            if learn_level in learnset:
                learn_level += self.rng.randint(1, 3)

            # Generate move (favor creature's types, but allow some variety)
            if self.rng.random() < 0.7:
                move_type = self.rng.choice(types)
            else:
                move_type = self.rng.choice(TYPES)

            # Power level of move scales with learn level
            if learn_level < 15:
                move_power = "basic"
            elif learn_level < 30:
                move_power = "intermediate"
            else:
                move_power = "advanced"

            move = self._generate_move(move_type, move_power)
            learnset[learn_level] = move

        return learnset

    def _generate_tm_compatibility(self, types: List[str]) -> List[str]:
        """
        Generate list of TM move names this creature can learn.

        Args:
            types: Creature's type(s)

        Returns:
            List of TM move names
        """
        # Define some common TM moves
        # These will be created as actual TM items later
        tm_moves = {
            # Universal/common TMs (most creatures can learn)
            "common": ["Swift Strike", "Mega Impact", "Fury Slash"],
            # Type-specific TMs
            "Flame": ["Flame Burst", "Inferno Blast", "Sacred Flame"],
            "Aqua": ["Hydro Blast", "Aqua Storm", "Tidal Wave"],
            "Leaf": ["Vine Storm", "Petal Burst", "Solar Beam"],
            "Volt": ["Thunder Blast", "Volt Storm", "Electric Surge"],
            "Frost": ["Frost Beam", "Ice Storm", "Frozen Fury"],
            "Terra": ["Earth Blast", "Quake Storm", "Boulder Crush"],
            "Gale": ["Aero Blast", "Sky Storm", "Whirlwind"],
            "Toxin": ["Toxic Blast", "Poison Storm", "Venom Strike"],
            "Mind": ["Psychic Blast", "Mind Storm", "Confusion Wave"],
            "Spirit": ["Spirit Blast", "Ghost Storm", "Shadow Strike"],
            "Beast": ["Wild Slash", "Feral Strike", "Primal Fury"],
            "Brawl": ["Power Punch", "Combat Strike", "Fighting Fury"],
            "Insect": ["Bug Blast", "Swarm Storm", "Insect Fury"],
            "Metal": ["Steel Slash", "Metal Storm", "Iron Impact"],
            "Mystic": ["Mystic Blast", "Fairy Storm", "Magic Strike"],
            "Shadow": ["Dark Blast", "Shadow Storm", "Void Strike"]
        }

        compatible = []

        # All creatures can learn common TMs
        compatible.extend(tm_moves["common"])

        # Add type-specific TMs
        for creature_type in types:
            if creature_type in tm_moves:
                compatible.extend(tm_moves[creature_type])

        # Add a few random TMs from other types (30% chance each)
        for tm_type, moves in tm_moves.items():
            if tm_type != "common" and tm_type not in types:
                for move_name in moves:
                    if self.rng.random() < 0.3:
                        compatible.append(move_name)

        return list(set(compatible))  # Remove duplicates

    def _generate_ability(self, types: List[str], power_level: str, stats: CreatureStats) -> Ability:
        """Generate a passive ability for the creature based on its types and stats."""

        # Type-based abilities (50% of creatures get type-based abilities)
        type_abilities = {
            "Flame": [
                ("Blaze", "Boosts Flame-type moves when HP is low", "type_boost_low_hp"),
                ("Flash Fire", "Powers up Flame moves when hit by fire", "absorb_type"),
                ("Drought", "Changes weather to sunny when sent out", "weather_sun"),
            ],
            "Aqua": [
                ("Torrent", "Boosts Aqua-type moves when HP is low", "type_boost_low_hp"),
                ("Swift Swim", "Boosts Speed in rain", "speed_rain"),
                ("Drizzle", "Changes weather to rain when sent out", "weather_rain"),
            ],
            "Leaf": [
                ("Overgrow", "Boosts Leaf-type moves when HP is low", "type_boost_low_hp"),
                ("Chlorophyll", "Boosts Speed in sunny weather", "speed_sun"),
                ("Leaf Guard", "Prevents status conditions in sunny weather", "status_immune_sun"),
            ],
            "Volt": [
                ("Static", "May paralyze on contact", "paralyze_contact"),
                ("Volt Absorb", "Restores HP when hit by Volt moves", "absorb_type"),
                ("Lightning Rod", "Draws Volt moves to itself", "draw_type"),
            ],
            "Frost": [
                ("Snow Cloak", "Boosts Evasion in hail", "evasion_hail"),
                ("Ice Body", "Restores HP in hail", "heal_hail"),
                ("Slush Rush", "Boosts Speed in hail", "speed_hail"),
            ],
            "Terra": [
                ("Sand Veil", "Boosts Evasion in sandstorm", "evasion_sandstorm"),
                ("Sand Rush", "Boosts Speed in sandstorm", "speed_sandstorm"),
                ("Sand Stream", "Changes weather to sandstorm", "weather_sandstorm"),
            ],
            "Metal": [
                ("Sturdy", "Cannot be knocked out with one hit", "survive_ohko"),
                ("Heavy Metal", "Doubles creature weight", "stat_weight"),
                ("Light Metal", "Halves creature weight", "stat_weight"),
            ],
            "Toxin": [
                ("Poison Point", "May poison on contact", "poison_contact"),
                ("Poison Touch", "May poison targets on contact", "poison_contact"),
                ("Immunity", "Cannot be poisoned", "status_immune_poison"),
            ],
            "Shadow": [
                ("Cursed Body", "May disable moves on contact", "disable_contact"),
                ("Shadow Tag", "Prevents fleeing", "prevent_flee"),
                ("Infiltrator", "Ignores barriers and substitutes", "ignore_barriers"),
            ],
            "Mind": [
                ("Synchronize", "Passes status problems to the foe", "reflect_status"),
                ("Inner Focus", "Protects from flinching", "no_flinch"),
                ("Telepathy", "Anticipates ally moves", "anticipate"),
            ],
        }

        # Stat-based abilities (choose based on highest stat)
        stat_abilities = []

        # High HP abilities
        if stats.hp >= 80:
            stat_abilities.extend([
                ("Thick Fat", "Reduces damage from Flame and Frost moves", "resist_flame_frost"),
                ("Filter", "Reduces super effective damage", "reduce_super"),
            ])

        # High Attack abilities
        if stats.attack >= 80:
            stat_abilities.extend([
                ("Huge Power", "Doubles Attack stat", "double_attack"),
                ("Guts", "Boosts Attack when statused", "attack_boost_status"),
                ("Sheer Force", "Removes added effects to boost power", "power_no_effects"),
                ("Super Luck", "Heightens critical hit ratio", "boost_crit"),
                ("Sniper", "Boosts critical hit power", "crit_power_boost"),
                ("Skill Link", "Multi-hit moves always hit maximum times", "multi_hit_max"),
                ("Rock Head", "Protects from recoil damage", "no_recoil"),
                ("Simple", "Doubles stat stage changes", "double_stat_changes"),
            ])

        # High Defense abilities
        if stats.defense >= 80:
            stat_abilities.extend([
                ("Iron Barbs", "Inflicts damage on contact", "damage_contact"),
                ("Solid Rock", "Reduces super effective damage", "reduce_super"),
                ("Battle Armor", "Blocks critical hits", "no_crits"),
                ("Shell Armor", "Blocks critical hits", "no_crits"),
            ])

        # High Speed abilities
        if stats.speed >= 80:
            stat_abilities.extend([
                ("Speed Boost", "Gradually boosts Speed", "speed_gradual"),
                ("Quick Feet", "Boosts Speed when statused", "speed_boost_status"),
                ("Unburden", "Boosts Speed when item is used", "speed_after_item"),
            ])

        # High Special abilities
        if stats.special >= 80:
            stat_abilities.extend([
                ("Magic Guard", "Only damaged by attacks", "no_indirect_damage"),
                ("Adaptability", "Boosts STAB effectiveness", "boost_stab"),
                ("Rivalry", "Boosts against same type", "boost_same_type"),
                ("Contrary", "Inverts stat stage changes", "invert_stat_changes"),
            ])

        # Universal abilities (any creature can have these)
        universal_abilities = [
            ("Keen Eye", "Prevents accuracy reduction", "no_accuracy_loss"),
            ("Intimidate", "Lowers opposing Attack on switch-in", "lower_attack_entry"),
            ("Pressure", "Makes foe use more PP", "increase_pp_use"),
            ("Trace", "Copies foe's ability", "copy_ability"),
            ("Natural Cure", "Heals status on switching out", "heal_status_switch"),
            ("Shed Skin", "May heal status each turn", "heal_status_chance"),
            ("Regenerator", "Restores HP when switching out", "heal_switch"),
            ("Moxie", "Boosts Attack after knocking out opponent", "attack_ko_boost"),
            ("Unaware", "Ignores opponent's stat stages", "ignore_stat_stages"),
        ]

        # Choose ability based on type and stats
        ability_pool = []

        # Add type-specific abilities for creature's types
        for creature_type in types:
            if creature_type in type_abilities:
                ability_pool.extend(type_abilities[creature_type])

        # Add stat-based abilities
        ability_pool.extend(stat_abilities)

        # Always include some universal abilities
        ability_pool.extend(universal_abilities)

        # Remove duplicates
        ability_pool = list(set(ability_pool))

        # Choose one ability
        if ability_pool:
            name, description, effect_type = self.rng.choice(ability_pool)
        else:
            # Fallback to a universal ability
            name, description, effect_type = self.rng.choice(universal_abilities)

        return Ability(name=name, description=description, effect_type=effect_type)

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
