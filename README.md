# Climate Classification

- [Climate Classification](#climate-classification)
- [IMPORTANT NOTICE](#important-notice)
  - [Introduction](#introduction)
  - [The Classifications Methods](#the-classifications-methods)
    - [Koppen-Geiger Climate Classification](#koppen-geiger-climate-classification)
  - [The Data](#the-data)
  - [License](#license)
  - [Contributing](#contributing)


# IMPORTANT NOTICE

The project is currently in a very early stage of development. The code is not yet ready for use. The README is also not yet complete.
Contributions are welcome, but please read the [CONTRIBUTING.md](CONTRIBUTING.md) file before submitting a pull request.

**It is not working at the moment**


## Introduction

This project aims to predict the likelihood of an observed variable being in a certain category (biome) based on the values of the observed variables.

We aim to classify the biome of a given location based on the following observed variables:

- Bioclimactic Variables
- Temperature
- Precipitation

And in future we hope to include the following observed variables:

- Elevation
- Soil Type
- Vegetation Type
- Animal Type

More info about the data can be found [here](#the-data).

![The Classification image](classification.png)

## The Classifications Methods

Predicting the biome of a given location based on the observed variables is a classification problem. There are many classification methods available, but we will focus on the following:

- Koppen-Geiger Climate Classification


### Koppen-Geiger Climate Classification

The Koppen-Geiger climate classification is designed specifically for climate classification. It divides the climate into 5 main categories, which are then further divided into subcategories. The main categories are as follows:

- A: Tropical
- B: Dry
- C: Temperate
- D: Continental
- E: Polar


More information on the Koppen-Geiger climate classification can be found [here](https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification).

A heavily modified version of [salvah22](https://github.com/salvah22/koppenclassification)'s python implementation is used.

The Koppen-Geiger classification will then be applied to the data to create a training set for the Naive Bayes classifier.

## The Data

The data used in this project is from the [WorldClim](https://www.worldclim.org/) database. The data is available for download [here](https://www.worldclim.org/data/worldclim21.html).

The 5 minute resolution data is used for this project.

The downloader script will download and extract the `.tif` files for the following variables by default:

- Bioclimactic Variables
- Average Temperature
- Precipitation

The data is averaged over the years 1970-2000 to create a single `.tif` file for each variable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct, and the process for submitting pull requests.