"""
A module containing utility functions for reading and writing GeoTiff files
"""


import os
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
import pandas as pd
import numpy as np
import sqlite3


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

    # Convert the dataframe to a numpy array
    data = data.to_numpy()

    # Write the data to a .tif file
    with rasterio.open(file, "w", **metadata) as dataset:
        dataset.write(data, 1)


class GeoDB:
    """
    A database for storing GeoTiff files in a database.
    """

    def __init__(self, file: str):
        """
        Create a new GeoDB object.

        Args:
            file (str): The path to the database file.
        """

        # Create the database file if it does not exist
        if not os.path.isfile(file):
            with open(file, "w") as f:
                pass

        # Connect to the database
        self.conn = sqlite3.connect(file)

        self.conn.enable_load_extension(True)
        self.conn.load_extension("mod_spatialite")

        # Create the table if it does not exist
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS geotiffs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, geom BLOB, meta BLOB)
            """
        )

        self.conn.commit()

    def addGeoTiff(self, name: str, file: str):
        """
        Add a GeoTiff file to the database.

        Args:
            name (str): The name of the GeoTiff file.
            file (str): The path to the GeoTiff file.

        Raises:
            ValueError: If the file does not exist.
        """

        with rasterio.open(file) as dataset:
            data = dataset.read(1)
            meta = dict(dataset.meta)

        # Convert the data to a blob
        data = data.tobytes()
        meta = str(meta).encode("utf-8")

        self.conn.execute(
            """
            INSERT INTO geotiffs (name, geom, meta) VALUES (?, ?, ?)
            """,
            (name, data, meta)
        )

        self.conn.commit()

    def getGeoTiff(self, name: str):
        """
        Get a GeoTiff file from the database.

        Args:
            name (str): The name of the GeoTiff file.
        """

        data = self.conn.execute(
            """
            SELECT geom, meta FROM geotiffs WHERE name = ?
            """,
            (name,)
        ).fetchone()

        if data is None:
            return None

        # Reconstruct the data
        data_buffer = np.frombuffer(data[0], dtype=np.uint8)
        meta = eval(data[1].decode("utf-8"))

        # Open the raster dataset
        memfile = rasterio.io.MemoryFile(data_buffer.all())
        dataset = memfile.open(driver="GTiff", width=meta["width"], height=meta["height"],
                               count=meta["count"], dtype=meta["dtype"], transform=meta["transform"])

        # Read the raster data
        data = dataset.read(1)

        # Close the dataset and memory file
        dataset.close()
        memfile.close()

        return (meta, data)

    def close(self):
        """
        Close the database connection.
        """

        self.conn.close()


if __name__ == "__main__":
    print("Testing GeoTiff.py")
    import matplotlib.pyplot as plt
    original = plt.imread("./data/classification_5m.tif")
    original = original[:, :, 0]

    db = GeoDB("./data/test.db")

    # add classification_5m.tif to the database
    db.addGeoTiff("classification_5m.tif", "./data/classification_5m.tif")

    # get classification_5m.tif from the database
    meta, data = db.getGeoTiff("classification_5m.tif")

    # close the database
    db.close()

    # plot the original and the data from the database
    # and the conmarison image
    comp = np.isclose(original, data, equal_nan=True)
    plt.subplot(1, 3, 1)
    plt.imshow(original)
    plt.title("Original")
    plt.subplot(1, 3, 2)
    plt.imshow(data)
    plt.title("From Database")
    plt.subplot(1, 3, 3)
    plt.imshow(comp, cmap="gray")
    plt.title("Comparison")
    plt.show()
