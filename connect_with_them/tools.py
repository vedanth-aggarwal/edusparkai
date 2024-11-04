import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from langchain import hub
from langchain.agents import AgentExecutor,create_react_agent,tool
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains.summarize.chain import load_summarize_chain
from langchain.tools.base import StructuredTool
from langchain_groq import ChatGroq
from langchain.pydantic_v1 import BaseModel, Field

from Credentials import credentials,categories_mapping
from Prompts import Prompt_query

from bs4 import BeautifulSoup

model_name = 'llama-3.1-70b-versatile'

llm = ChatGroq(model=model_name,temperature=0.3,api_key="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")

class SearchArticlesModel(BaseModel):
    category: str = Field(description='Category that you want to get some information about')

def scrape_page(category: str, num_articles: int) -> list:
    # Build the URL based on the category
    url = f"https://www.edutopia.org/{categories_mapping[category]}"

    try:
        # Send a GET request to fetch the page content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the 'main' section of the page
        main = soup.find('main')
        if not main:
            print("Main section not found")
            return []

        # Find the 'ul' element within the 'main' section
        ul = main.find('ul')
        if not ul:
            print("List (ul) not found")
            return []

        # Find all 'li' elements within the 'ul'
        li_tags = ul.find_all('li')

        # Extract the 'href' attribute from 'a' tags within 'li'
        article_links = [li.find('a')['href'] for li in li_tags if li.find('a')]

        # Return the required number of article links
        return [f'https://www.edutopia.org{link}' for link in article_links[:min(num_articles, len(article_links))]]

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []

def Search_Articles(category: str) -> str:
    try:
        if category not in list(categories_mapping.keys()) :
            print(f"\n category before changing : {category}")
            if "'" in category :
                category = category.replace("'","")
            if '"' in category :
                category = category.replace('"','')
            print(f"\n category after changing : {category}")
            if category not in list(categories_mapping.keys()) :
                return f"Invalid category: {category}. Valid categories are: {list(categories_mapping.keys())}"

        links = scrape_page(category, 3)
        if not links:
            return f"No articles found for '{category}'"

        loader = WebBaseLoader(links)
        docs = loader.load()

        summarization_chain = load_summarize_chain(llm=llm, verbose=False,chain_type='map_reduce')
        summary = summarization_chain.invoke(docs)
        return summary
    except Exception as e:
        return f"An error occurred while searching articles for '{category}'. Please try again later."

tools = [
    StructuredTool.from_function(
        name='Search Articles',
        func=Search_Articles,
        description= f'''Get a some informations about a certain category from edutopia website ,
        this tool is useful when you want to have more informations from the web about a certain teaching category ,
        it takes a category as argument that is included in {list(categories_mapping.keys())}''',
        args_schema= SearchArticlesModel
    )
]

prompt = hub.pull("hwchase17/react") #structured-chat-agent
agent = create_react_agent(llm,tools,prompt)

Agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors="Check your output formatting, ensure correct syntax.",
    max_iterations=20
)
