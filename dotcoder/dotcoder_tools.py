from langchain.tools import Tool

from dotcoder.google_search_tool import GoogleSearchTool
from dotcoder.github_tool import GitHubTool


# *************** Google Search Tool ****************

google_search = GoogleSearchTool()

google_search_tool = Tool(
    name="GoogleSearchTool",
    func=google_search.google_search,
    description=google_search.google_search.__doc__
)

# **************** GitHub Search Tool ****************

github_search = GitHubTool()

github_code_url_search_tool = Tool(
    name="GitHubCodeUrlSearchTool",
    func=github_search.search_github_code_urls,
    description=github_search.search_github_code_urls.__doc__
)

get_content_from_url_tool = Tool(
    name="GetContentFromUrlTool",
    func=github_search.get_content_from_url,
    description=github_search.get_content_from_url.__doc__
)
