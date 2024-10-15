import pandas as pd
import json
import re
from util.constants import *

df = pd.read_csv("C:/Users/qbeas/Downloads/satisfactorytools-2024-10-15.csv")
print(df.head())


def array_find(array, key, value):
    for item in array:
        if key in item and item[key] == value:
            return item

def parse_recipe(string):
    data_str = string[1:-1]

    # Define a regex pattern to extract ItemClass and Amount
    pattern = re.compile(r'ItemClass="([^"]+)",Amount=(\d+)')

    # Find all matches
    matches = pattern.findall(data_str)

    # Convert matches to a list of dictionaries
    return [{"ItemClass": match[0], "Amount": int(match[1])} for match in matches]

def find_native_class(data, name):
    for item in data:
        if 'NativeClass' in item and 'Classes' in item:
            for cls in item['Classes']:
                if 'mDisplayName' in cls and cls['mDisplayName'] == name:
                    return item['NativeClass']
    return None




print(parse_recipe(array_find(array_find(json['data'], 'NativeClass', "/Script/CoreUObject.Class'/Script/FactoryGame.FGRecipe'")['Classes'], 'mDisplayName', 'Alternate: Classic Battery')['mIngredients']))
