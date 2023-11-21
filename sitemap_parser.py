import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


class SitemapParser:
    """
    Class for parsing and extracting URLs from sitemaps of a specified website.
    Limits the number of sitemaps processed to avoid excessive scraping.

    Attributes:
        target_url (str): URL of the target website for sitemap extraction.
        sitemap_data (dict): Dictionary to store URLs and their DataFrame representation.
        processed_sitemaps_count (int): Counter for the number of sitemaps processed.
        max_sitemap_limit (int): Maximum number of sitemaps to process.
    """

    def __init__(self, target_url):
        """
        Constructor for SitemapParser.

        Args:
            target_url (str): Website URL to extract sitemaps from.
        """
        self.target_url = target_url
        self.sitemap_data = {}
        self.processed_sitemaps_count = 0
        self.max_sitemap_limit = 20
        self.extract_sitemaps()

    def fetch_content(self, url):
        """
        Fetches and returns the content of a given URL.

        Args:
            url (str): URL to fetch the content from.

        Returns:
            str: The content of the URL.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return ""

    def parse_sitemap(self, sitemap_url):
        """
        Parses the sitemap XML and extracts URLs. Processes nested sitemaps recursively.

        Args:
            sitemap_url (str): URL of the sitemap to parse.
        """
        if self.processed_sitemaps_count >= self.max_sitemap_limit:
            return

        xml_content = self.fetch_content(sitemap_url)
        soup = BeautifulSoup(xml_content, "xml")
        urls = [loc.text for loc in soup.find_all("loc")]

        sitemap_id = sitemap_url.split("/")[-1]
        df = pd.DataFrame(urls, columns=["URLs"])
        df = self.enhance_dataframe(df)
        self.sitemap_data[sitemap_id] = df

        # Process nested sitemaps
        for loc in soup.find_all("loc"):
            if (
                loc.text.endswith(".xml")
                and self.processed_sitemaps_count < self.max_sitemap_limit
            ):
                self.processed_sitemaps_count += 1
                self.parse_sitemap(loc.text)

    def extract_sitemaps(self):
        """
        Extracts all sitemaps listed in the website's robots.txt.
        """
        robots_txt_url = f"{self.target_url}/robots.txt"
        robots_txt_content = self.fetch_content(robots_txt_url)
        for line in robots_txt_content.splitlines():
            if line.startswith("Sitemap:"):
                sitemap_url = line.split(": ")[1].strip()
                self.parse_sitemap(sitemap_url)

    def enhance_dataframe(self, dataframe):
        """
        Enhances the DataFrame by splitting URLs into components.

        Args:
            dataframe (pd.DataFrame): DataFrame of URLs to enhance.

        Returns:
            pd.DataFrame: Enhanced DataFrame.
        """

        def split_url_path(url):
            return url.replace(self.target_url, "").strip("/").split("/")

        max_depth = max(len(split_url_path(url)) for url in dataframe["URLs"])
        for depth in range(max_depth):
            dataframe[f"Level_{depth}"] = dataframe["URLs"].apply(
                lambda x: split_url_path(x)[depth]
                if depth < len(split_url_path(x))
                else None
            )

        return dataframe

    def save_to_csv(self, directory="parsed_sitemaps"):
        """
        Saves the parsed sitemaps to CSV files in the specified directory.

        Args:
            directory (str): Directory to save CSV files.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        for sitemap_id, df in self.sitemap_data.items():
            df.to_csv(os.path.join(directory, f"{sitemap_id}.csv"), index=False)


# Example usage:
# parser = SitemapParser("https://www.example.com")
# parser.save_to_csv()
