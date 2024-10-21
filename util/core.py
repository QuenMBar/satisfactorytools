import pandas as pd


class Core:
    def __init__(self, base_df: pd.DataFrame, resourse_df: pd.DataFrame, recipe_df: pd.DataFrame):
        self.base_df = base_df
        self.resourse_df = resourse_df
        self.recipe_df = recipe_df
        self.output_df = pd.DataFrame()
        print("Core initialized.")

    # TODO: Handle duplicate cases and multiple inputs
    def db_append(self, data: dict):
        new_dataframe = pd.DataFrame([data])
        if self.output_df.empty:
            self.output_df = new_dataframe
            return
        self.output_df = pd.concat([self.output_df, new_dataframe], ignore_index=True)

    def core_logic(self, name: str, ammount) -> None:
        print(f"Getting history for {name}.")
        new_data = {}
        if name in self.resourse_df["Name"].values:
            print(f"{name} does exist in resourse_df.")
            new_data["Recipe"] = f"Raw {name}"
            new_data["Result_Name_0"] = name
            new_data["Result_Ammount_0"] = ammount
            self.db_append(new_data)
            return None

        item_ammount = ammount
        recipe = self.recipe_df[self.recipe_df["Name"] == name].iloc[0]
        new_data["Recipe"] = recipe["Name"]
        product = next((item for item in recipe["Product"] if item["Name"] == name), None)
        normalized_item_ammount = item_ammount / product["Amount"]
        print("Output: ")
        for index, product in enumerate(recipe["Product"]):
            product_name = product["Name"]
            product_ammount = product["Amount"]
            product_total = normalized_item_ammount * product_ammount
            print(f"{product_name}: {product_total}")
            new_data[f"Result_Name_{index}"] = product_name
            new_data[f"Result_Ammount_{index}"] = product_total
        print("Input: ")
        for index, ingredient in enumerate(recipe["Ingredients"]):
            ingredient_name = ingredient["Name"]
            ingredient_ammount = ingredient["Amount"]
            ingredient_total = normalized_item_ammount * ingredient_ammount
            print(f"{ingredient_name}: {ingredient_total}")
            new_data[f"Input_Name_{index}"] = ingredient_name
            new_data[f"Input_Ammount_{index}"] = ingredient_total
        self.db_append(new_data)
        for ingredient in recipe["Ingredients"]:
            ingredient_name = ingredient["Name"]
            ingredient_ammount = ingredient["Amount"]
            ingredient_total = normalized_item_ammount * ingredient_ammount
            self.core_logic(ingredient_name, ingredient_total)

    def get_dependencies(self, name: str) -> pd.DataFrame:
        self.output_df = pd.DataFrame()
        item_ammount = self.base_df[self.base_df["item_name"] == name].iloc[0]["total_production"]
        self.core_logic(name, item_ammount)
        self.output_df.to_csv("output.csv", index=False)
