"""
NPC (Non-Player Character) system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from ..core.creature import Team


@dataclass
class Dialogue:
    """A piece of dialogue with optional conditions."""
    text: str
    condition: Optional[str] = None  # e.g., "has_badge_1", "before_battle"


@dataclass
class NPC:
    """A non-player character."""

    id: str
    name: str
    location_id: str
    x: int
    y: int
    sprite: str = "@"  # ASCII character for now

    dialogues: List[Dialogue] = field(default_factory=list)
    is_trainer: bool = False
    trainer_team: Optional[Team] = None
    has_been_defeated: bool = False
    is_shopkeeper: bool = False
    shop_inventory: List[str] = field(default_factory=list)  # List of item IDs sold
    is_healer: bool = False
    specialty_type: Optional[str] = None  # For gym leaders with type specialization
    is_gym_leader: bool = False  # Flag for gym leader status
    badge_id: Optional[str] = None  # Badge ID awarded by this gym leader
    badge_name: Optional[str] = None  # Name of the badge
    badge_description: Optional[str] = None  # Description of the badge

    def get_dialogue(self, game_state: Dict = None) -> str:
        """
        Get appropriate dialogue based on game state.

        Args:
            game_state: Dictionary with game state flags

        Returns:
            Dialogue text to display
        """
        if not self.dialogues:
            return f"{self.name}: Hello!"

        # If trainer and already defeated
        if self.is_trainer and self.has_been_defeated:
            return f"{self.name}: You were too strong for me!"

        # Find first matching dialogue
        for dialogue in self.dialogues:
            if dialogue.condition is None:
                return f"{self.name}: {dialogue.text}"
            elif game_state and game_state.get(dialogue.condition, False):
                return f"{self.name}: {dialogue.text}"

        # Default to first dialogue
        return f"{self.name}: {self.dialogues[0].text}"

    def to_dict(self) -> dict:
        """Serialize NPC to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'location_id': self.location_id,
            'x': self.x,
            'y': self.y,
            'sprite': self.sprite,
            'is_trainer': self.is_trainer,
            'has_been_defeated': self.has_been_defeated
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NPC':
        """Deserialize NPC from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            location_id=data['location_id'],
            x=data['x'],
            y=data['y'],
            sprite=data.get('sprite', '@'),
            is_trainer=data.get('is_trainer', False),
            has_been_defeated=data.get('has_been_defeated', False)
        )


class NPCRegistry:
    """Registry of all NPCs in the game."""

    def __init__(self, use_json: bool = True):
        """
        Initialize NPC registry.

        Args:
            use_json: If True, load NPCs from JSON file. If False, use legacy hardcoded NPCs.
        """
        self.npcs: Dict[str, NPC] = {}
        self.use_json = use_json

        if use_json:
            self._load_npcs_from_json()
        else:
            self._create_npcs()

    def _load_npcs_from_json(self):
        """Load all NPCs from JSON data file."""
        from ..data.npc_loader import NPCLoader

        loader = NPCLoader()
        self.npcs = loader.load_all_npcs()

    def _create_npcs(self):
        """Create all authored NPCs (legacy hardcoded method)."""

        # Professor in starter town
        professor = NPC(
            id="prof_oak",
            name="Prof. Cypress",
            location_id="town_starter",
            x=5,
            y=5,
            sprite="P",
            dialogues=[
                Dialogue("Welcome to the world of Genemon!"),
                Dialogue("Each creature is unique to your journey!")
            ]
        )
        self.npcs[professor.id] = professor

        # Rival in starter town
        rival = NPC(
            id="rival_starter",
            name="Blake",
            location_id="town_starter",
            x=10,
            y=10,
            sprite="R",
            is_trainer=True,
            dialogues=[
                Dialogue("Hey! I'm going to be the best trainer!"),
                Dialogue("Let's battle!", "before_battle")
            ]
        )
        self.npcs[rival.id] = rival

        # Shopkeeper in second town
        shopkeeper = NPC(
            id="shop_oakwood",
            name="Merchant Mae",
            location_id="town_second",
            x=15,
            y=5,
            sprite="S",
            is_shopkeeper=True,
            shop_inventory=[
                'potion',
                'super_potion',
                'hyper_potion',
                'max_potion',
                'revive',
                'max_revive',
                'ether',
                'antidote',
                'awakening',
                'burn_heal',
                'paralyze_heal',
                'capture_ball',
                'great_ball',
                'ultra_ball'
            ],
            dialogues=[
                Dialogue("Welcome to my shop!"),
                Dialogue("I sell potions, revival items, and capture balls!")
            ]
        )
        self.npcs[shopkeeper.id] = shopkeeper

        # Gym Leader in third town - Flame type specialist
        gym_leader = NPC(
            id="gym_leader_1",
            name="Leader Flint",
            location_id="town_third",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Flame",
            badge_id="badge_flame",
            badge_name="Ember Badge",
            badge_description="Proof of victory over Leader Flint and mastery of Flame-type battles.",
            dialogues=[
                Dialogue("I'm the Flame-type Gym Leader!"),
                Dialogue("Prove your strength in battle!")
            ]
        )
        self.npcs[gym_leader.id] = gym_leader

        # Gym Leader in fourth town - Aqua type specialist
        gym_leader_2 = NPC(
            id="gym_leader_2",
            name="Leader Marina",
            location_id="town_fourth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Aqua",
            badge_id="badge_aqua",
            badge_name="Cascade Badge",
            badge_description="Proof of victory over Leader Marina and mastery of Aqua-type battles.",
            dialogues=[
                Dialogue("Welcome to Aquamarine Harbor!"),
                Dialogue("Face the power of the ocean!")
            ]
        )
        self.npcs[gym_leader_2.id] = gym_leader_2

        # Gym Leader in fifth town - Volt type specialist
        gym_leader_3 = NPC(
            id="gym_leader_3",
            name="Leader Zapper",
            location_id="town_fifth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Volt",
            badge_id="badge_volt",
            badge_name="Thunder Badge",
            badge_description="Proof of victory over Leader Zapper and mastery of Volt-type battles.",
            dialogues=[
                Dialogue("Feel the power of lightning!"),
                Dialogue("Your circuits are overloaded by my electric prowess!")
            ]
        )
        self.npcs[gym_leader_3.id] = gym_leader_3

        # Gym Leader in sixth town - Frost type specialist
        gym_leader_4 = NPC(
            id="gym_leader_4",
            name="Leader Glacia",
            location_id="town_sixth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Frost",
            badge_id="badge_frost",
            badge_name="Glacier Badge",
            badge_description="Proof of victory over Leader Glacia and mastery of Frost-type battles.",
            dialogues=[
                Dialogue("Welcome to Frostfield, where ice reigns supreme!"),
                Dialogue("Your determination melted my defenses!")
            ]
        )
        self.npcs[gym_leader_4.id] = gym_leader_4

        # Gym Leader in seventh town - Shadow type specialist
        gym_leader_5 = NPC(
            id="gym_leader_5",
            name="Leader Umbra",
            location_id="town_seventh",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Shadow",
            badge_id="badge_shadow",
            badge_name="Eclipse Badge",
            badge_description="Proof of victory over Leader Umbra and mastery of Shadow-type battles.",
            dialogues=[
                Dialogue("The shadows are my allies..."),
                Dialogue("You have illuminated the darkness within me!")
            ]
        )
        self.npcs[gym_leader_5.id] = gym_leader_5

        # Nurse Joy in Thunderpeak City
        nurse_thunderpeak = NPC(
            id="nurse_thunderpeak",
            name="Nurse Joy",
            location_id="town_fifth",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Welcome to Thunderpeak! Let me heal your team!")
            ]
        )
        self.npcs[nurse_thunderpeak.id] = nurse_thunderpeak

        # Nurse Joy in Frostfield Village
        nurse_frostfield = NPC(
            id="nurse_frostfield",
            name="Nurse Joy",
            location_id="town_sixth",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("You look cold! Warm up and let me heal your team!")
            ]
        )
        self.npcs[nurse_frostfield.id] = nurse_frostfield

        # Nurse Joy in Shadowmere Town
        nurse_shadowmere = NPC(
            id="nurse_shadowmere",
            name="Nurse Joy",
            location_id="town_seventh",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Even in the shadows, I'll heal your team!")
            ]
        )
        self.npcs[nurse_shadowmere.id] = nurse_shadowmere

        # Trainers on Route 1
        route1_trainer1 = NPC(
            id="trainer_route1_1",
            name="Bug Catcher Tim",
            location_id="route_1",
            x=10,
            y=12,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("Let's battle!"),
                Dialogue("You're strong!")
            ]
        )
        self.npcs[route1_trainer1.id] = route1_trainer1

        route1_trainer2 = NPC(
            id="trainer_route1_2",
            name="Lass Anna",
            location_id="route_1",
            x=10,
            y=18,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("Hi! Want to battle?"),
                Dialogue("Good match!")
            ]
        )
        self.npcs[route1_trainer2.id] = route1_trainer2

        # Trainers on Route 3
        route3_trainer1 = NPC(
            id="trainer_route3_1",
            name="Ace Trainer Jake",
            location_id="route_3",
            x=10,
            y=15,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("I'm an expert trainer!"),
                Dialogue("Impressive skills!")
            ]
        )
        self.npcs[route3_trainer1.id] = route3_trainer1

        route3_trainer2 = NPC(
            id="trainer_route3_2",
            name="Hiker Bob",
            location_id="route_3",
            x=10,
            y=25,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("I love the mountains!"),
                Dialogue("You got me!")
            ]
        )
        self.npcs[route3_trainer2.id] = route3_trainer2

        # Healer in each town
        healer_newbark = NPC(
            id="healer_newbark",
            name="Nurse Joy",
            location_id="town_starter",
            x=14,
            y=5,
            sprite="H",
            is_healer=True,
            dialogues=[
                Dialogue("I can heal your creatures!"),
                Dialogue("Come back anytime!")
            ]
        )
        self.npcs[healer_newbark.id] = healer_newbark

        # Healer in fourth town
        healer_fourth = NPC(
            id="healer_fourth",
            name="Nurse Joy",
            location_id="town_fourth",
            x=5,
            y=5,
            sprite="H",
            is_healer=True,
            dialogues=[
                Dialogue("Welcome to Aquamarine Harbor!"),
                Dialogue("Let me heal your team!")
            ]
        )
        self.npcs[healer_fourth.id] = healer_fourth

        # Gym Leader in eighth town - Terra type specialist
        gym_leader_6 = NPC(
            id="gym_leader_6",
            name="Leader Boulder",
            location_id="town_eighth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Terra",
            badge_id="badge_terra",
            badge_name="Boulder Badge",
            badge_description="Proof of victory over Leader Boulder and mastery of Terra-type battles.",
            dialogues=[
                Dialogue("My rock-solid defense is unbreakable!"),
                Dialogue("Your strength has shattered my resolve!")
            ]
        )
        self.npcs[gym_leader_6.id] = gym_leader_6

        # Gym Leader in ninth town - Mind type specialist
        gym_leader_7 = NPC(
            id="gym_leader_7",
            name="Leader Sage",
            location_id="town_ninth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Mind",
            badge_id="badge_mind",
            badge_name="Wisdom Badge",
            badge_description="Proof of victory over Leader Sage and mastery of Mind-type battles.",
            dialogues=[
                Dialogue("The mind is the ultimate battleground..."),
                Dialogue("Your mental fortitude has exceeded my expectations!")
            ]
        )
        self.npcs[gym_leader_7.id] = gym_leader_7

        # Gym Leader in tenth town - Brawl type specialist
        gym_leader_8 = NPC(
            id="gym_leader_8",
            name="Leader Champion",
            location_id="town_tenth",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            is_gym_leader=True,
            specialty_type="Brawl",
            badge_id="badge_brawl",
            badge_name="Victory Badge",
            badge_description="Proof of victory over Leader Champion and mastery of Brawl-type battles.",
            dialogues=[
                Dialogue("Show me your fighting spirit!"),
                Dialogue("You have the heart of a true champion!")
            ]
        )
        self.npcs[gym_leader_8.id] = gym_leader_8

        # Nurse Joy in Boulder Ridge City
        nurse_boulder = NPC(
            id="nurse_boulder",
            name="Nurse Joy",
            location_id="town_eighth",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Welcome to Boulder Ridge! Rest up for the gym challenge!")
            ]
        )
        self.npcs[nurse_boulder.id] = nurse_boulder

        # Nurse Joy in Mindspire Heights
        nurse_mindspire = NPC(
            id="nurse_mindspire",
            name="Nurse Joy",
            location_id="town_ninth",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Clear your mind and let me heal your team!")
            ]
        )
        self.npcs[nurse_mindspire.id] = nurse_mindspire

        # Nurse Joy in Victory Valley
        nurse_victory = NPC(
            id="nurse_victory",
            name="Nurse Joy",
            location_id="town_tenth",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("You're close to Victory Road! Prepare well!")
            ]
        )
        self.npcs[nurse_victory.id] = nurse_victory

        # Nurse Joy in Champion's Hall
        nurse_elite = NPC(
            id="nurse_elite",
            name="Nurse Joy",
            location_id="elite_hall",
            x=5,
            y=5,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Only the strongest trainers make it here. Let me heal you!")
            ]
        )
        self.npcs[nurse_elite.id] = nurse_elite

        # Elite Four Member 1 - Mystic specialist
        elite_1 = NPC(
            id="elite_1",
            name="Elite Mystica",
            location_id="elite_hall",
            x=8,
            y=10,
            sprite="E",
            is_trainer=True,
            dialogues=[
                Dialogue("I am the first of the Elite Four. Prove your worth!"),
                Dialogue("Impressive... but there are three more ahead!")
            ]
        )
        self.npcs[elite_1.id] = elite_1

        # Elite Four Member 2 - Gale specialist
        elite_2 = NPC(
            id="elite_2",
            name="Elite Tempest",
            location_id="elite_hall",
            x=12,
            y=10,
            sprite="E",
            is_trainer=True,
            dialogues=[
                Dialogue("Feel the fury of the storm!"),
                Dialogue("Your resolve is stronger than any gale!")
            ]
        )
        self.npcs[elite_2.id] = elite_2

        # Elite Four Member 3 - Metal specialist
        elite_3 = NPC(
            id="elite_3",
            name="Elite Steel",
            location_id="elite_hall",
            x=8,
            y=14,
            sprite="E",
            is_trainer=True,
            dialogues=[
                Dialogue("My iron defense cannot be breached!"),
                Dialogue("You've forged an incredible team!")
            ]
        )
        self.npcs[elite_3.id] = elite_3

        # Elite Four Member 4 - Spirit specialist
        elite_4 = NPC(
            id="elite_4",
            name="Elite Phantom",
            location_id="elite_hall",
            x=12,
            y=14,
            sprite="E",
            is_trainer=True,
            dialogues=[
                Dialogue("The spirits will decide your fate!"),
                Dialogue("Your spirit burns brighter than mine!")
            ]
        )
        self.npcs[elite_4.id] = elite_4

        # Champion - the final challenge
        champion = NPC(
            id="champion",
            name="Champion Aurora",
            location_id="elite_hall",
            x=10,
            y=3,
            sprite="C",
            is_trainer=True,
            dialogues=[
                Dialogue("You've made it this far. I am the Champion! Show me everything!"),
                Dialogue("Congratulations! You are the new Champion!")
            ]
        )
        self.npcs[champion.id] = champion

        # Move Relearner - Special NPC to teach forgotten moves
        move_relearner = NPC(
            id="move_relearner",
            name="Move Tutor Ray",
            location_id="town_tenth",
            x=15,
            y=5,
            sprite="M",
            dialogues=[
                Dialogue("I can help your creatures remember forgotten moves!"),
                Dialogue("Come back anytime you need to relearn moves!")
            ]
        )
        self.npcs[move_relearner.id] = move_relearner

        # TM Shop in eighth town
        tm_shop = NPC(
            id="tm_shop_boulder",
            name="TM Merchant Terra",
            location_id="town_eighth",
            x=15,
            y=10,
            sprite="S",
            is_shopkeeper=True,
            shop_inventory=[
                'tm01', 'tm02', 'tm03', 'tm04', 'tm05', 'tm06',
                'tm07', 'tm08', 'tm09', 'tm10', 'tm11', 'tm12',
                'tm13', 'tm14', 'tm15', 'tm16', 'tm17'
            ],
            dialogues=[
                Dialogue("Welcome to the TM Shop!"),
                Dialogue("These Technical Machines contain powerful moves!")
            ]
        )
        self.npcs[tm_shop.id] = tm_shop

        # TM Shop in ninth town
        tm_shop_2 = NPC(
            id="tm_shop_mindspire",
            name="TM Merchant Mind",
            location_id="town_ninth",
            x=15,
            y=10,
            sprite="S",
            is_shopkeeper=True,
            shop_inventory=[
                'tm18', 'tm19', 'tm20', 'tm21', 'tm22', 'tm23',
                'tm24', 'tm25', 'tm26', 'tm27', 'tm28', 'tm29',
                'tm30', 'tm31', 'tm32', 'tm33', 'tm34'
            ],
            dialogues=[
                Dialogue("More TMs for your collection!"),
                Dialogue("Master these moves and nothing can stop you!")
            ]
        )
        self.npcs[tm_shop_2.id] = tm_shop_2

        # TM Shop in tenth town
        tm_shop_3 = NPC(
            id="tm_shop_victory",
            name="TM Merchant Victory",
            location_id="town_tenth",
            x=14,
            y=10,
            sprite="S",
            is_shopkeeper=True,
            shop_inventory=[
                'tm35', 'tm36', 'tm37', 'tm38', 'tm39', 'tm40',
                'tm41', 'tm42', 'tm43', 'tm44', 'tm45', 'tm46',
                'tm47', 'tm48', 'tm49', 'tm50', 'tm51'
            ],
            dialogues=[
                Dialogue("The finest TMs for the final challenges!"),
                Dialogue("With these moves, you can conquer the Elite Four!")
            ]
        )
        self.npcs[tm_shop_3.id] = tm_shop_3

        # Additional trainers on Route 4
        route4_trainer1 = NPC(
            id="trainer_route4_1",
            name="Swimmer Maya",
            location_id="route_4",
            x=10,
            y=15,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("The ocean calls to me!"),
                Dialogue("You surf right over me!")
            ]
        )
        self.npcs[route4_trainer1.id] = route4_trainer1

        route4_trainer2 = NPC(
            id="trainer_route4_2",
            name="Fisherman Ron",
            location_id="route_4",
            x=10,
            y=25,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("I caught these creatures fishing!"),
                Dialogue("You reeled me in!")
            ]
        )
        self.npcs[route4_trainer2.id] = route4_trainer2

        # Additional trainers on Route 7
        route7_trainer1 = NPC(
            id="trainer_route7_1",
            name="Blackbelt Ken",
            location_id="route_7",
            x=10,
            y=20,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("My martial arts are unmatched!"),
                Dialogue("Your fighting spirit wins!")
            ]
        )
        self.npcs[route7_trainer1.id] = route7_trainer1

        route7_trainer2 = NPC(
            id="trainer_route7_2",
            name="Psychic Luna",
            location_id="route_7",
            x=10,
            y=35,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("I foresaw this battle..."),
                Dialogue("My vision was clouded!")
            ]
        )
        self.npcs[route7_trainer2.id] = route7_trainer2

        # Additional trainers on Route 9
        route9_trainer1 = NPC(
            id="trainer_route9_1",
            name="Ace Trainer Sarah",
            location_id="route_9",
            x=10,
            y=20,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("I'm an elite trainer!"),
                Dialogue("You're even stronger than me!")
            ]
        )
        self.npcs[route9_trainer1.id] = route9_trainer1

        route9_trainer2 = NPC(
            id="trainer_route9_2",
            name="Dragon Tamer Drake",
            location_id="route_9",
            x=10,
            y=40,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("My creatures have the power of legends!"),
                Dialogue("You've tamed the untamable!")
            ]
        )
        self.npcs[route9_trainer2.id] = route9_trainer2

        # Victory Road trainers
        victory_trainer1 = NPC(
            id="trainer_victory_1",
            name="Veteran Marcus",
            location_id="victory_road",
            x=15,
            y=15,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("Only the best make it through Victory Road!"),
                Dialogue("You're ready for the Elite Four!")
            ]
        )
        self.npcs[victory_trainer1.id] = victory_trainer1

        victory_trainer2 = NPC(
            id="trainer_victory_2",
            name="Veteran Diana",
            location_id="victory_road",
            x=15,
            y=25,
            sprite="T",
            is_trainer=True,
            dialogues=[
                Dialogue("Turn back if you're not ready!"),
                Dialogue("You have what it takes!")
            ]
        )
        self.npcs[victory_trainer2.id] = victory_trainer2

        # Battle Tower Master - post-game challenge trainer
        battle_tower_master = NPC(
            id="battle_tower_master",
            name="Tower Master Zane",
            location_id="battle_tower",
            x=10,
            y=5,
            sprite="B",
            is_trainer=True,
            dialogues=[
                Dialogue("Welcome to the Battle Tower! I'll test your skills with random powerful creatures!"),
                Dialogue("You're truly a master trainer! Come back anytime for another challenge!")
            ]
        )
        self.npcs[battle_tower_master.id] = battle_tower_master

        # Battle Tower Assistant - provides healing
        battle_tower_healer = NPC(
            id="battle_tower_healer",
            name="Tower Assistant",
            location_id="battle_tower",
            x=5,
            y=10,
            sprite="N",
            is_healer=True,
            dialogues=[
                Dialogue("Welcome to the Battle Tower! Let me heal your team!"),
                Dialogue("Good luck in your battles!")
            ]
        )
        self.npcs[battle_tower_healer.id] = battle_tower_healer

        # Legendary Guardians - special trainers protecting legendaries
        legendary_guardian_1 = NPC(
            id="legendary_guardian_1",
            name="Guardian Kai",
            location_id="legendary_sanctuary",
            x=17,
            y=10,
            sprite="G",
            is_trainer=True,
            dialogues=[
                Dialogue("Only those who have defeated the Champion may enter this sacred place!"),
                Dialogue("You have proven yourself worthy!")
            ]
        )
        self.npcs[legendary_guardian_1.id] = legendary_guardian_1

        legendary_guardian_2 = NPC(
            id="legendary_guardian_2",
            name="Guardian Luna",
            location_id="legendary_sanctuary",
            x=17,
            y=30,
            sprite="G",
            is_trainer=True,
            dialogues=[
                Dialogue("The legendary creatures ahead are not to be taken lightly!"),
                Dialogue("You've earned the right to proceed!")
            ]
        )
        self.npcs[legendary_guardian_2.id] = legendary_guardian_2

        # Legendary Researcher - provides lore about legendaries
        legendary_researcher = NPC(
            id="legendary_researcher",
            name="Professor Sage",
            location_id="legendary_sanctuary",
            x=17,
            y=20,
            sprite="P",
            dialogues=[
                Dialogue("I study the legendary creatures of this region. They are the strongest of all!"),
                Dialogue("Six legendary creatures dwell in this sanctuary. Tread carefully!")
            ]
        )
        self.npcs[legendary_researcher.id] = legendary_researcher

        # Legendary Encounter NPCs - These are one-time battles with legendary creatures
        # Positioned at various spots in the Legendary Sanctuary
        # Each represents a specific legendary creature (IDs 146-151)

        legendary_encounter_1 = NPC(
            id="legendary_encounter_1",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=5,
            y=10,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("A powerful legendary creature blocks your path!"),
                Dialogue("The legendary creature watches you intently...")
            ]
        )
        self.npcs[legendary_encounter_1.id] = legendary_encounter_1

        legendary_encounter_2 = NPC(
            id="legendary_encounter_2",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=29,
            y=10,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("A majestic legendary creature appears!"),
                Dialogue("The legendary aura is overwhelming...")
            ]
        )
        self.npcs[legendary_encounter_2.id] = legendary_encounter_2

        legendary_encounter_3 = NPC(
            id="legendary_encounter_3",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=5,
            y=30,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("An ancient legendary creature emerges!"),
                Dialogue("The legendary creature radiates power...")
            ]
        )
        self.npcs[legendary_encounter_3.id] = legendary_encounter_3

        legendary_encounter_4 = NPC(
            id="legendary_encounter_4",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=29,
            y=30,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("A rare legendary creature stands before you!"),
                Dialogue("The legendary presence is unmistakable...")
            ]
        )
        self.npcs[legendary_encounter_4.id] = legendary_encounter_4

        legendary_encounter_5 = NPC(
            id="legendary_encounter_5",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=10,
            y=20,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("A mythical legendary creature awaits!"),
                Dialogue("The legendary creature's eyes glow with power...")
            ]
        )
        self.npcs[legendary_encounter_5.id] = legendary_encounter_5

        legendary_encounter_6 = NPC(
            id="legendary_encounter_6",
            name="Legendary Creature",
            location_id="legendary_sanctuary",
            x=24,
            y=20,
            sprite="L",
            is_trainer=True,
            dialogues=[
                Dialogue("The most powerful legendary creature appears!"),
                Dialogue("The ultimate legendary challenge stands before you...")
            ]
        )
        self.npcs[legendary_encounter_6.id] = legendary_encounter_6

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get NPC by ID."""
        return self.npcs.get(npc_id)

    def get_npcs_at_location(self, location_id: str) -> List[NPC]:
        """Get all NPCs at a specific location."""
        return [npc for npc in self.npcs.values()
                if npc.location_id == location_id]

    def get_npc_at_position(
        self,
        location_id: str,
        x: int,
        y: int
    ) -> Optional[NPC]:
        """Get NPC at specific position."""
        for npc in self.npcs.values():
            if npc.location_id == location_id and npc.x == x and npc.y == y:
                return npc
        return None
