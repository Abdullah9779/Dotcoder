class GitHubTool:
    def __init__(self, github_token=None):
        """
            Initialize the GitHubTool with a GitHub token.

            Args:
                github_token (str): Optional GitHub token. If not provided, it will be loaded from environment variables.
        """
        import os

        self.GITHUB_TOKEN = github_token or os.getenv("GITHUB_TOKEN")

        if not self.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN is not set. Pass it as an argument or set it in environment variables.")
        
    # ********** GitHub Search Tool **********

    def search_github_code_urls(self, data_for_search: dict = {}) -> list:
        """
        You have access to a tool called **"GitHubCodeUrlSearchTool"** that searches public GitHub repositories for HTML code files related to a given query using the GitHub Code Search API.

        This tool is especially useful when you need real-world code examples, UI components, or actual HTML implementations to enhance your output or build better websites.

        To use this tool, provide a dictionary `data_for_search` with the following keys:

        * `"query"`: *(required)* A keyword string to search within code files
        * `"max_results"`: *(optional)* The number of results to return (default is 10)
        * `"repo"`: *(optional)* A string to restrict the search to a specific GitHub repository (e.g., "username/repo") else `None`
        * `"file_format"`: *(required)* File type for filtering, which must **always** be set to `"html"` (do not change this)

        **Example:**

        ```python
        {
            "query": "chat UI component",
            "max_results": 5,
            "repo": "Abdullah9779/flask-projects", # else None
            "file_format": "html"
        }
        ```

        The tool constructs a GitHub Code Search query using the given inputs and returns a list of dictionaries. Each dictionary includes:

        * `"repo"`: Repository full name
        * `"description"`: Repository description
        * `"file"`: Path to the matching file
        * `"url"`: Direct URL to view the code file

        If no results are found or an error occurs, a relevant message is returned.
        Use this tool whenever you need real, working HTML code examples from GitHub to improve your designs or code generation results.
        If the user requests—or if you need to find HTML code to improve the website—you can use this tool to search for relevant code files in public or specific repositories.
        """

        import requests

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.GITHUB_TOKEN}"
        }

        url = "https://api.github.com/search/code"

        if data_for_search.get('repo', None) is not None:
            full_query = f"{data_for_search['query']} repo:{data_for_search['repo']} in:file language:{data_for_search['file_format']}"
        else:
            full_query = f"{data_for_search['query']} in:file language:{data_for_search['file_format']}"

        params = {
            "q": full_query,
            "per_page": data_for_search.get("max_results", 10)
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return [f"❌ Error {response.status_code}: {response.text}"]

        results = []
        for item in response.json().get("items", []):
            results.append({
                "repo": item["repository"]["full_name"],
                "description": item["repository"].get("description", "No description available"),
                "file": item["path"],
                "url": item["html_url"]
            })

        if not results:
            return ["No results found."]

        return results
    
    # ********** GitHub Raw File Content Tool **********

    def get_content_from_url(self, url: str) -> str:
        """
        You have access to a tool called "GetContentFromUrlTool" that retrieves and returns the content of a file from a direct raw URL, typically a raw GitHub file link.
        Use this tool when you need to read the actual contents of a code file or text file hosted online, such as fetching HTML, JavaScript, Python, or README files from raw GitHub URLs.
        To use this tool, follow the correct argument sequence: provide a single required argument url, which must be a string representing the direct raw file URL.
        The tool attempts to fetch the file content from the given URL and returns the entire content as a string.
        If the file contains more than 60,000 lines, only the first 60,000 lines are returned to handle large files efficiently.
        If the URL is invalid, the file is inaccessible, or the content is empty, the tool returns an error message.
        Use this tool to analyze, summarize, or transform live code from public repositories or other raw sources, and you are allowed to use the fetched content directly in your own code or outputs.
        """
        import requests

        response = requests.get(url)
        if response.status_code != 200:
            return f"❌ Error {response.status_code}: {response.text}"

        content = response.content.decode('utf-8')
        if not content:
            return "No content found at the provided URL."
        
        content_tokens = content.splitlines()
        if len(content_tokens) <= 50000:
            return content
        else:
            return "\n".join(content_tokens[0:50000])

