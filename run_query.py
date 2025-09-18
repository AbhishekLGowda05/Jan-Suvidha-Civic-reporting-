import chromadb
from sentence_transformers import SentenceTransformer

# This query is generic, but the agent's filter will make it specific
user_query = "What are the biggest problems right now?"
model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.PersistentClient(path="./scah_vectordb")
collection = client.get_collection(name="scah_reports")

query_embedding = model.encode(user_query).tolist()

# The BBMP agent applies a 'where' filter to only search BBMP documents
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2,
    where={"department": "BBMP"} # THIS IS THE MULTI-AGENT MAGIC
)

print("BBMP Agent found the following relevant reports:")
for i, doc in enumerate(results['documents'][0]):
    report_id = results['ids'][0][i]
    print(f"  - Report ID: {report_id}, Description: '{doc}'")