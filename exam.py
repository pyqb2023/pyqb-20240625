# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Programming in Python
# ## Exam: June 25, 2024
#
# You can solve the exercises below by using standard Python 3.11 libraries, NumPy, Matplotlib, Pandas, PyMC3.
# You can browse the documentation: [Python](https://docs.python.org/3.11/), [NumPy](https://numpy.org/doc/1.26/index.html), [Matplotlib](https://matplotlib.org/3.8.2/users/index.html), [Pandas](https://pandas.pydata.org/pandas-docs/version/2.1/index.html), [PyMC](https://www.pymc.io/projects/docs/en/v5.10.3/api.html).
# You can also look at the [slides of the course](https://homes.di.unimi.it/monga/lucidi2324/pyqb00.pdf) or your code on [GitHub](https://github.com).
#
# **It is forbidden to communicate with others.**
#
#
#
#

import numpy as np
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pymc as pm   # type: ignore
import arviz as az   # type: ignore

# ### Exercise 1 (max 2 points)
#
# The file [bird_data.csv](./bird_data.csv) (source: https://doi.org/10.13130/RD_UNIMI/5ZXGIV) contains data about a population of butterflies.
#
# Load the data in a pandas dataframe; be sure the columns `organic` and `alternate_management` have the `bool` dtype; use the column `transect_ID` as the index.

# +
data = pd.read_csv('bird_data.csv', index_col='transect_ID')
for k in ['organic', 'alternate_management']:
    data[k] = data[k].astype(bool)

data.head()
# -

# ### Exercise 2 (max 5 points)
#
# Make a figure with a scatterplot of the `X` and `Y` values; each point should be colored according its `subarea`. Use a proper title and a legend (Hint: https://matplotlib.org/3.8.2according/gallery/lines_bars_and_markers/scatter_with_legend.html).
#

# +
fig, ax = plt.subplots()


s = ax.scatter(data['X'], data['Y'], c=data['subarea'].map({'N': 0, 'E': 1, 'S': 2, 'W': 3}))
ax.set_title('Bird points by subarea')
_ = ax.legend(s.legend_elements()[0], ['N', 'E', 'S', 'W'])


# -

# ### Exercise 3 (max 7 points)
#
# Define a function `weighted_distance` that takes two points in a 2D Cartesian plane and a weight (a real number $w$) and returns the weighted Euclidean distance ($d = w\cdot\sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$) between them.
#
# To get the full marks, you should declare correctly the type hints and add a test within a doctest string.

def distance(a: tuple[float, float], b: tuple[float, float], w: float) -> float:
    """Return Euclidean distance between a and b.

    >>> np.isclose(distance((2, 3), (-1, -1), 2), 10.0)
    True

    """

    squares = (np.array(a) - np.array(b))**2
    return w*np.sqrt(squares.sum())


# ### Exercise 4 (max 6 points)
#
# Consider again the `X` and `Y` columns as the coordinates in a plane. Compute the average distance of each bird with respect to the other birds collected in the same subarea. (Hint: the magnitude of the result should be 4.4e06 for each subarea).
#
# To get the full marks avoid the use of explicit loops.

subarea_avg = data.groupby("subarea")[['X','Y']].apply(lambda d: d.apply(lambda r: distance(r['X'], r['Y'], 1), axis=1).mean())
subarea_avg


# ### Exercise 5 (max 2 points)
#
# Add a column `avg_subarea_dist`: in each row it has the value computed in Exercise 4 for the subarea of that row.

ss = subarea_avg[data['subarea']]
ss.index = data.index
data['avg_subarea_dist'] = ss
data.head()

# ### Exercise 6 (max 3 points)
#
# Plot a pie chart of the `functional_insectivores_species`. Each slice should have a proper label and report the corresponding proportion with one decimal digit (e.g., the slice for `functional_insectivores_species` number 8 should report 14.1%, since there are 19 occurrences and 135 records).

# +
fig, ax = plt.subplots()

_ = ax.pie(data['functional_insectivores_species'].value_counts(), autopct='%.1f%%', 
           labels=data['functional_insectivores_species'].value_counts().index)

# -

# ### Exercise 7 (max 3 points)
#
# Plot together, using different colors, the histograms with the density of `grassland` for each `seed_eater_species`.
#

fig, ax = plt.subplots()
for g in sorted(data['seed_eater_species'].unique()):
    ax.hist(data[data['seed_eater_species'] == g]['grassland'], density=True, label=str(g), bins='auto', alpha=.8)
ax.set_title('grassland')
_ = ax.legend()


# ### Exercise 8 (max 5 points)
#
# Given a random variable $x$, its **standardized** value is $\frac{x - \bar x}{\sigma_x}$, where $\bar x$ is the mean of $x$, and $\sigma_x$ its standard deviation. 
#
# Consider the statistical model:
#
# - $a$ is normally distributed with mean $=0$ and standard deviation $=1$
# - $b$ is normally distributed with mean $=0$ and standard deviation $=1$
# - $\sigma$ is exponentially distributed with $\lambda = 1$
# - The standardized value of `grassland` is normally distributed with mean $=a + b*V$ and standard deviation $=\sigma$, where $V$ is the standardized value of `vineyards`.
#
# Code this model with pymc, sample the model, and print the summary of the resulting estimation by using `az.summary`.


# +
def standard(x: pd.Series) -> pd.Series:
    return (x - x.mean())/x.std()

with pm.Model() as model:
    a = pm.Normal('a', 0, 1)
    b = pm.Normal('b', 0, 1)
    sigma = pm.Exponential('sigma', 1)
    g = pm.Normal('g', mu=a+b*standard(data['grassland']), 
                       sigma=sigma, 
                       observed=standard(data['vineyards']))

    idata = pm.sample(return_inferencedata=True)
# -

az.summary(idata)


