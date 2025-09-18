# manager/test_direct_query.py
import sys
import os
import chromadb
from sentence_transformers import SentenceTransformer

def test_direct_query():
    try:
        # Change to parent directory for database path
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(parent_dir, "scah_vectordb")
        print(f"Looking for database at: {db_path}")
        
        # Test direct access to ChromaDB
        client = chromadb.PersistentClient(path=db_path)
        
        try:
            collection = client.get_collection(name="scah_reports")
        except Exception as e:
            print(f"Collection doesn't exist: {e}")
            print("Available collections:", client.list_collections())
            return
        
        count = collection.count()
        print(f"Collection exists with {count} documents")
        
        if count == 0:
            print("No documents found in collection!")
            return
        
        # Get some sample data
        sample_data = collection.get(limit=min(10, count))
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
        print("\nTesting query...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode("road problems").tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={"department": "BBMP"}
        )
        
        print(f"Query results for BBMP: {len(results['ids'][0])} matches")
        if results['ids'][0]:
            for doc_id, doc in zip(results['ids'][0], results['documents'][0]):
                print(f"  ID: {doc_id}, Doc: {doc[:100]}...")
        else:
            print("No BBMP documents found!")
            
        # Test other departments
        for dept in ["BESCOM", "BTP", "BWSSB"]:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=1,
                where={"department": dept}
            )
            print(f"{dept} documents: {len(results['ids'][0])}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_query()