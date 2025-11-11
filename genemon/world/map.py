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

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get location by ID."""
        return self.locations.get(location_id)

    def get_starting_location(self) -> Location:
        """Get the starting location."""
        return self.locations["town_starter"]
