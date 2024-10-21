from enum import Enum
import re
from util.constants import json
from util.native_class import NativeClass
import pandas as pd


class SatisfactoryRecipes:

    def __init__(self):
        self.data = json["data"]

    def find_class(self, nc: NativeClass) -> dict:
        """
        Finds and returns the dictionary item from self.data where the "NativeClass" key matches the value of the given NativeClass instance.

        Args:
            nc (NativeClass): An instance of NativeClass whose value is used to search in the data.

        Returns:
            dict: The dictionary item from self.data that matches the given NativeClass value.
                  Returns None if no match is found.
        """
        value = nc.value
        for item in self.data:
            if "NativeClass" in item and item["NativeClass"] == value:
                return item

    def parse_recipe(self, string):
        data_str = string[1:-1]

        # Define a regex pattern to extract ItemClass and Amount
        pattern = re.compile(r'ItemClass="([^"]+)",Amount=(\d+)')

        # Find all matches
        matches = pattern.findall(data_str)

        # Convert matches to a list of dictionaries
        return [{"ItemClass": match[0], "Amount": int(match[1])} for match in matches]

    def find_native_classes(self, name) -> list:
        classes = []
        for item in self.data:
            if "NativeClass" in item and "Classes" in item:
                for cls in item["Classes"]:
                    if "mDisplayName" in cls and cls["mDisplayName"] == name:
                        classes.append(item["NativeClass"])
        return classes

    def find_item(self, nc: NativeClass, name: str):
        class_array = self.find_class(nc)
        matching_item = next((item for item in class_array["Classes"] if item.get("mDisplayName") == name), None)
