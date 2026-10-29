from pathlib import Path
from pypdf import PdfReader

def extract_pages(pdf_path: str) -> list[dict]:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"source": Path(pdf_path).name, "page": i, "text": text})
    return pages

def chunk_pages(pages: list[dict], chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    result = []
    step = chunk_size - overlap
    for page in pages:
        
        text = " ".join(page["text"].split())
        if len(text) < 100:
            continue
        for i, start in enumerate(range(0, len(text), step)):
             # range(0, 16, 4) produces start: 0, 4, 8, 12
             # i : cuhnk number
             # i = 0: first chunk; i = 1: second chunk
            chunk_text = text[start: start + chunk_size]
            result.append({
                "source": page["source"],
                "page": page["page"],
                "chunk_size": chunk_size,
                "chunk_index": i,
                "text": chunk_text,
            })
    return result



# if __name__ == "__main__":
#     pages = extract_pages("data/Sijing_Deng_FPGA_RISC-V_Lab_Reports_Portfolio.pdf")
#     print(f"{len(pages)} pages")
#     print(pages[0])
#     lengths = [len(p["text"]) for p in pages]
#     print("min:", min(lengths), "max:", max(lengths), "avg:", sum(lengths) // len(lengths))
#     print(pages[10]["text"])

#     text = " ".join(pages[10]["text"].split())
#     start = text.find("Signed addition")
#     print("length:", len(text), "start:", start)
#     print("--- 160 chars ---")
#     print(text[start:start + 160])
#     print("--- 800 chars ---")
#     print(text[start:start + 800])

#     print("--- test on ABCDEFGHIJKLMNOP---")
#     test_pages = [{"source": "test.pdf", "page": 1, "text": "ABCDEFGHIJKLMNOP"}]
#     print(chunk_pages(test_pages, chunk_size=6, overlap=2))



# if __name__ == "__main__":
#     fake_pages = [
#         {"source": "test.pdf", "page": 1, "text": "ABCDEFGHIJKLMNOP"},
#         {"source": "test.pdf", "page": 2, "text": "QRSTUVWX"},
#     ]
#     for chunk in chunk_pages(fake_pages, chunk_size=6, overlap=2):
#         print(chunk)


if __name__ == "__main__":
    pages = extract_pages("data/Sijing_Deng_FPGA_RISC-V_Lab_Reports_Portfolio.pdf")
    short_pages = []
    for page in pages:
        clean = " ".join(page["text"].split())
        if len(clean) < 100:
            short_pages.append(page["page"])
    print(short_pages)
    print(pages[56]["text"])
    print(pages[57]["text"])
    print(pages[58]["text"])
