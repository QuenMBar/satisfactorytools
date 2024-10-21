import pandas as pd


class Core:
    def __init__(self):
        print("Core initialized.")

    def get_history(self, name: str) -> pd.Dataframe:
        print("Getting history.")
