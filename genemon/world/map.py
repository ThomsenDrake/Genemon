"""
World map and location system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class TileType(Enum):
    """Types of terrain tiles."""
    GRASS = "grass"
    WATER = "water"
    PATH = "path"
    BUILDING = "building"
    TREE = "tree"
    MOUNTAIN = "mountain"
    CAVE = "cave"
    DOOR = "door"


@dataclass
class Tile:
    """A single map tile."""
    type: TileType
    walkable: bool
    can_encounter: bool = False
    encounter_rate: float = 0.0

    def get_char(self) -> str:
        """Get ASCII character for this tile."""
        chars = {
            TileType.GRASS: ".",
            TileType.WATER: "~",
            TileType.PATH: ":",
            TileType.BUILDING: "#",
            TileType.TREE: "T",
            TileType.MOUNTAIN: "^",
            TileType.CAVE: "C",
            TileType.DOOR: "D"
        }
        return chars.get(self.type, "?")


@dataclass
class Location:
    """
    A location in the game world (town, route, cave, etc.).
    """
    id: str
    name: str
    width: int
    height: int
    tiles: List[List[Tile]]
    spawn_x: int  # Player spawn coordinates
    spawn_y: int
    connections: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    # Connections: {location_id: (exit_x, exit_y)}

    can_fly_to: bool = True  # Can player fast-travel here?
    has_healing: bool = False  # Has a healing center?
    has_shop: bool = False

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at coordinates, or None if out of bounds."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable."""
        tile = self.get_tile(x, y)
        return tile is not None and tile.walkable

    def to_ascii(self) -> str:
        """Render location as ASCII art."""
        lines = [f"=== {self.name} ==="]
        for row in self.tiles:
            lines.append("".join(tile.get_char() for tile in row))
        return "\n".join(lines)


class LocationBuilder:
    """Helper class to build locations."""

    @staticmethod
    def create_town(
        location_id: str,
        name: str,
        width: int = 20,
        height: int = 20
    ) -> Location:
        """Create a town location."""
        # Create a simple town layout
        tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                # Borders are trees/mountains
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    if x == width // 2 and y == height - 1:
                        # Exit at bottom center
                        row.append(Tile(TileType.PATH, True))
                    else:
                        row.append(Tile(TileType.TREE, False))
                # Some buildings
                elif (3 <= x <= 6 and 3 <= y <= 6) or \
                     (13 <= x <= 16 and 3 <= y <= 6) or \
                     (8 <= x <= 11 and 10 <= y <= 13):
                    row.append(Tile(TileType.BUILDING, False))
                # Paths around buildings
                elif x in [2, 7, 12, 17] or y in [2, 7, 9, 14]:
                    row.append(Tile(TileType.PATH, True))
                # Rest is grass
                else:
                    row.append(Tile(TileType.GRASS, True))
            tiles.append(row)

        return Location(
            id=location_id,
            name=name,
            width=width,
            height=height,
            tiles=tiles,
            spawn_x=width // 2,
            spawn_y=height - 2,
            can_fly_to=True,
            has_healing=True,
            has_shop=True
        )

    @staticmethod
    def create_route(
        location_id: str,
        name: str,
        length: int = 30
    ) -> Location:
        """Create a route (path with grass for encounters)."""
        width = 15
        height = length

        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                # Borders are trees
                if x == 0 or x == width - 1:
                    row.append(Tile(TileType.TREE, False))
                # Central path
                elif width // 2 - 2 <= x <= width // 2 + 2:
                    row.append(Tile(TileType.PATH, True))
                # Grass with encounters
                else:
                    row.append(Tile(
                        TileType.GRASS,
                        True,
                        can_encounter=True,
                        encounter_rate=0.15
                    ))
            tiles.append(row)

        return Location(
            id=location_id,
            name=name,
            width=width,
            height=height,
            tiles=tiles,
            spawn_x=width // 2,
            spawn_y=height - 1,
            can_fly_to=False
        )

    @staticmethod
    def create_cave(
        location_id: str,
        name: str,
        width: int = 25,
        height: int = 25
    ) -> Location:
        """Create a cave location."""
        tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                # Create cave-like structure with water
                if (x + y) % 7 == 0:
                    row.append(Tile(TileType.WATER, False))
                elif (x * y) % 11 == 0:
                    row.append(Tile(TileType.MOUNTAIN, False))
                else:
                    row.append(Tile(
                        TileType.GRASS,
                        True,
                        can_encounter=True,
                        encounter_rate=0.25
                    ))
            tiles.append(row)

        # Make entrance walkable
        tiles[height - 1][width // 2] = Tile(TileType.PATH, True)
        tiles[height - 2][width // 2] = Tile(TileType.PATH, True)

        return Location(
            id=location_id,
            name=name,
            width=width,
            height=height,
            tiles=tiles,
            spawn_x=width // 2,
            spawn_y=height - 2,
            can_fly_to=False
        )


class World:
    """The game world containing all locations."""

    def __init__(self):
        """Initialize the game world."""
        self.locations: Dict[str, Location] = {}
        self._create_world()

    def _create_world(self):
        """Create the authored world map."""

        # Starting town
        starter_town = LocationBuilder.create_town(
            "town_starter",
            "Newbark Village"
        )
        self.locations[starter_town.id] = starter_town

        # Route 1
        route_1 = LocationBuilder.create_route(
            "route_1",
            "Route 1",
            length=25
        )
        self.locations[route_1.id] = route_1

        # Second town
        second_town = LocationBuilder.create_town(
            "town_second",
            "Oakwood City"
        )
        self.locations[second_town.id] = second_town

        # Route 2
        route_2 = LocationBuilder.create_route(
            "route_2",
            "Route 2",
            length=30
        )
        self.locations[route_2.id] = route_2

        # First cave
        cave_1 = LocationBuilder.create_cave(
            "cave_1",
            "Whispering Cavern"
        )
        self.locations[cave_1.id] = cave_1

        # Third town (with gym)
        third_town = LocationBuilder.create_town(
            "town_third",
            "Steelforge Town"
        )
        self.locations[third_town.id] = third_town

        # Route 3
        route_3 = LocationBuilder.create_route(
            "route_3",
            "Route 3",
            length=35
        )
        self.locations[route_3.id] = route_3

        # Fourth town (second gym)
        fourth_town = LocationBuilder.create_town(
            "town_fourth",
            "Aquamarine Harbor"
        )
        self.locations[fourth_town.id] = fourth_town

        # Route 4
        route_4 = LocationBuilder.create_route(
            "route_4",
            "Route 4",
            length=32
        )
        self.locations[route_4.id] = route_4

        # Fifth town (third gym)
        fifth_town = LocationBuilder.create_town(
            "town_fifth",
            "Thunderpeak City"
        )
        self.locations[fifth_town.id] = fifth_town

        # Route 5
        route_5 = LocationBuilder.create_route(
            "route_5",
            "Route 5",
            length=38
        )
        self.locations[route_5.id] = route_5

        # Sixth town (fourth gym)
        sixth_town = LocationBuilder.create_town(
            "town_sixth",
            "Frostfield Village"
        )
        self.locations[sixth_town.id] = sixth_town

        # Route 6
        route_6 = LocationBuilder.create_route(
            "route_6",
            "Route 6",
            length=40
        )
        self.locations[route_6.id] = route_6

        # Seventh town (fifth gym)
        seventh_town = LocationBuilder.create_town(
            "town_seventh",
            "Shadowmere Town"
        )
        self.locations[seventh_town.id] = seventh_town

        # Route 7
        route_7 = LocationBuilder.create_route(
            "route_7",
            "Route 7",
            length=42
        )
        self.locations[route_7.id] = route_7

        # Eighth town (sixth gym - Terra)
        eighth_town = LocationBuilder.create_town(
            "town_eighth",
            "Boulder Ridge City"
        )
        self.locations[eighth_town.id] = eighth_town

        # Route 8
        route_8 = LocationBuilder.create_route(
            "route_8",
            "Route 8",
            length=45
        )
        self.locations[route_8.id] = route_8

        # Ninth town (seventh gym - Mind)
        ninth_town = LocationBuilder.create_town(
            "town_ninth",
            "Mindspire Heights"
        )
        self.locations[ninth_town.id] = ninth_town

        # Route 9
        route_9 = LocationBuilder.create_route(
            "route_9",
            "Route 9",
            length=48
        )
        self.locations[route_9.id] = route_9

        # Tenth town (eighth gym - Brawl)
        tenth_town = LocationBuilder.create_town(
            "town_tenth",
            "Victory Valley"
        )
        self.locations[tenth_town.id] = tenth_town

        # Victory Road - challenging path to Elite Four
        victory_road = LocationBuilder.create_cave(
            "victory_road",
            "Victory Road",
            width=30,
            height=35
        )
        self.locations[victory_road.id] = victory_road

        # Elite Four Hall - final challenge
        elite_hall = LocationBuilder.create_town(
            "elite_hall",
            "Champion's Hall"
        )
        elite_hall.has_healing = True
        elite_hall.has_shop = False
        self.locations[elite_hall.id] = elite_hall

        # Battle Tower - post-game challenge facility
        battle_tower = LocationBuilder.create_town(
            "battle_tower",
            "Battle Tower",
            width=20,
            height=25
        )
        battle_tower.has_healing = True
        battle_tower.has_shop = False
        self.locations[battle_tower.id] = battle_tower

        # Legendary Sanctuary - post-game legendary encounter area
        legendary_sanctuary = LocationBuilder.create_cave(
            "legendary_sanctuary",
            "Legendary Sanctuary",
            width=35,
            height=40
        )
        self.locations[legendary_sanctuary.id] = legendary_sanctuary

        # Set up connections
        starter_town.connections["route_1"] = (starter_town.width // 2, starter_town.height - 1)
        route_1.connections["town_starter"] = (route_1.width // 2, route_1.height - 1)
        route_1.connections["town_second"] = (route_1.width // 2, 0)
        second_town.connections["route_1"] = (second_town.width // 2, second_town.height - 1)
        second_town.connections["route_2"] = (second_town.width // 2, 0)
        route_2.connections["town_second"] = (route_2.width // 2, route_2.height - 1)
        route_2.connections["cave_1"] = (route_2.width // 2, 0)
        cave_1.connections["route_2"] = (cave_1.width // 2, cave_1.height - 1)
        cave_1.connections["town_third"] = (cave_1.width // 2, 0)
        third_town.connections["cave_1"] = (third_town.width // 2, third_town.height - 1)
        third_town.connections["route_3"] = (third_town.width // 2, 0)
        route_3.connections["town_third"] = (route_3.width // 2, route_3.height - 1)
        route_3.connections["town_fourth"] = (route_3.width // 2, 0)
        fourth_town.connections["route_3"] = (fourth_town.width // 2, fourth_town.height - 1)
        fourth_town.connections["route_4"] = (fourth_town.width // 2, 0)
        route_4.connections["town_fourth"] = (route_4.width // 2, route_4.height - 1)
        route_4.connections["town_fifth"] = (route_4.width // 2, 0)
        fifth_town.connections["route_4"] = (fifth_town.width // 2, fifth_town.height - 1)
        fifth_town.connections["route_5"] = (fifth_town.width // 2, 0)
        route_5.connections["town_fifth"] = (route_5.width // 2, route_5.height - 1)
        route_5.connections["town_sixth"] = (route_5.width // 2, 0)
        sixth_town.connections["route_5"] = (sixth_town.width // 2, sixth_town.height - 1)
        sixth_town.connections["route_6"] = (sixth_town.width // 2, 0)
        route_6.connections["town_sixth"] = (route_6.width // 2, route_6.height - 1)
        route_6.connections["town_seventh"] = (route_6.width // 2, 0)
        seventh_town.connections["route_6"] = (seventh_town.width // 2, seventh_town.height - 1)
        seventh_town.connections["route_7"] = (seventh_town.width // 2, 0)
        route_7.connections["town_seventh"] = (route_7.width // 2, route_7.height - 1)
        route_7.connections["town_eighth"] = (route_7.width // 2, 0)
        eighth_town.connections["route_7"] = (eighth_town.width // 2, eighth_town.height - 1)
        eighth_town.connections["route_8"] = (eighth_town.width // 2, 0)
        route_8.connections["town_eighth"] = (route_8.width // 2, route_8.height - 1)
        route_8.connections["town_ninth"] = (route_8.width // 2, 0)
        ninth_town.connections["route_8"] = (ninth_town.width // 2, ninth_town.height - 1)
        ninth_town.connections["route_9"] = (ninth_town.width // 2, 0)
        route_9.connections["town_ninth"] = (route_9.width // 2, route_9.height - 1)
        route_9.connections["town_tenth"] = (route_9.width // 2, 0)
        tenth_town.connections["route_9"] = (tenth_town.width // 2, tenth_town.height - 1)
        tenth_town.connections["victory_road"] = (tenth_town.width // 2, 0)
        victory_road.connections["town_tenth"] = (victory_road.width // 2, victory_road.height - 1)
        victory_road.connections["elite_hall"] = (victory_road.width // 2, 0)
        elite_hall.connections["victory_road"] = (elite_hall.width // 2, elite_hall.height - 1)
        elite_hall.connections["battle_tower"] = (elite_hall.width - 5, elite_hall.height // 2)
        battle_tower.connections["elite_hall"] = (5, battle_tower.height // 2)
        elite_hall.connections["legendary_sanctuary"] = (5, elite_hall.height // 2)
        legendary_sanctuary.connections["elite_hall"] = (legendary_sanctuary.width - 5, legendary_sanctuary.height // 2)

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get location by ID."""
        return self.locations.get(location_id)

    def get_starting_location(self) -> Location:
        """Get the starting location."""
        return self.locations["town_starter"]
