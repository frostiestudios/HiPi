from enum import Enum
from typing import Optional
from functools import partial


class Attributes(str, Enum):
    RESET = "\N{ESC}[0m"
    BOLD = "\N{ESC}[1m"
    FAINT = "\N{ESC}[2m"
    UNDERLINE = "\N{ESC}[4m"
    BLINK = "\N{ESC}[5m"

    @classmethod
    def as_format(cls):
        keys = [e.name.lower() for e in cls]
        values = [e.value for e in cls]
        keyvals = zip(keys, values)
        return {k: v for k, v in keyvals}




class Color(int, Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96

    @classmethod
    def as_format(cls):
        keys = [e.name.lower() for e in cls]
        values = [e.default() for e in cls]
        bg_keys = [e.name.lower()+"_bg" for e in cls]
        bg_values = [e.background() for e in cls]
        data = {k:v for k, v in  zip(keys, values)}
        data.update({k:v for k, v in  zip(bg_keys, bg_values)})
        return data

    def default(self) -> str:
        return f"\N{ESC}[{self.value}m"

    def background(self) -> str:
        bg = self.value + 10
        return f"\N{ESC}[{bg}m"


def _color(color: Color, s: str, bg=False) -> str:
    if bg:
        r = color.background() + s
    else:
        r = color.default() + s
    if not r.endswith(Attributes.RESET):
        r += Attributes.RESET
    return r

def _attr(a: Optional[str] = None, s: Optional[str] = None) -> str:
    if a is None or s is None:
        return Attributes.RESET
    r = a + s
    if not r.endswith(Attributes.RESET):
        r += Attributes.RESET
    return r

black = partial(_color, Color.BLACK)
red = partial(_color, Color.RED)
green = partial(_color, Color.GREEN)
yellow = partial(_color, Color.YELLOW)
blue = partial(_color, Color.BLUE)
magenta = partial(_color, Color.MAGENTA)
cyan = partial(_color, Color.CYAN)
white = partial(_color, Color.WHITE)

bright_red = partial(_color, Color.BRIGHT_RED)
bright_green = partial(_color, Color.BRIGHT_GREEN)
bright_yellow = partial(_color, Color.BRIGHT_YELLOW)
bright_blue = partial(_color, Color.BRIGHT_BLUE)
bright_magenta = partial(_color, Color.BRIGHT_MAGENTA)
bright_cyan = partial(_color, Color.BRIGHT_CYAN)

reset = partial(_attr, None, None)
bold = partial(_attr, Attributes.BOLD)
blink = partial(_attr, Attributes.BLINK)
underline = partial(_attr, Attributes.UNDERLINE)


def create_formatter(fmt: str):
    def _formatter(*args, **kwargs):
        return fmt.format(
            *args,
            **Color.as_format(),
            **Attributes.as_format(),
            **kwargs
        )
    return _formatter


