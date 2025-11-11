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
            dialogues=[
                Dialogue("Welcome to my shop!"),
                Dialogue("I sell potions and capture balls!")
            ]
        )
        self.npcs[shopkeeper.id] = shopkeeper

        # Gym Leader in third town
        gym_leader = NPC(
            id="gym_leader_1",
            name="Leader Flint",
            location_id="town_third",
            x=10,
            y=7,
            sprite="G",
            is_trainer=True,
            dialogues=[
                Dialogue("I'm the Flame-type Gym Leader!"),
                Dialogue("Prove your strength in battle!")
            ]
        )
        self.npcs[gym_leader.id] = gym_leader

        # Healer in each town
        healer_newbark = NPC(
            id="healer_newbark",
            name="Nurse Joy",
            location_id="town_starter",
            x=14,
            y=5,
            sprite="H",
            dialogues=[
                Dialogue("I can heal your creatures!"),
                Dialogue("Come back anytime!")
            ]
        )
        self.npcs[healer_newbark.id] = healer_newbark

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
