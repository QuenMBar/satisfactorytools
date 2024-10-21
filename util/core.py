import pandas as pd


class Core:
    def __init__(self, base_df: pd.DataFrame, resourse_df: pd.DataFrame, recipe_df: pd.DataFrame):
        self.base_df = base_df
        self.resourse_df = resourse_df
        self.recipe_df = recipe_df
        print("Core initialized.")

    def get_dependencies(self, name: str) -> pd.DataFrame:
        print(f"Getting history for {name}.")
        item_ammount = self.base_df[self.base_df["item_name"] == name].iloc[0]["net_total"]
