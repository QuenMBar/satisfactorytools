import pandas as pd
import json
import re
from util.constants import *
from util.native_class import NativeClass
from util.satisfactory_recipes import SatisfactoryRecipes
from util.scraper import Scraper

scraped = Scraper()
result = scraped.scrape_data()
if not result:
    print("Failed to scrape data, check the scraper.")
    exit()
scraped_dataframe = pd.read_csv("scraped_data.csv")
print(scraped_dataframe.head())

sr = SatisfactoryRecipes()
resource_df = sr.parse_data_resource()
print(resource_df.head())
recipe_df = sr.parse_data_recipe()
print(recipe_df.head())

# sr = SatisfactoryRecipes()
# print(sr.find_class(NativeClass.Recipe))

# Given a end product, create a data frame mapping out what the process for it would be.

# sr.datamineDependents("Uranium Fuel Rod")
