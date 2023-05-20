"""
The install script for the data package.
"""

import os
import requests
import zipfile
from .constants import BASE_URL, VARIABLES, RESOLUTIONS, AnsiColours


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


if __name__ == "__main__":

    from tqdm import tqdm
    from itertools import product as cartesianProduct

    dataDir = "./data"
    variables = ['average temperature', 'precipitation']
    resolutions = ['5 minutes']
    downloadList = [(VARIABLES[variable], RESOLUTIONS[res])
                    for variable, res in cartesianProduct(variables, resolutions)]

    print(f"{AnsiColours.Green}Data directory set to: {AnsiColours.Blue}{dataDir}{AnsiColours.Reset}")
    print(f"Downloading data for {variables}")
    print(f"At {resolutions} resolutions")

    try:
        for variable, res in tqdm(downloadList, desc="Downloading data", colour="green", unit="file"):
            downloadData(variable, res, dataDir)

        for variable, res in tqdm(downloadList, desc="Extracting data", colour="green", unit="file"):
            extractData(variable, res, dataDir)

    except Exception as e:
        print(f"{AnsiColours.Red}Fatal Exception! Download Failed{AnsiColours.Reset}")
        print(f"{AnsiColours.Red}Error: {e}{AnsiColours.Reset}")

    print(f"{AnsiColours.Green}Done!{AnsiColours.Reset}")
