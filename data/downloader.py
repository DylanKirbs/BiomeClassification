"""
The install script for the data package.
"""

import urllib.request
import zipfile
import io

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

    url = getFullUrl(variable, res)

    with urllib.request.urlopen(url) as response:
        data = response.read()

    # save the data to a zip file
    with open(f'{path}/{variable}_{res}.zip', 'wb') as f:
        f.write(data)

    return


if __name__ == "__main__":

    from tqdm import tqdm

    dataDir = "./data"
    variables = ['average temperature', 'precipitation']
    resolutions = ['5 minutes']

    print(f"Data directory set to: {dataDir}")
    print("Downloading data for the following variables:")
    print(variables)
    print("At the following resolutions:")
    print(resolutions)

    for variable, res in tqdm(zip(variables, resolutions), desc="Downloading data"):
        downloadData(VARIABLES[variable], RESOLUTIONS[res], dataDir)

    for variable, res in tqdm(zip(variables, resolutions), desc="Extracting data"):
        with zipfile.ZipFile(f'{dataDir}/{variable}_{res}.zip', 'r') as zip_ref:
            zip_ref.extractall(dataDir)
