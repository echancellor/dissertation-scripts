'''
This module does the cluster analysis on the individual overall probability distributions
(as csv files)

This module makes the figures 3.3
'''

import os
import gdal
import sys
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsVectorLayer
)
import pandas as ps
from PyQt5.QtCore import QFileInfo
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



sns.set()

fn = "C:\\Dissertation Project\\ScenariosQGIS\\Scenario28 - Fish,Mammal,Turtle,Larval,Coral\\ClusterInput4.csv"

df = ps.read_csv(fn, keep_default_na=False, na_values=[""])

df1 = df.fillna(0)
#df1.set_index('key', inplace=True)
g=sns.clustermap(df1)

plt.show()

