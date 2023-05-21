import matplotlib.colors as colors

KOPPEN_DICT = {
    "": 0,
    "Af": 1,
    "Am": 2,
    "Aw": 3,
    "As": 4,
    "BWh": 5,
    "BWk": 6,
    "BSh": 7,
    "BSk": 8,
    "Csa": 9,
    "Csb": 10,
    "Csc": 11,
    "Cwa": 12,
    "Cwb": 13,
    "Cwc": 14,
    "Cfa": 15,
    "Cfb": 16,
    "Cfc": 17,
    "Dsa": 18,
    "Dsb": 19,
    "Dsc": 20,
    "Dsd": 21,
    "Dwa": 22,
    "Dwb": 23,
    "Dwc": 24,
    "Dwd": 25,
    "Dfa": 26,
    "Dfb": 27,
    "Dfc": 28,
    "Dfd": 29,
    "ET": 30,
    "EF": 31
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
The inverse of the Koppen-Geiger climate classification dictionary.

The keys are the integer codes, and the values are the corresponding
Koppen-Geiger climate classification codes.

Eg:
    >>> INVERSE_KOPPEN_DICT[1] # returns "Af"
    
It is recommended to use: `INVERSE_KOPPEN_DICT.get(1, "NA")` instead incase an invalid key is passed.
"""

CLASSIFICATION_COLORS = [
    '#FFFFFF',
    '#0000FE',
    '#0077FF',
    '#46A9FA',
    '#A9F5FF',
    '#F00000',
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
The list of colors used to represent the Koppen-Geiger climate classification.

The colors are stored as hex values.

The values correspond to the Koppen-Geiger climate classification integer codes from the `KOPPEN_DICT` dictionary.
Value 0 is reserved for the "NA" or empty classification, this is the default color for the map.
"""

CLASSIFICATION_COLORS_2 = [
    '#FFFFFF',
    '#930101',  # Af
    '#fd0000',  # Am
    '#ffcaca',  # Aw
    '#fd686c',  # As
    '#fccb03',  # BWh
    '#fdfc54',  # BWk
    '#c98a00',  # BSh
    '#cbab54',  # BSk
    '#00fe00',  # Csa
    '#95ff00',  # Csb
    '#cbff00',  # Csc
    '#b46500',  # Cwa
    '#966604',  # Cwb
    '#5e4001',  # Cwc
    '#003000',  # Cfa
    '#015001',  # Cfb
    '#007700',  # Cfc
    '#fe6cfd',  # Dsa
    '#f8b9f7',  # Dsb
    '#e6cafd',  # Dsc
    '#cacccb',  # Dsd
    '#ccb6ff',  # Dwa
    '#997cb2',  # Dwb
    '#8a59b2',  # Dwc
    '#6d23b3',  # Dwd
    '#300030',  # Dfa
    '#650164',  # Dfb
    '#cb00cb',  # Dfc
    '#c71587',  # Dfd
    '#65ffff',  # ET
    '#6396ff',  # EF
]

CLASSIFICATION_CMAP = colors.ListedColormap(
    [colors.hex2color(hex_value)for hex_value in CLASSIFICATION_COLORS]
)  # type: ignore
"""
Matplotlib CMAP of the classification colors
"""

CLASSIFICATION_NAMES = list(KOPPEN_DICT.keys())
"""
The list of Koppen-Geiger climate classification names.

Index 0 is reserved for the "NA" or empty classification.
"""
