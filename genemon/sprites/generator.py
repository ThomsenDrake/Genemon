"""
Pixel sprite generation for creatures.
Generates actual pixel art sprites as 2D arrays of colors.
"""

import random
from typing import List, Tuple, Dict
import json


class Color:
    """RGB color representation."""

    def __init__(self, r: int, g: int, b: int):
        self.r = max(0, min(255, r))
        self.g = max(0, min(255, g))
        self.b = max(0, min(255, b))

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def darken(self, factor: float = 0.7) -> 'Color':
        """Return a darker version of this color."""
        return Color(
            int(self.r * factor),
            int(self.g * factor),
            int(self.b * factor)
        )

    def lighten(self, factor: float = 1.3) -> 'Color':
        """Return a lighter version of this color."""
        return Color(
            min(255, int(self.r * factor)),
            min(255, int(self.g * factor)),
            min(255, int(self.b * factor))
        )


# Transparent color
TRANSPARENT = Color(0, 0, 0)


# Type-based color palettes
TYPE_COLORS = {
    "Flame": [Color(255, 100, 0), Color(255, 200, 0), Color(200, 50, 0)],
    "Aqua": [Color(50, 150, 255), Color(100, 200, 255), Color(0, 100, 200)],
    "Leaf": [Color(100, 200, 50), Color(50, 150, 50), Color(150, 255, 100)],
    "Volt": [Color(255, 255, 0), Color(255, 200, 0), Color(200, 200, 0)],
    "Frost": [Color(150, 200, 255), Color(200, 230, 255), Color(100, 150, 200)],
    "Terra": [Color(150, 100, 50), Color(100, 70, 40), Color(200, 150, 100)],
    "Gale": [Color(200, 220, 255), Color(150, 180, 220), Color(100, 150, 200)],
    "Toxin": [Color(150, 50, 150), Color(200, 100, 200), Color(100, 0, 100)],
    "Mind": [Color(255, 100, 200), Color(200, 150, 255), Color(255, 150, 220)],
    "Spirit": [Color(100, 50, 150), Color(150, 100, 200), Color(80, 40, 120)],
    "Beast": [Color(180, 180, 180), Color(150, 150, 150), Color(120, 120, 120)],
    "Brawl": [Color(200, 100, 50), Color(150, 80, 40), Color(255, 150, 100)],
    "Insect": [Color(150, 200, 50), Color(100, 150, 100), Color(200, 255, 150)],
    "Metal": [Color(180, 180, 200), Color(150, 150, 170), Color(200, 200, 220)],
    "Mystic": [Color(255, 150, 200), Color(255, 200, 220), Color(200, 100, 150)],
    "Shadow": [Color(80, 80, 100), Color(50, 50, 70), Color(100, 100, 120)]
}


class SpriteGenerator:
    """Generates pixel art sprites for creatures."""

    def __init__(self, seed: int = None):
        """
        Initialize sprite generator.

        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)

    def generate_creature_sprites(
        self,
        creature_id: int,
        types: List[str],
        archetype: str = "quadruped",
        is_shiny: bool = False
    ) -> Dict[str, List[List[str]]]:
        """
        Generate all sprites for a creature.

        Args:
            creature_id: Unique ID for reproducibility
            types: Creature types (for color palette)
            archetype: Body type (bird, fish, quadruped, etc.)
            is_shiny: If True, generates shiny (alternate color) variant

        Returns:
            Dictionary with 'front', 'back', and 'mini' sprite data
            Each sprite is a 2D array of hex color strings
        """
        # Set seed based on creature ID for reproducibility
        self.rng.seed(self.seed + creature_id)

        # Get color palette (shiny or normal)
        palette = self._get_palette(types, is_shiny=is_shiny)

        # Generate sprites
        front = self._generate_front_sprite(palette, archetype)
        back = self._generate_back_sprite(palette, archetype)
        mini = self._generate_mini_sprite(palette, archetype)

        return {
            'front': self._sprite_to_hex_array(front),
            'back': self._sprite_to_hex_array(back),
            'mini': self._sprite_to_hex_array(mini)
        }

    def _get_palette(self, types: List[str], is_shiny: bool = False) -> List[Color]:
        """
        Get color palette based on creature types.

        Args:
            types: List of creature types
            is_shiny: If True, generates shiny (alternate) color palette

        Returns:
            List of Color objects for sprite rendering
        """
        primary_type = types[0] if types else "Beast"

        if primary_type in TYPE_COLORS:
            base_colors = TYPE_COLORS[primary_type].copy()
        else:
            base_colors = TYPE_COLORS["Beast"].copy()

        # Apply shiny transformation if requested
        if is_shiny:
            base_colors = self._shinyfy_palette(base_colors)

        # Add some variation
        palette = base_colors + [
            base_colors[0].darken(),
            base_colors[0].lighten(),
            Color(0, 0, 0),  # Black for outlines
            Color(255, 255, 255)  # White for highlights
        ]

        return palette

    def _shinyfy_palette(self, palette: List[Color]) -> List[Color]:
        """
        Transform a color palette into a shiny variant.
        Applies color shifts to create rare, alternate colorations.

        Args:
            palette: Original color palette

        Returns:
            Shiny variant palette
        """
        shiny_palette = []

        for color in palette:
            # Apply golden/sparkle tint for shiny variants
            # Shift hue by rotating RGB values and adjusting saturation
            r, g, b = color.r, color.g, color.b

            # Different shiny strategies based on color intensity
            avg = (r + g + b) // 3

            if avg < 85:  # Dark colors -> shift to purple/blue
                shiny_color = Color(
                    min(255, r + 50),
                    min(255, g + 30),
                    min(255, b + 100)
                )
            elif avg < 170:  # Mid colors -> shift to gold/bronze
                shiny_color = Color(
                    min(255, r + 60),
                    min(255, g + 40),
                    max(0, b - 30)
                )
            else:  # Light colors -> shift to silver/cyan
                shiny_color = Color(
                    min(255, max(0, r - 20)),
                    min(255, g + 20),
                    min(255, b + 40)
                )

            shiny_palette.append(shiny_color)

        return shiny_palette

    def _generate_front_sprite(
        self,
        palette: List[Color],
        archetype: str
    ) -> List[List[Color]]:
        """Generate 56x56 front-facing sprite."""
        size = 56
        sprite = [[TRANSPARENT for _ in range(size)] for _ in range(size)]

        # Draw based on archetype
        if archetype in ["bird", "quadruped", "biped"]:
            sprite = self._draw_symmetric_creature(sprite, palette, size)
        elif archetype in ["serpent", "fish"]:
            sprite = self._draw_elongated_creature(sprite, palette, size)
        else:
            sprite = self._draw_blob_creature(sprite, palette, size)

        return sprite

    def _generate_back_sprite(
        self,
        palette: List[Color],
        archetype: str
    ) -> List[List[Color]]:
        """Generate 56x56 back-facing sprite (simpler than front)."""
        size = 56
        sprite = [[TRANSPARENT for _ in range(size)] for _ in range(size)]

        # Back sprites are typically simpler
        sprite = self._draw_simple_back(sprite, palette, size)

        return sprite

    def _generate_mini_sprite(
        self,
        palette: List[Color],
        archetype: str
    ) -> List[List[Color]]:
        """Generate 16x16 mini sprite for overworld."""
        size = 16
        sprite = [[TRANSPARENT for _ in range(size)] for _ in range(size)]

        # Mini sprite is a simplified version
        sprite = self._draw_mini(sprite, palette, size)

        return sprite

    def _draw_symmetric_creature(
        self,
        sprite: List[List[Color]],
        palette: List[Color],
        size: int
    ) -> List[List[Color]]:
        """Draw a symmetric creature (most monsters)."""
        center_x = size // 2
        body_color = palette[0]
        dark_color = palette[3] if len(palette) > 3 else body_color.darken()
        outline_color = palette[5] if len(palette) > 5 else Color(0, 0, 0)

        # Draw body (oval shape in center)
        for y in range(size // 4, 3 * size // 4):
            for x in range(size // 3, 2 * size // 3):
                # Create oval using distance formula
                dx = (x - center_x) / (size // 6)
                dy = (y - size // 2) / (size // 4)
                if dx * dx + dy * dy < 1:
                    sprite[y][x] = body_color

        # Add simple head (circle on top)
        head_y = size // 4
        for y in range(max(0, head_y - size // 8), min(size, head_y + size // 8)):
            for x in range(center_x - size // 10, center_x + size // 10):
                dx = (x - center_x) / (size // 10)
                dy = (y - head_y) / (size // 8)
                if dx * dx + dy * dy < 1:
                    sprite[y][x] = body_color

        # Add eyes
        eye_y = size // 4
        for eye_x in [center_x - size // 12, center_x + size // 12]:
            if 0 <= eye_y < size and 0 <= eye_x < size:
                sprite[eye_y][eye_x] = Color(0, 0, 0)

        # Add some detail spots
        num_spots = self.rng.randint(2, 5)
        spot_color = palette[1] if len(palette) > 1 else body_color.lighten()
        for _ in range(num_spots):
            spot_x = self.rng.randint(size // 3, 2 * size // 3)
            spot_y = self.rng.randint(size // 3, 2 * size // 3)
            if sprite[spot_y][spot_x] == body_color:
                sprite[spot_y][spot_x] = spot_color

        return sprite

    def _draw_elongated_creature(
        self,
        sprite: List[List[Color]],
        palette: List[Color],
        size: int
    ) -> List[List[Color]]:
        """Draw an elongated creature (serpent, fish)."""
        body_color = palette[0]
        accent_color = palette[1] if len(palette) > 1 else body_color.lighten()

        center_x = size // 2

        # Draw sinuous body
        for y in range(size // 6, 5 * size // 6):
            # Create wave pattern
            offset = int(size // 8 * self.rng.random() *
                        (1 if y % 10 < 5 else -1))
            width = size // 6

            for x in range(max(0, center_x + offset - width),
                          min(size, center_x + offset + width)):
                sprite[y][x] = body_color

        # Add head
        head_y = size // 6
        for y in range(max(0, head_y - size // 12), min(size, head_y + size // 12)):
            for x in range(center_x - size // 8, center_x + size // 8):
                sprite[y][x] = body_color

        # Eyes
        sprite[head_y][center_x - size // 16] = Color(0, 0, 0)
        sprite[head_y][center_x + size // 16] = Color(0, 0, 0)

        return sprite

    def _draw_blob_creature(
        self,
        sprite: List[List[Color]],
        palette: List[Color],
        size: int
    ) -> List[List[Color]]:
        """Draw a simple blob-like creature."""
        body_color = palette[0]
        center_x, center_y = size // 2, size // 2

        # Draw blob
        for y in range(size // 4, 3 * size // 4):
            for x in range(size // 4, 3 * size // 4):
                dx = (x - center_x) / (size // 4)
                dy = (y - center_y) / (size // 4)
                if dx * dx + dy * dy < 1:
                    sprite[y][x] = body_color

        # Eyes
        sprite[center_y - size // 12][center_x - size // 12] = Color(0, 0, 0)
        sprite[center_y - size // 12][center_x + size // 12] = Color(0, 0, 0)

        return sprite

    def _draw_simple_back(
        self,
        sprite: List[List[Color]],
        palette: List[Color],
        size: int
    ) -> List[List[Color]]:
        """Draw simplified back sprite."""
        body_color = palette[0]
        center_x = size // 2

        # Simple back silhouette
        for y in range(size // 4, 3 * size // 4):
            for x in range(size // 3, 2 * size // 3):
                dx = (x - center_x) / (size // 6)
                dy = (y - size // 2) / (size // 4)
                if dx * dx + dy * dy < 1:
                    sprite[y][x] = body_color

        return sprite

    def _draw_mini(
        self,
        sprite: List[List[Color]],
        palette: List[Color],
        size: int
    ) -> List[List[Color]]:
        """Draw 16x16 mini sprite."""
        body_color = palette[0]
        center = size // 2

        # Small blob for mini sprite
        for y in range(size // 4, 3 * size // 4):
            for x in range(size // 4, 3 * size // 4):
                dx = (x - center) / (size // 4)
                dy = (y - center) / (size // 4)
                if dx * dx + dy * dy < 1:
                    sprite[y][x] = body_color

        # Tiny eyes
        sprite[center - 2][center - 2] = Color(0, 0, 0)
        sprite[center - 2][center + 2] = Color(0, 0, 0)

        return sprite

    def _sprite_to_hex_array(self, sprite: List[List[Color]]) -> List[List[str]]:
        """Convert sprite color array to hex string array for serialization."""
        return [
            [
                (col.to_hex() if col != TRANSPARENT else "transparent")
                for col in row
            ]
            for row in sprite
        ]

    def sprite_to_ascii(self, sprite_data: List[List[str]], scale: int = 1) -> str:
        """
        Convert sprite to ASCII art for terminal display.

        Args:
            sprite_data: 2D array of hex colors
            scale: Scaling factor (1 = full size)

        Returns:
            ASCII representation of sprite
        """
        # Downsample if scale < 1
        if scale < 1:
            sprite_data = self._downsample_sprite(sprite_data, scale)

        ascii_art = []
        for row in sprite_data:
            line = ""
            for pixel in row:
                if pixel == "transparent":
                    line += " "
                else:
                    # Use different characters for different brightness
                    brightness = self._hex_to_brightness(pixel)
                    if brightness > 200:
                        line += "#"
                    elif brightness > 150:
                        line += "+"
                    elif brightness > 100:
                        line += "*"
                    elif brightness > 50:
                        line += "."
                    else:
                        line += ":"
            ascii_art.append(line)

        return "\n".join(ascii_art)

    def _hex_to_brightness(self, hex_color: str) -> int:
        """Calculate brightness from hex color."""
        if hex_color == "transparent":
            return 0

        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return int((r + g + b) / 3)

    def _downsample_sprite(
        self,
        sprite: List[List[str]],
        scale: float
    ) -> List[List[str]]:
        """Downsample sprite by scale factor."""
        height = len(sprite)
        width = len(sprite[0]) if height > 0 else 0

        new_height = max(1, int(height * scale))
        new_width = max(1, int(width * scale))

        new_sprite = []
        for y in range(new_height):
            row = []
            for x in range(new_width):
                src_y = min(int(y / scale), height - 1)
                src_x = min(int(x / scale), width - 1)
                row.append(sprite[src_y][src_x])
            new_sprite.append(row)

        return new_sprite

    @staticmethod
    def hex_to_color(hex_string: str) -> Color:
        """Convert hex string to Color object."""
        if hex_string == "transparent":
            return TRANSPARENT
        if hex_string.startswith('#'):
            hex_string = hex_string[1:]
        r = int(hex_string[0:2], 16)
        g = int(hex_string[2:4], 16)
        b = int(hex_string[4:6], 16)
        return Color(r, g, b)

    @staticmethod
    def hex_array_to_color_array(hex_sprite: List[List[str]]) -> List[List[Color]]:
        """Convert 2D hex string array to 2D Color array."""
        return [[SpriteGenerator.hex_to_color(hex_color) for hex_color in row] for row in hex_sprite]

    @staticmethod
    def export_sprite_to_png(sprite: List[List[Color]], filename: str, scale: int = 1):
        """
        Export a sprite to a PNG file using pure Python (no PIL/Pillow required).

        Args:
            sprite: 2D array of Color objects
            filename: Output PNG filename
            scale: Scale factor for upscaling (default 1 = no scaling)

        Note: This uses pure Python PNG encoding without external dependencies.
        For production use, consider using Pillow library for better PNG support.
        """
        import struct
        import zlib

        height = len(sprite)
        width = len(sprite[0]) if height > 0 else 0

        if scale > 1:
            # Scale up the sprite
            scaled_sprite = []
            for y in range(height):
                for _ in range(scale):
                    row = []
                    for x in range(width):
                        for _ in range(scale):
                            row.append(sprite[y][x])
                    scaled_sprite.append(row)
            sprite = scaled_sprite
            height = len(sprite)
            width = len(sprite[0]) if height > 0 else 0

        # PNG file structure
        def write_chunk(chunk_type: bytes, data: bytes) -> bytes:
            """Write a PNG chunk with length, type, data, and CRC."""
            length = struct.pack('>I', len(data))
            crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
            return length + chunk_type + data + crc

        # Build PNG data
        png_data = b'\x89PNG\r\n\x1a\n'  # PNG signature

        # IHDR chunk (image header)
        ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # RGB, 8-bit
        png_data += write_chunk(b'IHDR', ihdr)

        # IDAT chunk (image data)
        raw_data = bytearray()
        for row in sprite:
            raw_data.append(0)  # Filter type (0 = None)
            for color in row:
                raw_data.extend([color.r, color.g, color.b])

        compressed = zlib.compress(bytes(raw_data), 9)
        png_data += write_chunk(b'IDAT', compressed)

        # IEND chunk (end of file)
        png_data += write_chunk(b'IEND', b'')

        # Write to file
        with open(filename, 'wb') as f:
            f.write(png_data)

    @staticmethod
    def export_creature_sprites_to_png(front_sprite: List[List[Color]],
                                      back_sprite: List[List[Color]],
                                      mini_sprite: List[List[Color]],
                                      creature_name: str,
                                      output_dir: str = "sprites",
                                      scale: int = 2):
        """
        Export all three sprites for a creature to PNG files.

        Args:
            front_sprite: Front-facing sprite
            back_sprite: Back-facing sprite
            mini_sprite: Mini sprite for overworld
            creature_name: Name of the creature (for filenames)
            output_dir: Directory to save sprites (will be created if needed)
            scale: Scale factor for upscaling (default 2x)
        """
        import os

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Export each sprite
        SpriteGenerator.export_sprite_to_png(
            front_sprite,
            os.path.join(output_dir, f"{creature_name}_front.png"),
            scale=scale
        )

        SpriteGenerator.export_sprite_to_png(
            back_sprite,
            os.path.join(output_dir, f"{creature_name}_back.png"),
            scale=scale
        )

        SpriteGenerator.export_sprite_to_png(
            mini_sprite,
            os.path.join(output_dir, f"{creature_name}_mini.png"),
            scale=scale * 2  # Mini sprites get extra scaling since they're smaller
        )

    @staticmethod
    def export_all_creatures_to_png(species_dict: dict,
                                   output_dir: str = "sprites_export",
                                   scale: int = 2,
                                   progress_callback=None):
        """
        Export all 151 creatures to PNG files in bulk.

        Args:
            species_dict: Dictionary of creature_id -> CreatureSpecies
            output_dir: Directory to save all sprites (will be created if needed)
            scale: Scale factor for upscaling (default 2x)
            progress_callback: Optional function(current, total, name) called for each creature

        Returns:
            Number of creatures exported successfully
        """
        import os

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        total = len(species_dict)
        exported = 0

        for creature_id, species in sorted(species_dict.items()):
            try:
                # Get sprite data (handle both dict and list formats)
                if hasattr(species, 'sprite_data') and species.sprite_data:
                    sprite_data = species.sprite_data
                else:
                    # Skip if no sprite data
                    print(f"Warning: No sprite data for creature #{creature_id} ({species.name})")
                    continue

                # Convert hex sprites to Color sprites
                front_color = SpriteGenerator.hex_array_to_color_array(sprite_data['front'])
                back_color = SpriteGenerator.hex_array_to_color_array(sprite_data['back'])
                mini_color = SpriteGenerator.hex_array_to_color_array(sprite_data['mini'])

                # Create sanitized filename
                safe_name = f"{creature_id:03d}_{species.name.replace(' ', '_').replace('/', '_')}"

                # Export all three sprites
                SpriteGenerator.export_creature_sprites_to_png(
                    front_color,
                    back_color,
                    mini_color,
                    safe_name,
                    output_dir,
                    scale
                )

                exported += 1

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(exported, total, species.name)

            except Exception as e:
                print(f"Error exporting creature #{creature_id} ({species.name}): {e}")

        return exported
