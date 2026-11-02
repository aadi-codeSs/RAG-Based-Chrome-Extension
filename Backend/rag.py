import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever


load_dotenv()


def _get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to Backend/.env or your environment variables."
        )

    return api_key


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


def _build_prompt():
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Answer the user's question using only the
            provided webpage context.

            If the answer is not present in the context,
            say that the information was not found on
            the webpage.
            """
        ),
        (
            "user",
            """
            Webpage Content:
            {context}

            Question:
            {question}
            """
        )
    ])


def rag_pipeline(content: str, query: str):

    api_key = _get_api_key()

    # Gemini embedding model
    embedding = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=api_key,
    output_dimensionality=768,
)

    # Gemini LLM
    llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    google_api_key=api_key
)

    # Prompt + LLM + Parser
    prompt = _build_prompt()
    parser = StrOutputParser()

    chain = prompt | llm | parser

    # Convert webpage content into a Document
    doc = Document(page_content=content)

    # Split webpage into chunks
    chunks = splitter.split_documents([doc])

    # Vector database
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding
    )

    # Semantic search
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    # Keyword search
    keyword_search = BM25Retriever.from_documents(chunks)
    keyword_search.k = 3

    # Hybrid search
    final_retriever = EnsembleRetriever(
        retrievers=[
            retriever,
            keyword_search
        ],
        weights=[0.5, 0.5]
    )

    # Retrieve relevant chunks
    retrieved_docs = final_retriever.invoke(query)

    # Build context

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    # Generate answer
    result = chain.invoke({
        "context": context,
        "question": query
    })

    return result
