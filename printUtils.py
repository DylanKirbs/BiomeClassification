"""
Utilities for printing to the terminal.
"""

from dataclasses import dataclass


@dataclass
class AnsiColours:
    """
    ANSI terminal escape codes.

    Use in string li
    """
    RED: str = "\033[91m"
    GREEN: str = "\033[92m"
    YELLOW: str = "\033[93m"
    BLUE: str = "\033[94m"
    MAGENTA: str = "\033[95m"
    CYAN: str = "\033[96m"
    WHITE: str = "\033[97m"
    RESET: str = "\033[0m"


def cPrint(text: str, color: str = AnsiColours.WHITE, end='\n'):
    """
    Prints the text to StdOut with the color applied.

    Args:
        text (str): The text to write.
        color (str, optional): The ANSI escape code. Defaults to AnsiColours.WHITE.
        end (str, optional): The line terminating character.
    """
    print(f'{color}{text}{AnsiColours.RESET}', end=end)


def hPrint(text: str, pattern: str, color: str = AnsiColours.RED, end='\n'):
    """
    Highlights a pattern in the text with the specified color.

    The pattern must be an exact match.

    Args:
        text (str): The text to write.
        pattern (str): The pattern.
        color (str, optional): The ANSI escape code. Defaults to AnsiColours.RED.
        end (str, optional): The line terminating character. Defaults to '\n'.
    """
    text = text.replace(pattern, f'{color}{pattern}{AnsiColours.RESET}')
    print(text, end=end)
