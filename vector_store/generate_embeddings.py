from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain.vectorstores import Qdrant
import qdrant_client
import os
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from web_scrape_pages import extract_all_links

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

    url = "http://localhost:6333"

    qdrant = QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=url,
        collection_name="nasa_web_pages",
    )