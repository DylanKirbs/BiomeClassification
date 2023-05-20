import matplotlib.colors as colors

KOPPEN_DICT = {
    "Af": 1,
    "Am": 2,
    "Aw": 3,
    "BWh": 4,
    "BWk": 5,
    "BSh": 6,
    "BSk": 7,
    "Csa": 8,
    "Csb": 9,
    "Csc": 10,
    "Cwa": 11,
    "Cwb": 12,
    "Cwc": 13,
    "Cfa": 14,
    "Cfb": 15,
    "Cfc": 16,
    "Dsa": 17,
    "Dsb": 18,
    "Dsc": 19,
    "Dsd": 20,
    "Dwa": 21,
    "Dwb": 22,
    "Dwc": 23,
    "Dwd": 24,
    "Dfa": 25,
    "Dfb": 26,
    "Dfc": 27,
    "Dfd": 28,
    "ET": 29,
    "EF": 30
}
"""
The dictionary of Koeppen-Geiger climate classification codes.

The keys are the Koeppen-Geiger climate classification codes, and the values
are the corresponding integer codes. (1-30)

Eg:
    >>> KOPPEN_DICT["Af"] # returns 1

It is recommended to use: `KOPPEN_DICT.get("Af", 0)` instead incase an invalid key is passed.    
"""

INVERSE_KOPPEN_DICT = dict((v, k) for k, v in KOPPEN_DICT.items())
"""
The inverse of the Koeppen-Geiger climate classification dictionary.

The keys are the integer codes, and the values are the corresponding
Koeppen-Geiger climate classification codes.

Eg:
    >>> INVERSE_KOPPEN_DICT[1] # returns "Af"
    
It is recommended to use: `INVERSE_KOPPEN_DICT.get(1, "NA")` instead incase an invalid key is passed.
"""

CLASSIFICATION_COLORS = [
    '#FFFFFF',
    '#0000FE',
    '#0077FF',
    '#46A9FA',
    '#FE0000',
    '#FE9695',
    '#F5A301',
    '#FFDB63',
    '#ffff00',
    '#c6c700',
    '#969600',
    '#96ff96',
    '#63c764',
    '#329633',
    '#c6ff4e',
    '#66ff33',
    '#33c701',
    '#ff00fe',
    '#c600c7',
    '#963295',
    '#966495',
    '#abb1ff',
    '#5a77db',
    '#4c51b5',
    '#320087',
    '#00ffff',
    '#38c7ff',
    '#007e7d',
    '#00455e',
    '#b2b2b2',
    '#686868'
]
"""
The list of colors used to represent the Koeppen-Geiger climate classification.

The colors are stored as hex values.

The values correspond to the Koeppen-Geiger climate classification integer codes from the `KOPPEN_DICT` dictionary.
Value 0 is reserved for the "NA" classification, this is the default color for the map.
"""

CLASSIFICATION_CMAP = colors.ListedColormap(
    [colors.hex2color(hex_value)for hex_value in CLASSIFICATION_COLORS]
)
"""
Matplotlib CMAP of the classification colors
"""
