from app.services.text_processing.cleaner import TextCleaner
from app.services.text_processing.chunker import TextChunker


text = """
    Python is a programming language.


    It is widely used in artificial intelligence,
    web development, automation and data science.
"""


cleaned = TextCleaner.clean(text)

print("=== CLEANING TEST ===")
print(cleaned)

chunker = TextChunker(
    chunk_size=50,
    overlap=10,
)

chunks = chunker.split(cleaned)

print()
print("=== CHUNKING TEST ===")

for chunk in chunks:
    print(
        f"[Chunk {chunk.chunk_index}] "
        f"{chunk.content}"
    )

print()
print(f"Total chunks: {len(chunks)}")
print()
print("=== TEXT PROCESSING TEST PASSED ===")