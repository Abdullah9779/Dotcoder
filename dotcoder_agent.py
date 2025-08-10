from dotenv import load_dotenv
load_dotenv()

# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

from dotcoder.dotcoder_tools import google_search_tool, get_content_from_url_tool, github_code_url_search_tool

with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# llm = ChatGroq(model="deepseek-r1-distill-llama-70b")

prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    ("placeholder", "{chat_history}"),
    ("human", "{query}"),
    ("placeholder", "{agent_scratchpad}")
])

chat_history = []

tools = [
    google_search_tool,
    get_content_from_url_tool,
    github_code_url_search_tool
]

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt, 
    tools=tools
)

agent_e = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

def DotCoderAgent(query, chat_history, system_prompt=system_prompt):
    response = agent_e.invoke({"query": query, "chat_history": chat_history, "system_prompt": system_prompt})
    return response


