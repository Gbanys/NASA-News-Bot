from typing import Any
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
import qdrant_client
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from mysql_database.database import add_answer, add_question, get_questions_by_conversation
from mysql_database.message_history import get_message_history, get_questions_and_answers_from_database
import boto3

ssm_client = boto3.client('ssm', region_name='eu-west-2')
def get_parameter(param_name, with_decryption=True) -> Any:
    response = ssm_client.get_parameter(
        Name=param_name,
        WithDecryption=with_decryption
    )
    return response['Parameter']['Value']

if os.environ["ENVIRONMENT"] == "PRODUCTION":
    os.environ["OPENAI_API_KEY"] = get_parameter('/nasa_chatbot/openai_api_key')


def retrieve_information_from_nasa_vectorstore(user_input: str) -> str:
    "Retrieve news articles from NASA"
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    client = qdrant_client.QdrantClient(host=os.environ["QDRANT_HOST"], port=6333)
    qdrant = Qdrant(
        client=client,
        collection_name="nasa_web_pages",
        embeddings=embeddings,
    )
    retriever = qdrant.as_retriever()
    docs = retriever.invoke(user_input)
    return "\n\n".join(doc.page_content for doc in docs)


def define_and_return_the_agent_executor(temperature: float) -> AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Use the tool that you have to retrieve relevant context. \
            If you are not able to retrieve relevant information to answer the question then say that you don't know the answer"),
            ("placeholder", "{history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ]
    )

    llm = ChatOpenAI(temperature=temperature)
    nasa_tool = StructuredTool.from_function(func=retrieve_information_from_nasa_vectorstore)
    tools = [nasa_tool]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor



def create_agent(temperature: float) -> RunnableWithMessageHistory:
    agent_executor = define_and_return_the_agent_executor(temperature)
    agent = RunnableWithMessageHistory(
        agent_executor,
        get_message_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    return agent


def query(question: str, conversation_id: int, temperature: float) -> list:
    agent = create_agent(temperature)
    try:
        agent.invoke({"input" : question}, config={"configurable" : {"session_id" : conversation_id}})
    except Exception as e:
        print(e)
        add_question(question, conversation_id)
        question_id = get_questions_by_conversation(conversation_id)[-1][0]
        add_answer("Sorry, I am having trouble answering this question, could you please try again?,", question_id)
        
    list_of_messages = get_questions_and_answers_from_database(conversation_id)
    return list_of_messages


