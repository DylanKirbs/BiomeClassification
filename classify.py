import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
from data.constants import RESOLUTIONS
from itertools import product as cartesian_product
from data.downloader import downloadData, extractData
from data.dataUtils import readGeoData, getFilePath, writeGeoData, plotHeatmap
from constants import KOPPEN_DICT, CLASSIFICATION_CMAP
import concurrent.futures


def downloadRequiredFiles(files: list[str], resolution, dataPath: str = "./data") -> None:
    """
    Checks for and downloads any necessary files from the list.

    The file list should simply contain the WC variable names.
    For example:
        `files = ['tavg','prec']`

    Args:
        files (list[str]): The list of files.
        resolution (str): The resolution of the files.
        dataPath (str, optional): The data directory. Defaults to "./data".
    """

    print("Downloading files.")
    for file in files:
        if not os.path.isfile(f"{dataPath}/{file}_{resolution}.zip"):
            print(f"Data for {file} at {resolution} resolution not found.")
            print("Downloading data...")
            downloadData(resolution, file, dataPath)
            print("Extracting data...")
            extractData(resolution, file, dataPath)
        else:
            print(
                f"Using existing data for {file} at {resolution} resolution.")


def readGeodataFiles(dataNames: list[tuple[str, str]], resolution: str, dataPath: str = "./data"):
    """
    Read the Geodata files into a dictionary.

    The data names should be a list of tuples, each with the variable and month.
    For example:
        `('tavg', '01')` for the average temperature in January

    The returned geodata dictionary will be indexed with the variable and month as follows.
        `geodata['tavg_01']` will return the tuple of the metadata and data.

    Args:
        dataNames (list[tuple[str, str]]): The geodata file names as tuples of variable and month.
        resolution (str): The resolution of the files.
        dataPath (str, optional): The data directory. Defaults to "./data".

    Returns:
        dict[str, tuple]: The geodata dictionary.
    """

    geoData = {}
    for var, month in tqdm(dataNames, desc="Reading files", unit="files"):

        # Get the path
        filePath = getFilePath(dataPath, var, resolution, month)

        # Read the data into the dict
        geoData[f"{var}_{month}"] = readGeoData(filePath)

    return geoData


def classifyGeoData(data: pd.DataFrame, chunks_size: int = 100, thread_count: int = 2):

    chunk_size = data.shape[0] // chunks_size

    chunks = [data.iloc[i:i+chunk_size]
              for i in range(0, data.shape[0], chunk_size)]

    """# TODO may need to fix the aggregation and return corrected data
    # Create a ThreadPoolExecutor with a specified number of threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:

        # Submit the processing of each chunk to the executor
        futures = [executor.submit(computeChunk, chunk)
                   for chunk in chunks]

        # Iterate over the completed futures to retrieve the results
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing chunks"):
            result = future.result()  # Get the processed chunk
            # Optionally, you can aggregate or process the results here"""

    for chunk in tqdm(chunks, desc="Computing chunks", unit="chunks"):

        # Cols 0:2 are lat, lon and class
        # Cols 3:15 are tavg_01:12
        # Cols 16:28 are prec_01:12
        computeChunk(chunk)

        # print(classification.iloc[i:i+chunk_size]['classification'])

    return data


def computeChunk(chunk):
    """
    Processes a single chunk of the dataframe.

    It is assumed that each row of the chunk follows this format:
    ['lat', 'lon', 'classification', 'tavg01' ... 'tavg12', 'prec01' ... 'prec12']

    The chunk will be updated to contain the Koppen-Geiger classification.

    Args:
        chunk (dataframe): The chunk to process

    Returns:
        dataframe: The processed chunk
    """
    chunk.loc['classification'] = chunk.apply(
        lambda row: koppen_beck(row[3:15], row[16:28], row[0] > 0), axis=1)
    return chunk


def computeRegionalClassification(resolution: str, dataPath: str = "./data"):
    """
    Computes the regional classification of a given resolution.

    The format will be the same as the WorldClim data, except that it will store the classification as an integer.

    If the `tavg` and `prec` data for the given resolution are not in the data path, it will be downloaded.

    The resolution must be one of the following:

    | Resolution | Description |
    | ---------- | ----------- |
    | 2.5m       | 2.5 arc-minute resolution |
    | 5m         | 5 arc-minute resolution   |
    | 10m        | 10 arc-minute resolution  |
    | 30m        | 30 arc-minute resolution  |

    Args:
        resolution (str): The resolution of the classification to compute.

    Raises:
        ValueError: If the resolution is invalid.

    Returns:
        Tuple: The metadata of the classification and the classification itself.
    """

    # Initialise the Constants
    REQUIRED_FILES = ["tavg", "prec"]
    CHUNKS = 100
    NUM_THREADS = 3
    MONTHS = ["01", "02", "03", "04", "05",
              "06", "07", "08", "09", "10", "11", "12"]

    # Validate the resolution
    if resolution not in RESOLUTIONS.values():
        raise ValueError(
            f"Invalid resolution: {resolution}.\nValid resolutions are: {RESOLUTIONS.values()}")

    downloadRequiredFiles(REQUIRED_FILES, resolution, dataPath)

    dataFiles = list(x for x in cartesian_product(REQUIRED_FILES, MONTHS))
    geoData = readGeodataFiles(dataFiles, resolution, dataPath)

    colNames = list(f"{var}_{month}" for var, month in dataFiles)

    # The classification will be a df with a colum for lat, lon, tavg, prec, and classification
    data = pd.DataFrame(
        columns=["lat", "lon", "classification"].extend(colNames))

    meta, base = geoData[colNames[0]]
    data["lat"] = np.repeat(base.index.values, base.shape[1])
    data["lon"] = np.tile(base.columns.values, base.shape[0])
    data["classification"] = 0  # classification values

    # Thus we need to flatten the tavg and prec data into columns
    for col in tqdm(colNames, desc="Flattening data", unit="files"):
        data[col] = geoData[col][1].values.flatten()

    classification = classifyGeoData(data, CHUNKS, NUM_THREADS)

    # Convert the classification back to a raster
    print("Converting classification to raster...")
    classification = classification.pivot(
        index="lat", columns="lon", values="classification")

    # TODO: Figure out why we need to reverse the latitudes
    # We may be able to correct this when we create the lat column in the first place
    classification = classification.iloc[::-1]

    print("Classification Complete.")

    return (meta, classification)


def koppen_beck(temp: float, prec: float, north_hemisphere: bool) -> int:

    temps = np.array(temp)
    precs = np.array(prec)

    # If any of the values are NaN, return ""
    if np.isnan(temps).any() or np.isnan(precs).any():
        return 0

    # pre-calculations
    m_a_t = temps.sum() / 12
    m_a_p = precs.sum() / 12
    p_min = precs.min()
    t_min = temps.min()
    t_max = temps.max()

    t_above_10 = 0
    for temp in temps:
        if temp > 10:
            t_above_10 += 1

    if not north_hemisphere:  # southern hemisphere, winter from the 3rd to 9th month
        if precs[3:9].sum() > 0.7 * m_a_p:
            p_thresh = 2 * m_a_t
        elif np.concatenate((precs[0:3], precs[9:12])).sum() > 0.7 * m_a_p:  # summer
            p_thresh = 2 * m_a_t + 28
        else:
            p_thresh = 2 * m_a_t + 14
        p_w_min = precs[3:9].min()
        p_w_max = precs[3:9].max()
        p_s_min = np.concatenate(
            (precs[0:3], precs[9:12])).min()
        p_s_max = np.concatenate(
            (precs[0:3], precs[9:12])).max()

    else:  # northern hemisphere, summer from the 3rd to 9th month
        he = "N"
        if np.concatenate((precs[0:3], precs[9:12])).sum() > 0.7 * m_a_p:
            p_thresh = 2 * m_a_t
        elif precs[3:9].sum() > 0.7 * m_a_p:  # summer
            p_thresh = 2 * m_a_t + 28
        else:
            p_thresh = 2 * m_a_t + 14
        p_s_min = precs[3:9].min()
        p_s_max = precs[3:9].max()
        p_w_min = np.concatenate(
            (precs[0:3], precs[9:12])).min()
        p_w_max = np.concatenate(
            (precs[0:3], precs[9:12])).max()

    # classification conditionals
    koppenClass = ""
    if m_a_p < 10 * p_thresh:
        koppenClass = "B"
        if m_a_p < 5 * p_thresh:
            koppenClass = koppenClass + "W"
        else:
            koppenClass = koppenClass + "S"
        if m_a_t >= 18:
            koppenClass = koppenClass + "h"
        else:
            koppenClass = koppenClass + "k"
    elif t_min >= 18:
        koppenClass = "A"
        if p_min >= 60:
            koppenClass = koppenClass + "f"
        else:
            if p_min >= 100 - m_a_p / 25:
                koppenClass = koppenClass + "m"
            else:
                koppenClass = koppenClass + "w"
    elif t_max > 10 and 0 < t_min < 18:
        koppenClass = "C"
        if p_s_min < 40 and p_s_min < p_w_max / 3:
            koppenClass = koppenClass + "s"
        elif p_w_min < p_s_max / 10:
            koppenClass = koppenClass + "w"
        else:
            koppenClass = koppenClass + "f"
        if t_max >= 22:
            koppenClass = koppenClass + "a"
        else:
            if t_above_10 >= 4:
                koppenClass = koppenClass + "b"
            elif 1 <= t_above_10 < 4:
                koppenClass = koppenClass + "c"
    elif t_max > 10 and t_min <= 0:
        koppenClass = "D"
        if p_s_min < 40 and p_s_min < p_w_max / 3:
            koppenClass = koppenClass + "s"
        elif p_w_min < p_s_max / 10:
            koppenClass = koppenClass + "w"
        else:
            koppenClass = koppenClass + "f"
        if t_max >= 22:
            koppenClass = koppenClass + "a"
        else:
            if t_above_10 >= 4:
                koppenClass = koppenClass + "b"
            elif t_min < -38:
                koppenClass = koppenClass + "d"
            else:
                koppenClass = koppenClass + "c"
    elif t_max <= 10:
        koppenClass = "E"
        if t_max > 0:
            koppenClass = koppenClass + "T"
        else:
            koppenClass = koppenClass + "F"

    # print(temps, precs, koppenClass)

    return KOPPEN_DICT.get(koppenClass, 0)


if __name__ == "__main__":

    recompute = True
    resolution = "5m"

    if recompute:
        meta, classification = computeRegionalClassification(resolution)

        print("Writing GeoTIFF...")
        try:
            writeGeoData(classification, meta,
                         f"./data/classification_{resolution}.tif")
        except Exception as e:
            print(e)

    print("Reading GeoTIFF...")
    meta, classification = readGeoData(
        f"./data/classification_{resolution}.tif")

    print("Plotting...")
    # plot the data using the colors from `CLASSIFICATION_COLORS`
    plotHeatmap(plt, sns, classification,
                "Classification", cmap=CLASSIFICATION_CMAP)
    plt.show()
