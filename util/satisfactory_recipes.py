import re
from util.constants import json
from util.native_class import NativeClass
import pandas as pd


class SatisfactoryRecipes:

    def __init__(self):
        self.data = json["data"]
        self.resource_df = pd.DataFrame()
        self.recipe_df = pd.DataFrame()

    def parse_float_from_string(self, s):
        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
        if match:
            return float(match.group())
        return None

    def db_append_resource(self, data: dict) -> pd.DataFrame:
        new_dataframe = pd.DataFrame([data])
        if self.resource_df.empty:
            self.resource_df = new_dataframe
        self.resource_df = pd.concat([self.resource_df, new_dataframe], ignore_index=True)

    def db_append_recipe(self, data: dict) -> pd.DataFrame:
        new_dataframe = pd.DataFrame([data])
        if self.recipe_df.empty:
            self.recipe_df = new_dataframe
        self.recipe_df = pd.concat([self.recipe_df, new_dataframe], ignore_index=True)

    def parse_data_resource(self) -> pd.DataFrame:
        """
        Parses the data from the JSON file and returns a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the parsed data.
        """
        data = self.find_class(NativeClass.ResourceDescriptor)
        for item in data:
            self.db_append_resource(
                {"Name": item["mDisplayName"], "Description": item["mDescription"], "Abreviation": item["mAbbreviatedDisplayName"]}
            )

        return self.resource_df

    def parse_data_recipe(self) -> pd.DataFrame:
        """
        Parses the data from the JSON file and returns a pandas DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the parsed data.
        """
        data = self.find_class(NativeClass.Recipe)
        for item in data:
            self.db_append_recipe(
                {
                    "Name": item["mDisplayName"],
                    "Ingredients": self.parse_recipe(item["mIngredients"]),
                    "Product": self.parse_recipe(item["mProduct"]),
                }
            )

        return self.recipe_df

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
                return item["Classes"]

    def parse_recipe(self, string):
        data_str = string[1:-1]

        # Define a regex pattern to extract ItemClass and Amount
        pattern = re.compile(r'ItemClass="([^"]+)",Amount=(\d+)')

        # Find all matches
        matches = pattern.findall(data_str)

        # Convert matches to a list of dictionaries
        response = [{"ItemClass": match[0], "Amount": int(match[1])} for match in matches]
        for item in response:
            item_class_path = item["ItemClass"]
            item_class_name = item_class_path.split(".")[-1].replace("'", "")
            data = self.check_all_desc(item_class_name, "ClassName")

            item["Name"] = data["mDisplayName"]

        return response

    def find_native_classes(self, name: str, element_name: str) -> list:
        classes = []
        for item in self.data:
            if "NativeClass" in item and "Classes" in item:
                for cls in item["Classes"]:
                    if element_name in cls and cls[element_name] == name:
                        classes.append(item["NativeClass"])
        return classes

    def check_all_desc(self, name: str, element_name: str):
        classes = [
            NativeClass.ItemDescriptor,
            NativeClass.ItemDescriptorBiomass,
            NativeClass.ItemDescriptorNuclearFuel,
            NativeClass.ItemDescriptorPowerBoosterFuel,
            NativeClass.ResourceDescriptor,
            NativeClass.PowerShardDescriptor,
            NativeClass.ConsumableDescriptor,
            NativeClass.EquipmentDescriptor,
            NativeClass.BuildingDescriptor,
            NativeClass.PoleDescriptor,
            NativeClass.VehicleDescriptor,
            NativeClass.AmmoTypeInstantHit,
            NativeClass.AmmoTypeProjectile,
            NativeClass.AmmoTypeSpreadshot,
        ]
        for nc_class in classes:
            response = self.find_item(nc_class, name, element_name)
            if response:
                return response

        return None

    def find_item(self, nc: NativeClass, name: str, element_name: str):
        class_array = self.find_class(nc)
        matching_item = next((item for item in class_array if item.get(element_name) == name), None)
        return matching_item


# sr = SatisfactoryRecipes()
# # print(sr.find_native_classes("Desc_SpikedRebar_C", "ClassName"))
# # print(sr.parse_recipe(sr.find_item(NativeClass.Recipe, "Bauxite (Caterium)", "mDisplayName")["mIngredients"]))
# # print(sr.parse_recipe(sr.find_item(NativeClass.Recipe, "Bauxite (Caterium)", "mDisplayName")["mProduct"]))
# sr.parse_data()
