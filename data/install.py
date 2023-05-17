"""
The install script for the data package.
"""

WC_VERSION = "2.1"
BASE_URL = f"https://biogeo.ucdavis.edu/data/worldclim/v{WC_VERSION}/base/wc{WC_VERSION}"

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


def getFullUrl(variable: str, res: str = "5m") -> str:
    """
    Generates the full url for the WoldClim data from the variable.

    Eg: url("tavg") -> "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/"wc2.1_5m_tavg.zip""

    Args:
        variable (str): The type and resolution of the data.
        res (str, optional): The resolution of the data. Defaults to "5m".


    Returns:
        str: The full url for the data.
    """
    global BASE_URL

    url = f'{BASE_URL}_{res}_{variable}.zip'

    return url
