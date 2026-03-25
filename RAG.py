from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
# embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.text_splitter = SentenceSplitter(
    chunk_size=512,      # how many tokens per chunk
    chunk_overlap=50)     # overlap between chunks so context isn't lost

STORAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),"store")

def build_index():
    documents = SimpleDirectoryReader(
        input_files=[r"C:\Users\uvais\OneDrive\Desktop\New folder (2)\ResearchAssistant\firstprinciplesthinking.txt"]
    ).load_data()
    
    print(f"Documents loaded: {len(documents)}")        # add this
    print(f"First doc preview: {documents[0].text[:300]}")  # add this
    
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(STORAGE_FOLDER)
    print("Index built and saved.")
    return index
 
def load_index():
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_FOLDER)
    return load_index_from_storage(
        storage_context,
        embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")  # add this
    )
 
def retrieve_context(query: str, top_k: int = 3) -> str:
    # Build index if it doesn't exist, otherwise load from disk
    if not os.path.exists(STORAGE_FOLDER):
        index = build_index()
    else:
        index = load_index()
 
    retriever = index.as_retriever(similarity_top_k=top_k)
    results = retriever.retrieve(query)
    #cleaning window lines
    cleaned = "\n\n".join([r.text.replace("\r\n", "\n").strip() for r in results])
    return cleaned
    
    return results
 #rag test
if __name__ == "__main__":
    context = retrieve_context("is first principle thinking useful?")
    print(context)