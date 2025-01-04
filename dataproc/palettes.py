from typing import List, Dict

class Palette:
    """
    Color palette management for data visualizations.
    Provides easy access to different color schemes.
    """

    _palettes: Dict[str, List[str]] = {
        "purples": ['#4361ee', '#3a0ca3', '#7209b7', '#560bad', '#480ca8',
                    '#3f37c9', '#4895ef', '#4cc9f0', '#3a86ff', '#0096c7'],
        "rainbow": ['#ff006e', '#8338ec', '#3a86ff', '#00f5d4', '#fb5607',
                    '#ff006e', '#3a86ff', '#ffbe0b', '#06d6a0', '#118ab2'],
        "nature": ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2',
                   '#1b4332', '#081c15', '#1b4332', '#2d6a4f', '#40916c'],
        "ocean": ['#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a',
                  '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'],
        "sunset": ['#ff6b6b', '#f06595', '#cc5de8', '#845ef7', '#5c7cfa',
                   '#339af0', '#22b8cf', '#20c997', '#51cf66', '#94d82d']
    }

    def __init__(self, name: str = "ocean"):
        """
        Initialize with a specific palette.
        
        Args:
            name: Name of the palette to use (default: "ocean")
        """
        self.set_palette(name)

    @property
    def available_palettes(self) -> List[str]:
        """Get list of available palette names."""
        return list(self._palettes.keys())

    def set_palette(self, name: str) -> None:
        """
        Set the active palette.
        
        Args:
            name: Name of the palette to use
        
        Raises:
            ValueError: If palette name doesn't exist
        """
        name = name.lower()
        if name not in self._palettes:
            raise ValueError(
                f"Unknown palette '{name}'. Available palettes: {', '.join(self.available_palettes)}"
            )
        self._active_palette = self._palettes[name]

    @property
    def colors(self) -> List[str]:
        """Get the current palette's colors."""
        return self._active_palette

    def add_palette(self, name: str, colors: List[str]) -> None:
        """
        Add a new custom palette.
        
        Args:
            name: Name for the new palette
            colors: List of color hex codes
        
        Raises:
            ValueError: If palette name already exists
        """
        name = name.lower()
        if name in self._palettes:
            raise ValueError(f"Palette '{name}' already exists")
        self._palettes[name] = colors

    def __getitem__(self, index: int) -> str:
        """Get color at specific index, wrapping around if index exceeds palette length."""
        return self._active_palette[index % len(self._active_palette)]

    def __len__(self) -> int:
        """Get number of colors in active palette."""
        return len(self._active_palette)

    def __iter__(self):
        """Iterate through colors in active palette."""
        return iter(self._active_palette)

# Example usage:
if __name__ == "__main__":
    # Initialize with default palette (ocean)
    palette = Palette()

    # Print available palettes
    print("Available palettes:", palette.available_palettes)

    # Use a different palette
    palette.set_palette("sunset")
    print("Sunset palette colors:", palette.colors)

    # Add a custom palette
    custom_colors = ['#001219', '#005f73', '#0a9396', '#94d2bd', '#ee9b00']
    palette.add_palette("custom", custom_colors)

    # Access colors by index (with wrapping)
    print("First color:", palette[0])
    print("Index beyond palette length:", palette[20])  # Will wrap around

    # Iterate through colors
    for color in palette:
        print("Color:", color)