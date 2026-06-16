from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from sentence_transformers import SentenceTransformer

import faiss
import numpy as np


# ==========================================
# LOAD PDF
# ==========================================

pdf_path = "documents/catiaPart1.pdf"

loader = PyPDFLoader(pdf_path)

documents = loader.load()

print(f"\nPages Loaded: {len(documents)}")


# ==========================================
# SPLIT INTO CHUNKS
# ==========================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Chunks Created: {len(chunks)}")


# ==========================================
# LOAD LOCAL EMBEDDING MODEL
# ==========================================

model = SentenceTransformer(
    r"models/all-MiniLM-L6-v2"
)

print("\nEmbedding Model Loaded")


# ==========================================
# CREATE EMBEDDINGS
# ==========================================

texts = [chunk.page_content for chunk in chunks]

embeddings = model.encode(texts)

print(f"Embedding Shape: {embeddings.shape}")


# ==========================================
# CREATE FAISS INDEX
# ==========================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

print(f"Vectors Stored: {index.ntotal}")


# ==========================================
# ASK QUESTION
# ==========================================

query = input("\nAsk a Question: ")

query_embedding = model.encode([query])


# ==========================================
# SEARCH VECTOR DATABASE
# ==========================================

k = 3

distances, indices = index.search(
    np.array(query_embedding),
    k
)


# ==========================================
# DISPLAY RESULTS
# ==========================================

print("\n")
print("=" * 80)
print("TOP MATCHING CHUNKS")
print("=" * 80)

for rank, idx in enumerate(indices[0], start=1):

    print(f"\nResult #{rank}")

    print(f"Distance Score: {distances[0][rank-1]:.4f}")

    print("-" * 80)

    print(chunks[idx].page_content[:300])

    print("\n" + "-" * 80)