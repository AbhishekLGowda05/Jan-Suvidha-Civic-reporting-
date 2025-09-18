# manager/tools/tools.py

import os
import psycopg2
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from decimal import Decimal

# --- SINGLETON INSTANCES ---
_embedding_model = None
_chroma_client = None
_report_collection = None

def get_database_path():
    """Get the correct path to the vector database"""
    current_file = os.path.abspath(__file__)
    # Go up from tools/tools.py to manager/ to project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    return os.path.join(project_root, "scah_vectordb")

def get_embedding_model():
    """
    Loads the SentenceTransformer model only once.
    """
    global _embedding_model
    if _embedding_model is None:
        print("Loading embedding model for the first time...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded and ready.")
    return _embedding_model

def get_report_collection():
    """
    Initializes the ChromaDB client and gets the collection only once.
    """
    global _chroma_client, _report_collection
    if _report_collection is None:
        db_path = get_database_path()
        print(f"Initializing ChromaDB client at: {db_path}")
        _chroma_client = chromadb.PersistentClient(path=db_path)
        _report_collection = _chroma_client.get_or_create_collection(name="scah_reports")
        print("ChromaDB client ready.")
    return _report_collection


def query_vector_database(query_text: str, department: str, n_results: int = 5) -> List[str]:
    """
    Queries the vector database to find relevant report IDs.
    """
    try:
        print(f"Querying vector database for department: {department}")
        print(f"Query text: {query_text}")
        
        model = get_embedding_model()
        collection = get_report_collection()
        
        # Check if collection has any documents
        collection_count = collection.count()
        print(f"Total documents in collection: {collection_count}")
        
        if collection_count == 0:
            print("No documents found in vector database!")
            return []
        
        query_embedding = model.encode(query_text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"department": department}
        )
        
        found_ids = results.get('ids', [[]])[0]
        print(f"Found {len(found_ids)} matching reports for {department}")
        
        return found_ids
    except Exception as e:
        print(f"Error querying vector database: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_report_details_from_db(report_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches full details from PostgreSQL.
    """
    if not report_ids:
        print("No report IDs provided")
        return []
        
    print(f"Fetching details for report IDs: {report_ids}")
    
    try:
        int_report_ids = [int(id) for id in report_ids]
    except ValueError as e:
        print(f"Error converting report IDs to integers: {e}")
        return []
    
    conn = None
    try:
        # Make connection string consistent
        conn = psycopg2.connect("dbname=scah_prototype user=abhisheklgowda")
        cur = conn.cursor()
        
        query = "SELECT report_id, description, category, status, latitude, longitude, department FROM Citizen_Reports WHERE report_id = ANY(%s);"
        cur.execute(query, (int_report_ids,))
        reports = cur.fetchall()
        
        print(f"Retrieved {len(reports)} reports from PostgreSQL")
        
        columns = [desc[0] for desc in cur.description]
        report_details = [dict(zip(columns, report)) for report in reports]

        # Convert any Decimal types to float
        for report in report_details:
            for key, value in report.items():
                if isinstance(value, Decimal):
                    report[key] = float(value)

        return report_details
    except Exception as e:
        print(f"Error fetching from PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()

# Add a debugging function
def debug_database_status():
    """
    Debug function to check database status
    """
    try:
        db_path = get_database_path()
        print(f"Database path: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"ERROR: Database directory does not exist at {db_path}")
            return
        
        # Check ChromaDB
        client = chromadb.PersistentClient(path=db_path)
        
        try:
            collection = client.get_collection(name="scah_reports")
        except Exception as e:
            print(f"Collection 'scah_reports' not found: {e}")
            collections = client.list_collections()
            print(f"Available collections: {[c.name for c in collections]}")
            return
            
        count = collection.count()
        print(f"ChromaDB has {count} documents")
        
        # Get a few sample documents to check departments
        if count > 0:
            sample = collection.get(limit=5)
            print("Sample documents:")
            for i, (doc_id, metadata) in enumerate(zip(sample['ids'], sample['metadatas'])):
                print(f"  ID: {doc_id}, Department: {metadata.get('department', 'N/A')}")
        else:
            print("No documents in collection!")
            return
        
        # Check PostgreSQL
        try:
            conn = psycopg2.connect("dbname=scah_prototype user=abhisheklgowda")
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Citizen_Reports;")
            pg_count = cur.fetchone()[0]
            print(f"PostgreSQL has {pg_count} reports")
            
            cur.execute("SELECT DISTINCT department FROM Citizen_Reports;")
            departments = cur.fetchall()
            print(f"Departments in PostgreSQL: {[dept[0] for dept in departments]}")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
        
    except Exception as e:
        print(f"Error during debug: {e}")
        import traceback
        traceback.print_exc()