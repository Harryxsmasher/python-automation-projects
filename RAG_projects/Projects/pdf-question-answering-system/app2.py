from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    r"models/all-MiniLM-L6-v2"
)

embedding = model.encode("CATIA Part Design Workbench")

print(len(embedding))
print(embedding[:10])