from pydantic import BaseModel
from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from langchain.agents import AgentExecutor, create_tool_calling_agent 
from langchain_core.prompts import ChatPromptTemplate
import os
import json
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv 

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)





class url_param(BaseModel):
    From : str 
    To: str 
    amount: int 

@tool
def request_tools(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Sends an HTTP POST request to xe.com and retrieves the currency conversion rate
    for the given amount, from_currency, and to_currency.
    
    Example: amount=5, from_currency='USD', to_currency='INR'
    """
    url = f"https://www.xe.com/currencyconverter/convert/?Amount={amount}&From={from_currency}&To={to_currency}"
    response = requests.post(url=url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    rate_element = soup.find('p', class_='sc-708e65be-1 chuBHG')

    if rate_element:
        return f"{amount} {from_currency} = {rate_element.text.strip()} {to_currency}"
    else:
        return "Conversion rate not found in the HTML."    
    
tools = [request_tools]    

def agent_retriever():
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that can retrieve and extract currency conversion rates. "
                "Use the request_tools tool to get the HTML content and to parse the rate. and give the response as only the required keys(amount entered(usd/inr), converted amount(uswd/inr)) and respective values with not extra explainations ",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    # Construct the Tools agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor
# res = agent_executor.invoke({"input": "can you convert 1 inr to usd"})



     
     

def get_news():
    # os.environ["TAVILY_API_KEY"] = os.get()
    retriever = TavilySearchAPIRetriever(k=10)

    prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the context provided.
        Format the response as a JSON where each item contains:
        - "headline": (short headline or summary)
        - no need for dates just mention the source 

        I want to use it as a slider for latest USD-INR news. The response need to be containing atleast 5 news

        Context: {context}

        Question: {question}
        """
    )

    chain = (
        RunnablePassthrough.assign(context=(lambda x: x["question"]) | retriever)
        | prompt
        | llm
    )

    # Run the chain with a question
    result = chain.invoke({"question": "give me the 5 latest news about USD to INR currency exchange rate"})
    print("==========================output============================")
    # print(result.content)
    op = result.content[7:-3]
    op_dict = json.loads(op)
    # print(op_dict)

    return op_dict
        
def covert_currency(params: url_param) -> str:
    agent = agent_retriever()
    prompt_input = f"Convert {params.amount} {params.From} to {params.To}"
    response = agent.invoke({"input": prompt_input})
    op = response['output'][7:-3]
    op_dict = json.loads(op)
    return op_dict


