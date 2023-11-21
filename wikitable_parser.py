import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class WikiTableParser:
    """
    A class to parse and extract tables from a Wikipedia page into pandas DataFrames.

    Attributes:
        url (str): URL of the Wikipedia page to parse.
        titles (list of str): Optional titles for each table to be extracted.
        dataframes (list of pandas.DataFrame): Extracted tables as DataFrames.
    """

    def __init__(self, url, titles=None):
        """
        Initialize the WikiTableParser with a URL.

        Args:
            url (str): URL of the Wikipedia page to parse.
            titles (list of str, optional): Titles for each table to be extracted.
        """
        self.url = url
        self.titles = titles or []
        self.dataframes = []

    def fetch_data(self):
        """
        Fetches the HTML content of the Wikipedia page.

        Returns:
            BeautifulSoup: Parsed HTML content of the page.

        Raises:
            Exception: If the page cannot be retrieved.
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
        else:
            raise Exception(
                f"Failed to retrieve the page. Status code: {response.status_code}"
            )

    def parse_tables(self):
        """
        Parses the HTML content and extracts tables into DataFrames.
        """
        soup = self.fetch_data()
        tables = soup.find_all("table", {"class": "wikitable"})

        for i, table in enumerate(tables):
            rows = table.find_all("tr")
            header = [th.text.strip() for th in rows[0].find_all("th")]
            data = [[td.text.strip() for td in tr.find_all("td")] for tr in rows[1:]]
            df = pd.DataFrame(data, columns=header)

            title = self.titles[i] if i < len(self.titles) else f"Table {i+1}"
            df.title = title
            self.dataframes.append(df)

    def get_dataframes(self):
        """
        Returns the DataFrames extracted from the Wikipedia page.

        Returns:
            list of pandas.DataFrame: Extracted DataFrames.
        """
        if not self.dataframes:
            self.parse_tables()
        return self.dataframes

    def save_dataframes_to_csv(self, directory="output_data"):
        """
        Saves the extracted tables to CSV files in the specified directory.

        Args:
            directory (str): Directory to save the CSV files. Defaults to 'output_data'.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        for i, df in enumerate(self.dataframes):
            title = self.titles[i] if i < len(self.titles) else f"Table_{i+1}"
            file_path = os.path.join(directory, f"{title}.csv")
            df.to_csv(file_path, index=False)
