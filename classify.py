import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from data.constants import RESOLUTIONS, AnsiColours
from data.downloader import downloadData, extractData
from data.dataUtils import readGeoData, writeGeoData, plotHeatmap
from constants import KOPPEN_DICT, CLASSIFICATION_CMAP, CLASSIFICATION_NAMES
import concurrent.futures


def cPrint(text: str, colour: str = AnsiColours.WHITE, end: str = "\n") -> None:
    """
    Prints the given text in the given colour.

    Args:
        text (str): The text to print.
        colour (str, optional): The ANSI colour string to print in. Defaults to AnsiColours.WHITE.
        end (str, optional): The end character. Defaults to "\n".
    """

    print(f"{colour}{text}{AnsiColours.RESET}", end=end)


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

    cPrint("Checking for required files.", AnsiColours.BLUE)

    # Check for the directory
    if not os.path.isdir(dataPath):
        cPrint("Creating data directory.", AnsiColours.YELLOW)
        os.makedirs(dataPath)

    # Check for the files
    for file in files:
        if not os.path.isdir(f"{dataPath}/{file}_{resolution}"):
            cPrint(
                f"{file}_{resolution} directory not found. Checking for zip file.", AnsiColours.YELLOW)

            # Check for the zip file
            if not os.path.isfile(f"{dataPath}/{file}_{resolution}.zip"):
                cPrint(
                    f"{file}_{resolution}.zip not found. Downloading.", AnsiColours.YELLOW)
                downloadData(file, resolution, dataPath)
                cPrint(f"{file}_{resolution}.zip downloaded.",
                       AnsiColours.GREEN)

            # Extract the zip file
            extractData(file, resolution, dataPath)
            cPrint(f"{file}_{resolution}.zip extracted.", AnsiColours.GREEN)

        cPrint(f"{file}_{resolution} directory found.", AnsiColours.GREEN)


def readGeodataDirs(dataDirs: list[str], dataPath: str = "./data"):
    """
    Read the Geodata files into a dictionary.

    Args:
        dataDirs (list[str]): The list of data directories.
        dataPath (str, optional): The data directory. Defaults to "./data".

    Returns:
        dict[str, tuple]: The geodata dictionary.
    """

    geoData: dict[str, tuple] = {}
    for dir in tqdm(dataDirs, desc="Retrieving files", unit="directories"):

        # Get the files from the directory
        files = os.listdir(f"{dataPath}/{dir}")
        files = [file for file in files if file.endswith(".tif")]
        files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

        for file in files:
            # Files in the directory are named like wc2.1_5m_bio_1.tif
            # The key is 5m_bio_1
            key = str('_'.join(file.split(".")[-2].split("_")[1:]))
            geoData[key] = readGeoData(f'{dataPath}/{dir}/{file}')

    return geoData


def concurrentClassification(data: pd.DataFrame, num_chunks: int = 100, thread_count: int = 2):
    """
    Classifies the given geodata concurrently.

    TODO: Implement threading

    Args:
        data (pd.DataFrame): The geodata to classify.
        num_chunks (int, optional): Number of chunks. Defaults to 100.
        thread_count (int, optional): Number of threads. Defaults to 2.

    Returns:
        pd.DataFrame: The classified geodata.
    """

    """ # TODO Confirm the new method works before removing this
    chunk_size = data.shape[0] // chunks

    for i in tqdm(range(0, data.shape[0], chunk_size), desc="Computing chunks", unit="chunks"):

        data.loc[i:i+chunk_size,
                 'classification'] = computeChunk(data.loc[i:i+chunk_size, :])

    return data
    """

    chunk_size = data.shape[0] // num_chunks
    chunks = [data.iloc[i:i + chunk_size]
              for i in range(0, data.shape[0], chunk_size)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        classified_chunks = list(executor.map(classify_chunk, chunks))

    # Combine the classified chunks back into a single DataFrame
    classified_data = pd.concat(classified_chunks)

    return classified_data


def computeChunk(chunk):
    """
    Processes a single chunk of the dataframe.

    It is assumed that each row of the chunk follows this format:
    [lat, lon, classification, bio(1-19), tavg(1-12), prec(1-12)]

    The chunk will be updated to contain the Koppen-Geiger classification.

    Args:
        chunk (dataframe): The chunk to process

    Returns:
        dataframe: The processed chunk
    """

    # row[0:2] are lat, lon & classification
    # row[3:21] are bio
    # row[22:34] are tavg
    # row[35:47] are prec

    return chunk.apply(
        lambda row: koppenGeigerClassify(row[3:21], row[22:34], row[35:47], row[0] > 0), axis=1)


def computeRegionalClassification(resolution: str, dataPath: str = "./data"):
    """
    Computes the regional classification of a given resolution.

    The format will be the same as the WorldClim data, except that it will store the classification as an integer.

    If the data for the given resolution is not in the data path, it will automatically be downloaded.

    The data required is:
    - bio


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

    print(
        f"Computing regional classification on {resolution} resolution WorldClim data.")

    # Initialise the Constants
    REQUIRED_VARS = ["bio", "tavg", "prec"]
    CHUNKS = 100
    NUM_THREADS = 3

    # Validate the resolution
    if resolution not in RESOLUTIONS.values():
        raise ValueError(
            f"Invalid resolution: {resolution}.\nValid resolutions are: {RESOLUTIONS.values()}")

    downloadRequiredFiles(REQUIRED_VARS, resolution, dataPath)

    dataDirs = list(f"{var}_{resolution}" for var in REQUIRED_VARS)
    geoData = readGeodataDirs(dataDirs, dataPath)

    # The classification will be a df with a colum for lat, lon, classification and the geoData keys
    data = pd.DataFrame(
        columns=["lat", "lon", "classification"].extend(geoData.keys()))

    meta, base = geoData.get(list(geoData.keys())[0])  # type: ignore
    data["lat"] = np.repeat(base.index.values, base.shape[1])
    data["lon"] = np.tile(base.columns.values, base.shape[0])
    data["classification"] = 0  # classification values

    # Thus we need to flatten the tavg and prec data into columns
    for col in tqdm(geoData.keys(), desc="Flattening data", unit="files"):
        data[col] = geoData[col][1].values.flatten()

    classification = concurrentClassification(data, CHUNKS, NUM_THREADS)

    # Convert the classification back to a raster
    print("Converting classification to raster...")
    classification = classification.pivot(
        index="lat", columns="lon", values="classification")

    # TODO: Figure out why we need to reverse the latitudes
    # We may be able to correct this when we create the lat column in the first place
    classification = classification.iloc[::-1]

    print("Classification Complete.")

    return (meta, classification)


def koppenGeigerClassify(bioVarSeries, tavgSeries, precSeries, north_hemisphere: bool) -> int:
    """
    Classifies a given location based on the Koppen-Geiger climate classification system.

    Required bioclimatic variables:
    - bio1: Annual Mean Temperature
    - bio5: Max Temperature of Warmest Month
    - bio6: Min Temperature of Coldest Month
    - bio10: Mean Temperature of Warmest Quarter
    - bio12: Annual Precipitation
    - bio14: Precipitation of Driest Month


    Args:
        bioVarSeries (pd.Series): The series of bioclimatic variables (1-19).
        tavgSeries (pd.Series): The series of average temperatures from January to December.
        precSereis (pd.Series): The series of precipitation from January to December.
        north_hemisphere (bool): Whether the location is in the northern hemisphere.

    Returns:
        int: The classification of the location.
    """
    m_a_t = bioVarSeries[0]
    m_a_p = bioVarSeries[11] / 12
    p_min = bioVarSeries[13]

    t_max = bioVarSeries[4]
    t_min = bioVarSeries[5]

    precArray = np.array(tavgSeries)
    tempArray = np.array(precSeries)

    t_above_10 = 0
    for temp in tempArray:
        if temp > 10:
            t_above_10 += 1

    if not north_hemisphere:  # southern hemisphere, winter from the 3rd to 9th month
        if precArray[3:9].sum() > 0.7 * m_a_p:
            p_thresh = 2 * m_a_t
        # summer
        elif np.concatenate((precArray[0:3], precArray[9:12])).sum() > 0.7 * m_a_p:
            p_thresh = 2 * m_a_t + 28
        else:
            p_thresh = 2 * m_a_t + 14
        p_w_min = precArray[3:9].min()
        p_w_max = precArray[3:9].max()
        p_s_min = np.concatenate(
            (precArray[0:3], precArray[9:12])).min()
        p_s_max = np.concatenate(
            (precArray[0:3], precArray[9:12])).max()

    else:  # northern hemisphere, summer from the 3rd to 9th month
        he = "N"
        if np.concatenate((precArray[0:3], precArray[9:12])).sum() > 0.7 * m_a_p:
            p_thresh = 2 * m_a_t
        elif precArray[3:9].sum() > 0.7 * m_a_p:  # summer
            p_thresh = 2 * m_a_t + 28
        else:
            p_thresh = 2 * m_a_t + 14
        p_s_min = precArray[3:9].min()
        p_s_max = precArray[3:9].max()
        p_w_min = np.concatenate(
            (precArray[0:3], precArray[9:12])).min()
        p_w_max = np.concatenate(
            (precArray[0:3], precArray[9:12])).max()

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

    recompute = False
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
    plotHeatmap(plt, classification,
                "Classification", cmap=CLASSIFICATION_CMAP, tick_labels=CLASSIFICATION_NAMES)  # type: ignore
    plt.savefig(f"./classification_{resolution}.png")
    plt.show()
