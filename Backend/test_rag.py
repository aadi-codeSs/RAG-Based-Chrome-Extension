from rag import rag_pipeline

content = """
Python is a programming language used for web development,
data science, machine learning, and automation.
"""

query = "What is Python used for?"

print("Starting RAG...")
result = rag_pipeline(content, query)

print("\nRESULT:")
print(result)