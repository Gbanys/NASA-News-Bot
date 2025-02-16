from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import os
from web_scrape_pages import extract_all_links
import boto3
from typing import Any

ssm_client = boto3.client('ssm', region_name='eu-west-2')
def get_parameter(param_name, with_decryption=True) -> Any:
    response = ssm_client.get_parameter(
        Name=param_name,
        WithDecryption=with_decryption
    )
    return response['Parameter']['Value']

if os.environ["ENVIRONMENT"] == "PRODUCTION":
    os.environ["OPENAI_API_KEY"] = get_parameter('/nasa_chatbot/openai_api_key')

def generate_embeddings() -> None:
    links = extract_all_links(number_of_pages=5)
    
    list_of_documents = []
    for link in links:
        documents = WebBaseLoader(link).load_and_split()
        valid_documents = [doc for doc in documents if doc.page_content]
        list_of_documents += valid_documents

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(list_of_documents)
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    qdrant = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=os.environ["QDRANT_HOST"],
        collection_name="nasa_web_pages",
    )

generate_embeddings()