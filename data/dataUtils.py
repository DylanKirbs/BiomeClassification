"""
A module containing utility functions for reading and writing data.
"""

import os
import rasterio
import pandas as pd
import numpy as np
from .constants import WC_VERSION


def readGeoData(file: str):
    """
    Read a .tif file into a dataframe.

    The metadata is stored in a dictionary and the data is stored in a dataframe.

    Args:
        file (str): The path to the .tif file

    Raises:
        ValueError: If the file does not exist.

    Returns:
        Tuple: A tuple containing the metadata and the data as a dataframe.
    """

    # validate the file
    if not os.path.isfile(file):
        raise ValueError("File does not exist: " + file)

    # Open the .tif file
    with rasterio.open(file) as dataset:
        metadata = dict(dataset.meta)
        data = dataset.read(1)

    # Convert the data to a dataframe and account for the no data value
    data = pd.DataFrame(data)
    data = data.replace(dataset.nodata, np.nan)

    # Get the coordinates using the transform
    transform = dataset.transform
    x = np.arange(data.shape[1]) * transform.a + transform.xoff
    y = np.arange(data.shape[0]) * transform.e + transform.yoff

    # Round the coordinates to 2 decimal places
    x = np.round(x, 2)
    y = np.round(y, 2)

    # Add the coordinates to the dataframe
    data.columns = x
    data.index = y

    # Return the dataframe
    return (metadata, data)


def writeGeoData(data, metadata, file: str):
    """
    Save the dataframe to a .tif file.

    Args:
        data (DataFrame): The dataframe to save.
        metadata (dict): The metadata of the dataframe.
        file (str): The file path to save it to.
    """

    # Convert the dataframe to a numpy array and account for the no data value
    data = data.to_numpy()

    # Write the data to a .tif file
    with rasterio.open(file, "w", **metadata) as dataset:
        dataset.write(data, 1)


def plotHeatmap(plt, sns, data, title, cmap="coolwarm"):
    """
    Plot a heatmap of the data.

    Args:
        data (DataFrame): The data to plot.
        title (str): The title of the plot.
        unit (str): The unit of the data (eg: "°C")
    """
    dims = data.shape[::-1]

    dims = (dims[0] / max(dims), dims[1] / max(dims))
    dims = (dims[0] * 20, dims[1] * 20)

    # Set up the figure
    plt.figure(figsize=dims)
    plt.title(title)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    sns.heatmap(data, annot=False, cmap=cmap, cbar=True)
