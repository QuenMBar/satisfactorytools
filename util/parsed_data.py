import pandas as pd


class ParsedData:
    def __init__(self, data):
        # self.data = pd.read_csv(data)
        # print(self.data.head())
        # self.data = self.data.loc[:, ~self.data.columns.str.contains("ng-scope src")]
        # self.data.columns = ['item_name', 'total_production', 'total_consumption', 'net_total', ]
        # print(self.data.to_markdown())
        # with open("output.md", "w") as file:
        #     file.write(self.data.to_markdown())
        # # self.data = self.data.applymap(lambda x: float(x.replace("/ min", "")) if isinstance(x, str) and "/ min" in x else x)
        # # print(self.data.head())




parDa = ParsedData()
