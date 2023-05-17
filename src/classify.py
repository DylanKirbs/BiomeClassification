"""
Performs the classification of the biome based on the Naive Bayes Classification.
"""

from numpy import sqrt, exp, pi


def normalDistribution(x: float, mean: float, var: float): return 1.0 / \
    (sqrt(2*pi*var))*exp(-pow((x-mean), 2)/(2.0*var))
