# tools/tools.py

import psycopg2
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from decimal import Decimal # <--- IMPORT THE DECIMAL TYPE

# --- SINGLETON INSTANCES ---
_embedding_model = None
_chroma_client = None
_report_collection = None

# ... (The get_embedding_model and get_report_collection functions remain the same) ...

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
        print("Initializing ChromaDB client for the first time...")
        _chroma_client = chromadb.PersistentClient(path="./scah_vectordb")
        _report_collection = _client.get_or_create_collection(name="scah_reports")
        print("ChromaDB client ready.")
    return _report_collection


def query_vector_database(query_text: str, department: str, n_results: int = 5) -> List[str]:
    """
    Queries the vector database to find relevant report IDs.
    """
    try:
        model = get_embedding_model()
        collection = get_report_collection()
        query_embedding = model.encode(query_text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"department": department}
        )
        return results.get('ids', [[]])[0]
    except Exception as e:
        print(f"Error querying vector database: {e}")
        return []

def get_report_details_from_db(report_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches full details from PostgreSQL.
    """
    if not report_ids:
        return []
    int_report_ids = [int(id) for id in report_ids]
    conn = None
    try:
        conn = psycopg2.connect(f"dbname=scah_prototype user=abhisheklgowda")
        cur = conn.cursor()
        query = "SELECT report_id, description, category, status, latitude, longitude FROM Citizen_Reports WHERE report_id = ANY(%s);"
        cur.execute(query, (int_report_ids,))
        reports = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        report_details = [dict(zip(columns, report)) for report in reports]

        # --- THIS IS THE FIX ---
        # Iterate through the results and convert any Decimal types to float
        for report in report_details:
            for key, value in report.items():
                if isinstance(value, Decimal):
                    report[key] = float(value)
        # --- END OF FIX ---

        return report_details
    except Exception as e:
        print(f"Error fetching from PostgreSQL: {e}")
        return []
    finally:
        if conn:
            conn.close()