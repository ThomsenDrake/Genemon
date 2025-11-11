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

    def __init__(self):
        """Initialize NPC registry."""
        self.npcs: Dict[str, NPC] = {}
        self._create_npcs()

    def _create_npcs(self):
        """Create all authored NPCs."""

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
                'ether',
                'antidote',
                'awakening',
                'burn_heal',
                'paralyze_heal',
                'capture_ball'
            ],
            dialogues=[
                Dialogue("Welcome to my shop!"),
                Dialogue("I sell potions and capture balls!")
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
