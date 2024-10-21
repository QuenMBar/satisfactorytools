import pandas as pd
import json
import re
from util.constants import *
from util.native_class import NativeClass
from util.satisfactory_recipes import SatisfactoryRecipes
from util.scraper import Scraper
from util.core import Core

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

c = Core(scraped_dataframe, resource_df, recipe_df)
c.get_dependencies("Uranium Fuel Rod")
c.get_dependencies("Plutonium Fuel Rod")


# print(get_inputs_array("Copper Ingot", scraped_dataframe))
