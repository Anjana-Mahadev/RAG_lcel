import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# ==============================
# LLM
# ==============================

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# ==============================
# Embeddings + Vectorstore
# ==============================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "vectorstore",
    embedding_model,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ==============================
# Memory
# ==============================

memory = ConversationBufferMemory(
    return_messages=True
)

# ==============================
# Prompt
# ==============================

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Conversation History:
{history}

Context:
{context}

Question:
{question}

Answer clearly and only from the context.
""")

# ==============================
# RAG Chain
# ==============================

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
        "history": lambda x: memory.load_memory_variables({})["history"]
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ==============================
# Main Function
# ==============================

def ask_question(question: str):
    docs = retriever.invoke(question)
    answer = rag_chain.invoke(question)

    memory.save_context(
        {"input": question},
        {"output": answer}
    )

    return {
        "answer": answer,
        "contexts": [doc.page_content for doc in docs]
    }