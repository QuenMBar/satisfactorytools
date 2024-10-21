import pandas as pd
import json
import re
from util.constants import *
from util.native_class import NativeClass
from util.satisfactory_recipes import SatisfactoryRecipes

df = pd.read_csv("C:/Users/qbeas/Downloads/satisfactorytools-2024-10-15.csv")
print(df.head())

sr = SatisfactoryRecipes()
# print(sr.find_class(NativeClass.Recipe))

# Given a end product, create a data frame mapping out what the process for it would be.

sr.datamineDependents("Uranium Fuel Rod")
