import requests
import pandas as pd
import logging


class SpaceflightNewsScraper:
    """
    Scraper class for fetching spaceflight news articles from the Spaceflight News API.

    Attributes:
        base_url (str): Base URL of the Spaceflight News API.
        per_page_limit (int): Number of articles to fetch per API call.
        total_limit (int): Total number of articles to fetch.
    """

    def __init__(self, base_url, per_page_limit, total_limit):
        """
        Initialize the SpaceflightNewsScraper.

        Args:
            base_url (str): Base URL of the Spaceflight News API.
            per_page_limit (int): Number of articles per API call.
            total_limit (int): Total number of articles to fetch.
        """
        self.base_url = base_url
        self.per_page_limit = per_page_limit
        self.total_limit = total_limit

    def generate_urls(self):
        """
        Generate URLs for API calls based on the total limit and per page limit.

        Returns:
            list: List of URLs for API calls.
        """
        urls = []
        for offset in range(1, self.total_limit, self.per_page_limit):
            url = f"{self.base_url}?limit={self.per_page_limit}&offset={offset}"
            urls.append(url)
        return urls

    def scrape_data(self):
        """
        Scrape data from Spaceflight News API and compile into a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing combined data from all API calls.
        """
        urls = self.generate_urls()
        all_data = []

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()["results"]
                all_data.extend(data)
            except requests.RequestException as e:
                logging.error(f"Failed to retrieve data from {url}: {e}")

        return pd.DataFrame(all_data)


# Example usage:
# scraper = SpaceflightNewsScraper(
#     base_url="https://api.spaceflightnewsapi.net/v4/articles/",
#     per_page_limit=500,
#     total_limit=5000
# )
# data = scraper.scrape_data()
# print(data.head())
