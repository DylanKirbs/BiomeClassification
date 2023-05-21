"""
The install script for the data package.
"""

if __name__ == "__main__":
    print("Please import the module.")
    exit(0)

import os
import requests
import zipfile


WC_VERSION = "2.1"
BASE_URL = f"https://biogeo.ucdavis.edu/data/worldclim/v{WC_VERSION}/base/wc{WC_VERSION}"
"""
The base url for the WorldClim data.
"""

VARIABLES = [
    "tmin",
    "tmax",
    "tavg",
    "prec",
    "srad",
    "wind",
    "vapr",
    "bio",
    "elev"
]
"""
The variables available for download are:
    - minimum temperature (C)
    - maximum temperature (C)
    - average temperature (C)
    - precipitation (mm)
    - solar radiation (W/m^2)
    - wind speed (m/s)
    - vapor pressure (hPa)
    - bioclimactic variables (19 variables)
    - elevation (m)
"""

RESOLUTIONS = [
    "30s",
    "2.5m",
    "5m",
    "10m",
]
"""
The resolutions available for download are:
    - 30 arc-seconds
    - 2.5 arc-minutes
    - 5 arc-minutes
    - 10 arc-minutes   
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


def downloadData(variable: str, res: str = "5m", path: str = "./data") -> None:
    """
    Downloads the data from the WorldClim website.

    The data is saved as a zip file named "{variable}_{res}.zip" in the path.

    Args:
        variable (str): The variable of the data.
        res (str, optional): The resolution on the variable. Defaults to "5m".
        path (str, optional): The download path. Defaults to "./data".
    """

    # Check if a file with the same name already exists
    downloadPath = f'{path}/{variable}_{res}.zip'
    if os.path.exists(downloadPath):
        print(f"File {downloadPath} already exists. Skipping download.")
        return None

    url = getFullUrl(variable, res)

    response = requests.get(url)
    response.raise_for_status()

    # save the data to a zip file
    with open(downloadPath, 'wb') as f:
        f.write(response.content)

    return None


def extractData(variable: str, res: str = "5m", dataDir: str = "./data"):
    """
    Extracts the data from the zip file into a folder.

    Args:
        variable (str): The variable of the data.
        res (str, optional): The resolution. Defaults to "5m".
        dataDir (str, optional): The data directory. Defaults to "./data".
    """
    fileName = f'{variable}_{res}'
    with zipfile.ZipFile(f'{dataDir}/{fileName}.zip', 'r') as zip_ref:
        zip_ref.extractall(f"{dataDir}/{fileName}")
