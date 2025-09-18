# test_direct_query.py
import chromadb
from sentence_transformers import SentenceTransformer

def test_direct_query():
    try:
        # Test direct access to ChromaDB
        client = chromadb.PersistentClient(path="./scah_vectordb")
        collection = client.get_collection(name="scah_reports")
        
        print(f"Collection exists with {collection.count()} documents")
        
        # Get some sample data
        sample_data = collection.get(limit=10)
        print(f"Sample documents: {len(sample_data['documents'])}")
        
        for i, (doc_id, doc, metadata) in enumerate(zip(
            sample_data['ids'], 
            sample_data['documents'], 
            sample_data['metadatas']
        )):
            print(f"ID: {doc_id}")
            print(f"Department: {metadata.get('department', 'N/A')}")
            print(f"Document: {doc[:100]}...")
            print("---")
            if i >= 2:  # Just show first 3
                break
        
        # Test a query
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode("road problems").tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={"department": "BBMP"}
        )
        
        print(f"\nQuery results for BBMP: {len(results['ids'][0])} matches")
        for doc_id, doc in zip(results['ids'][0], results['documents'][0]):
            print(f"  ID: {doc_id}, Doc: {doc[:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_query()