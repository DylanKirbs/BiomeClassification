import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import concurrent.futures
import matplotlib.pyplot as plt
from utilities.constants import KOPPEN_DICT
from data.GeoTif import readGeoData, writeGeoData
from data.WCDownloader import downloadFileList, RESOLUTIONS


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

    # Validate the resolution
    if resolution not in RESOLUTIONS:
        raise ValueError(
            f"Invalid resolution: {resolution}.\nValid resolutions are: {RESOLUTIONS}")

    downloadFileList(REQUIRED_VARS, resolution, dataPath)

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
    plt.imshow(classification)
    plt.savefig(f"./classification_{resolution}.png")
    plt.show()
