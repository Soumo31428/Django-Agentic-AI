import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

# Initialize chromadb client
client = chromadb.PersistentClient(path="./chroma_db")

embedding_fn = DefaultEmbeddingFunction()

#get or create collection - just like table in regular db

collection = client.get_or_create_collection(
    name="coolbreeze_docs",
    embedding_function=embedding_fn
)

