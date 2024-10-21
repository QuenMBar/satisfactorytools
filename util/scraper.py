from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import os


class Scraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument(
            "--user-data-dir=C:/Users/qbeas/AppData/Local/Google/Chrome/User Data"
        )  # Use your Chrome user data
        self.chrome_options.add_argument("--profile-directory=Default")  # Use your Chrome profile directory
        self.dataframe = pd.DataFrame()

    def parse_float_from_string(self, s):
        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
        if match:
            return float(match.group())
        return None

    def db_append(self, data: dict) -> pd.DataFrame:
        new_dataframe = pd.DataFrame([data])
        if self.dataframe.empty:
            self.dataframe = new_dataframe
        self.dataframe = pd.concat([self.dataframe, new_dataframe], ignore_index=True)

    def scrape_data(self) -> bool:
        if os.path.isfile("scraped_data.csv"):
            print("Data already loaded")
            return True

        print("Loading data")
        driver = webdriver.Chrome(options=self.chrome_options)

        # Navigate to the website
        driver.get("https://www.satisfactorytools.com/1.0/production")
        time.sleep(5)

        # Find the element and click it
        element = driver.find_element(By.XPATH, "//html/body/app/div/div/ui-view[2]/entity-listing/ui-view/ul/li[13]/span")
        element.click()
        time.sleep(1)

        element = driver.find_element(By.XPATH, "//html/body/app/div/div/ui-view[2]/entity-listing/ui-view/div[2]/div[5]/ul/li[4]/a")
        element.click()
        time.sleep(1)

        # Find the tbody element
        tbody = driver.find_element(By.XPATH, "//html/body/app/div/div/ui-view[2]/entity-listing/ui-view/div[2]/div[5]/div[4]/table/tbody")

        # Loop through each tr element within the tbody
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            # Find the td element within the tr and click it
            cell = row.find_element(By.TAG_NAME, "td")
            cell.click()
            # time.sleep(1)  # Adjust sleep time as necessary

        time.sleep(1)
        # Get the page source
        page_source = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        # Close the browser
        driver.quit()

        div = soup.find("div", {"ng-show": "ctrl.tab.resultTab === 'items'"})
        table_soup = div.table.tbody
        rows = table_soup.find_all("tr", recursive=False)
        for row in rows:
            loc_data = {}
            cells = row.find_all("td", recursive=False)
            loc_data["item_name"] = cells[1].text.strip()
            # print(loc_data)
            totals = cells[3].small.find_all("span", recursive=False)
            loc_data["total_production"] = self.parse_float_from_string(totals[0].text)
            loc_data["total_consumption"] = self.parse_float_from_string(totals[1].text)
            loc_data["net_total"] = self.parse_float_from_string(totals[2].text)

            inputs = cells[3].table.tbody.find_all("tr", recursive=False)
            for index, in_row in enumerate(inputs):
                in_cells = in_row.find_all("td", recursive=False)
                if in_cells[0].span.get("class")[1] == "fa-external-link-alt":
                    loc_data[f"input_{index}_type"] = "Raw"
                elif in_cells[0].span.get("class")[1] == "fa-sign-in-alt":
                    loc_data[f"input_{index}_type"] = "Input"
                elif in_cells[0].span.get("class")[1] == "fa-plus":
                    loc_data[f"input_{index}_type"] = "production"
                elif in_cells[0].span.get("class")[1] == "fa-minus":
                    loc_data[f"input_{index}_type"] = "consumption"
                else:
                    raise ValueError("Unknown input type")

                loc_data[f"input_{index}_amount"] = self.parse_float_from_string(in_cells[1].text)
                loc_data[f"input_{index}_name"] = in_cells[4].text.strip()

            self.db_append(loc_data)

        result = self.validate_data()
        if not result:
            return False

        self.dataframe.to_csv("scraped_data.csv", index=False)
        return True

    def validate_data(self) -> bool:
        for index, row in self.dataframe.iterrows():
            if (
                pd.isnull(row["item_name"])
                or pd.isnull(row["total_production"])
                or pd.isnull(row["total_consumption"])
                or pd.isnull(row["net_total"])
            ):
                print(f"Row {index} has missing values.")
                print(row)
                return False
            if row["item_name"] in ("Water", "Plutonium Waste", "Uranium Waste"):
                continue
            if not (round(row["total_production"], 4) == round(row["total_consumption"] + row["net_total"], 4)):
                print(f"Row {index} has inconsistent totals.")
                print(row)
                return False

            total_in = 0
            total_out = 0
            for i in range(30):
                if f"input_{i}_type" not in row or pd.isnull(row[f"input_{i}_type"]):
                    break
                if row[f"input_{i}_type"] in ("Input", "Raw", "production"):
                    total_in += row[f"input_{i}_amount"]
                elif row[f"input_{i}_type"] == "consumption":
                    total_out += row[f"input_{i}_amount"]

            total_in = round(total_in, 4)
            total_out = round(total_out, 4)
            if not (total_in == row["total_production"] and total_out == (row["total_consumption"])):
                print(f"Row {index} has inconsistent input/output totals.")
                print(row)
                print(total_in, total_out)
                return False

        return True
