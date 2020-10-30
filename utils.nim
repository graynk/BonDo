from random import rand
from strutils import repeat
from unicode import toLower, runeSubStr

proc generateOh*(vowels: string): string =
    return vowels.runeSubStr(0, 1).toLower().repeat(rand(1..8)) &
        "х".repeat(rand(1..8)) &
        ".".repeat(rand(3))