"""
Constants for the WorldClim data.
"""

from dataclasses import dataclass

WC_VERSION = "2.1"
BASE_URL = f"https://biogeo.ucdavis.edu/data/worldclim/v{WC_VERSION}/base/wc{WC_VERSION}"
"""
The base url for the WorldClim data.
"""

VARIABLES = {
    "minimum temperature": "tmin",
    "maximum temperature": "tmax",
    "average temperature": "tavg",
    "precipitation": "prec",
    "solar radiation": "srad",
    "wind speed": "wind",
    "vapor pressure": "vapr",
}
"""
The variables available for download.

The key is the name of the variable and the value is the code used in the url.

The variables are:
    - minimum temperature (C)
    - maximum temperature (C)
    - average temperature (C)
    - precipitation (mm)
    - solar radiation (W/m^2)
    - wind speed (m/s)
    - vapor pressure (hPa)
"""

RESOLUTIONS = {
    "30 seconds": "30s",
    "2.5 minutes": "2.5m",
    "5 minutes": "5m",
    "10 minutes": "10m",
}
"""
The resolutions available for download.

The key is the name of the resolution and the value is the code used in the url.

The resolutions are:
    - 30 seconds
    - 2.5 minutes
    - 5 minutes
    - 10 minutes   
"""


@dataclass
class AnsiColours:
    Red: str = "\033[91m"
    Green: str = "\033[92m"
    Yellow: str = "\033[93m"
    Blue: str = "\033[94m"
    Magenta: str = "\033[95m"
    Cyan: str = "\033[96m"
    White: str = "\033[97m"
    Reset: str = "\033[0m"


if __name__ == "__main__":
    print(f"{AnsiColours.Red}This is a module. Import it instead.{AnsiColours.Reset}")
