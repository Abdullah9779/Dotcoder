class GoogleSearchTool():
    def __init__(self, serper_api_key=None):
        import os

        self.SERPER_API_KEY = serper_api_key or os.getenv("SERPER_API_KEY")

        if not self.SERPER_API_KEY:
            raise ValueError("SERPER_API_KEY is not set. Pass it as an argument or set it in environment variables.")


    # ********** Google Search Tool **********

    def google_search(self, data_for_search: dict = {}):
        """
        You have access to a tool named **"GoogleSearchTool"** that allows you to retrieve real-time information from the internet using Google's search capabilities via the Serper API.
        This tool supports multiple search types: `"Search"` for general results, `"Images"` for image queries, `"Videos"` for video results, `"News"` for news articles, and `"Webpage"` to extract the full content of a specific URL.

        To use this tool, provide a dictionary `data_for_search` with the following keys:

        * `"search_query"`: *(required)* The search term or URL string
        * `"k"`: *(optional)* The number of results to return (default is 10)
        * `"search_type"`: *(required)* One of the following strings: `"Search"`, `"Images"`, `"Videos"`, `"News"`, or `"Webpage"`

        For example:

        ```python
        {
            "search_query": "latest AI models 2025",
            "k": 5,
            "search_type": "News"
        }
        ```

        If `"search_type"` is `"Webpage"`, the tool sends the URL to extract its full content.
        The function sends a POST request to the Serper API with your `SERPER_API_KEY` and returns the response JSON if successful.
        Use this tool to enhance your answers with live data, images, videos, or full webpage content.
        If the user requests—or if the AI determines that images, videos, or news articles would enhance the response—you can use this tool to fetch relevant and up-to-date content.
        """

        search_categories = [
            "Search",
            "Images",
            "Videos",
            "News",
            "Webpage",
        ]

        if data_for_search["search_type"] not in search_categories:
            return f"Invalid search type. Choose from {search_categories}"

        import requests
        import json

        if data_for_search["search_type"] == "Webpage":
            url = "https://scrape.serper.dev"

            payload = json.dumps({
                "url": data_for_search["search_query"],
            })

        else:
            url = f"https://google.serper.dev/{data_for_search['search_type']}"

            payload = json.dumps({
                "q": data_for_search["search_query"],
                "num": data_for_search.get("k", 10),
            })
        
        headers = {
            'X-API-KEY': self.SERPER_API_KEY,   
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return "Error occurred while searching."
