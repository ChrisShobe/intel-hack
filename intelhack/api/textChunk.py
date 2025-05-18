import re

def remove_sections(text, keywords=['table of contents', 'bibliography', 'references']):
    for kw in keywords:
        idx = text.lower().find(kw)
        if idx != -1:
            text = text[:idx]
    return text

def normalize_text(text):
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text

def adaptive_chunk_size(text, base_chunk=300, max_chunk=2000):
    word_count = len(text.split())
    scale_factor = min((word_count / 2000), (max_chunk / base_chunk))
    return int(base_chunk * scale_factor)

def chunk_text(text, chunk_size=500, overlap=20):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(' '.join(chunk))
        i += chunk_size - overlap
    return chunks

def process_text_and_chunk(text_path, output_path):
    with open(text_path, 'r') as file:
        text = file.read()

    text = remove_sections(text)
    text = normalize_text(text)

    chunk_size = min(adaptive_chunk_size(text), 2000)
    overlap = int(chunk_size * 0.15)

    sections = re.split(r'\n{2,}', text)
    all_chunks = []
    for section in sections:
        cleaned = section.strip()
        if len(cleaned.split()) > 50:
            all_chunks.extend(chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap))

    with open(output_path, 'w') as f:
        for i, chunk in enumerate(all_chunks):
            f.write(f"\n--- Chunk {i + 1} ---\n")
            f.write(chunk + '\n')

    print(f"[✓] Saved {len(all_chunks)} chunks to {output_path}")