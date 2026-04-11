import pandas as pd
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Path where the vector database will be saved
VECTORDB_PATH = "knowledge_base/security_vectordb"

def build_knowledge_base():
    """
    Reads your cleaned NVD dataset and converts every row
    into a searchable document in FAISS.
    Run this ONCE to create the database.
    After that, just call load_knowledge_base().
    """
    print("Building knowledge base from NVD dataset...")
    print("This will take 2-5 minutes the first time (downloading embedding model)")

    # Load your cleaned + labelled dataset
    df = pd.read_csv("data/labelled_dataset.csv")
    print(f"Loaded {len(df)} CVE entries")

    # Convert each row into a LangChain Document
    # Each document = one CVE entry with its description and metadata
    documents = []
    skipped = 0
    for _, row in df.iterrows():
        try:
            cvss = float(row['CVSS Score'])
        except (ValueError, TypeError):
            skipped += 1
            continue  # skip malformed rows

        content = (
            f"CVE: {row['CVE ID']}\n"
            f"Type: {row['label']}\n"
            f"Severity: {row['severity']} (CVSS: {cvss})\n"
            f"Platform: {row['platform']}\n"
            f"Attack Vector: {row['attack_vector']}\n"
            f"Description: {row['Description']}"
        )
        doc = Document(
            page_content=content,
            metadata={
                "cve_id":   str(row['CVE ID']),
                "label":    str(row['label']),
                "severity": str(row['severity']),
                "cvss":     cvss
            }
        )
        documents.append(doc)

    if skipped:
        print(f"Skipped {skipped} malformed rows (bad CVSS Score)")

    # Load the free HuggingFace embedding model
    # First run downloads ~22MB model — subsequent runs use cache
    print("Loading embedding model (downloads once)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

    # Build FAISS vector database and save to disk
    print("Building FAISS index (this is the slow part)...")
    vectordb = FAISS.from_documents(documents, embeddings)
    os.makedirs(VECTORDB_PATH, exist_ok=True)
    vectordb.save_local(VECTORDB_PATH)

    print(f"\nKnowledge base built successfully!")
    print(f"Saved to: {VECTORDB_PATH}")
    print(f"Total documents indexed: {len(documents)}")
    return vectordb


def load_knowledge_base():
    """
    Loads the saved FAISS database.
    If it does not exist yet, builds it first.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    if os.path.exists(VECTORDB_PATH):
        return FAISS.load_local(
            VECTORDB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Knowledge base not found — building it now...")
        return build_knowledge_base()


def search_knowledge_base(query: str, k: int = 3, label_filter: str = None):
    """
    Search the knowledge base for the most relevant CVE entries.

    query        — what you are searching for (e.g. "SQL injection fix")
    k            — how many results to return (default 3)
    label_filter — optional: only return entries of a specific type
                   e.g. label_filter="sqli" returns only SQL injection entries

    Returns a list of Document objects with page_content and metadata.
    """
    db = load_knowledge_base()

    if label_filter:
        # Search with a filter on the label metadata
        results = db.similarity_search(
            query, k=k,
            filter={"label": label_filter}
        )
    else:
        results = db.similarity_search(query, k=k)

    return results


# Run directly to build the knowledge base
if __name__ == "__main__":
    build_knowledge_base()

    # Test it works
    print("\nTest search: 'SQL injection fix'")
    results = search_knowledge_base("SQL injection fix", k=2)
    for r in results:
        print(f"\n--- {r.metadata['cve_id']} ({r.metadata['label']}) ---")
        print(r.page_content[:200])