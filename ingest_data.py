import chromadb
import psycopg2
from sentence_transformers import SentenceTransformer

print("Connecting to PostgreSQL to fetch reports...")
# Notice the new 'department' column in the SELECT query
conn = psycopg2.connect("dbname=scah_prototype user=abhisheklgowda") # Replace with your Mac username
cur = conn.cursor()
cur.execute("SELECT report_id, description, department FROM Citizen_Reports;")
reports = cur.fetchall()
cur.close()
conn.close()

report_ids = [str(report[0]) for report in reports]
report_descriptions = [report[1] for report in reports]
report_departments = [report[2] for report in reports] # Get the department
print(f"Found {len(reports)} reports to process.")

print("Loading sentence-transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(report_descriptions).tolist()
print("Created embeddings for all reports.")

client = chromadb.PersistentClient(path="./scah_vectordb")
collection = client.get_or_create_collection(name="scah_reports")

# The key change is here: adding the department to the metadata
metadatas = [{'department': dept} for dept in report_departments]

collection.add(
    embeddings=embeddings,
    documents=report_descriptions,
    metadatas=metadatas,
    ids=report_ids
)
print("✅ Success! Your department-aware vector database is ready.")