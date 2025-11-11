#!/usr/bin/env python3
"""
Genemon - A Python Monster Collector RPG

Main entry point for the game.
"""

import sys
import os

# Add the loop directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.core.game import Game


def main():
    """Main entry point."""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
