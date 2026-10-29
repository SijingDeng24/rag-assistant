import chromadb
from app.ingest import extract_pages, chunk_pages

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="lab_reports")

def build_index(chunks: list[dict]) -> None:
    ids, documents, metadatas = [], [], []
    for chunk in chunks:
        ids.append(f"{chunk['source']}-p{chunk['page']}-c{chunk['chunk_index']}")   # a unique ID string for this chunk
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "page": chunk["page"],
            "chunk_index": chunk["chunk_index"],
        })
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

def search(question: str, k: int = 3) -> list[dict]:
    results = collection.query(query_texts=[question], n_results=k)
    hits = []
    for text, meta, dist in zip(results["documents"][0],
                                results["metadatas"][0],
                                results["distances"][0]):
        hits.append({"text": text, "distance": dist, **meta})
    return hits

if __name__ == "__main__":
    pages = extract_pages("data/Sijing_Deng_FPGA_RISC-V_Lab_Reports_Portfolio.pdf")
    chunks = chunk_pages(pages, chunk_size=800, overlap=150)
    build_index(chunks)
    print("indexed", len(chunks), "chunks")
    for hit in search("How is signed overflow detected?"):
        print(hit["page"], round(hit["distance"], 3), hit["text"][:100])

    results = search("How is signed overflow detected?")
    print(results[0]["text"])