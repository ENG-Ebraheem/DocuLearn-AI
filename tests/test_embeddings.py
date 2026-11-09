from app.rag.embedding_service import EmbeddingService


print("=== EMBEDDING TEST ===")

embedding_service = EmbeddingService()

text = "Python is a programming language."

vector = embedding_service.embed_text(text)

print(f"Text: {text}")
print(f"Vector type: {type(vector)}")
print(f"Vector dimensions: {len(vector)}")

print()
print("First 10 values:")

print(vector[:10])

print()
print("=== EMBEDDING TEST PASSED ===")