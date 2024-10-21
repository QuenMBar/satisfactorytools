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

    def db_append_generic(self, original_db: pd.DataFrame, data: dict) -> pd.DataFrame:
        new_dataframe = pd.DataFrame([data])
        if original_db.empty:
            return new_dataframe
        return pd.concat([original_db, new_dataframe], ignore_index=True)

    def get_inputs_array(self, item_name: str) -> pd.Series:
        inputs_array = self.base_df[self.base_df["item_name"] == item_name].iloc[0]
        result_array = []
        for index in range(0, 30):
            if f"input_{index}_type" not in inputs_array:
                break
            input_name = inputs_array[f"input_{index}_type"]
            if pd.isnull(input_name):
                break
            if input_name in ("production", "Raw", "Input"):
                result_array.append(
                    {
                        "type": input_name,
                        "name": inputs_array[f"input_{index}_name"],
                        "amount": float(inputs_array[f"input_{index}_amount"]),
                    }
                )

        return result_array

    # TODO: Need to handle Recursive recipes.  Disolved Silica being made out of quartz and not accounting for the dissolved silica in the quartz recipe.
    # Special Cases: Dark matter (TODO), rubber/plastic (Handler for 1->3), quartz crystals(Handler for the option of either recipe),
    # compacted coal (end there, not useful), Aluminum Ingot (use pure aluminum ingot recipe), raw resource or input exists (break)
    def core_logic(self, name: str, ammount) -> None:
        print(f"Getting history for {name}.")
        new_data = {}
        if name in ("Dark Matter Residue", "Plastic", "Rubber", "Quartz Crystal"):
            print(f"{name} will be parsed through a handler.")
            new_data["Recipe"] = f"Handler {name}"
            new_data["Result_Name_0"] = name
            new_data["Result_Ammount_0"] = ammount
            self.db_append(new_data)
            return None

        inputs_array = self.get_inputs_array(name)
        print(f"Inputs for {name}: {inputs_array}")

        if any(input_item["type"] in ("Raw", "Input") for input_item in inputs_array) or name == "Compacted Coal":
            print(f"{name} is a raw resource or input.")
            new_data["Recipe"] = f"Raw or Input {name}"
            new_data["Result_Name_0"] = name
            new_data["Result_Ammount_0"] = ammount
            self.db_append(new_data)
            return None

        if len(inputs_array) == 0:
            print(f"No inputs found for {name}.")
            raise ValueError(f"No inputs found for {name}.")

        recipe_name = inputs_array[0]["name"]
        if name == "Aluminum Ingot":
            recipe_name = "Alternate: Pure Aluminum Ingot"

        item_ammount = ammount
        recipe = self.recipe_df[self.recipe_df["Name"] == recipe_name].iloc[0]
        new_data["Recipe"] = recipe["Name"]
        print(f"Recipe: {recipe['Name']}")
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

    def condense_output(self):
        condensed_output = pd.DataFrame()
        for index, row in self.output_df.iterrows():
            new_row = {}
            if (not condensed_output.empty) and row["Recipe"] in condensed_output["Recipe"].values:
                continue

            new_row["Recipe"] = row["Recipe"]
            all_rows = self.output_df[self.output_df["Recipe"] == row["Recipe"]]

            for index in range(0, 5):
                if f"Result_Name_{index}" not in row:
                    break
                new_row[f"Result_Name_{index}"] = row[f"Result_Name_{index}"]
                new_row[f"Result_Ammount_{index}"] = all_rows[f"Result_Ammount_{index}"].sum()
            for index in range(0, 5):
                if f"Input_Name_{index}" not in row:
                    break
                new_row[f"Input_Name_{index}"] = row[f"Input_Name_{index}"]
                new_row[f"Input_Ammount_{index}"] = all_rows[f"Input_Ammount_{index}"].sum()

            condensed_output = self.db_append_generic(condensed_output, new_row)
        self.output_df = condensed_output

    def get_dependencies(self, name: str) -> pd.DataFrame:
        self.output_df = pd.DataFrame()
        item_ammount = self.base_df[self.base_df["item_name"] == name].iloc[0]["total_production"]
        self.core_logic(name, item_ammount)
        self.condense_output()
        self.output_df.to_csv(f"output_{name.replace(' ', '_')}.csv", index=False)
