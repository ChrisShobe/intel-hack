import fitz  # PyMuPDF
import os

def extract_text_and_note_images(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    output_lines = []

    for page_num, page in enumerate(doc, start=1):
        output_lines.append(f"--- Page {page_num} ---")
        
        text = page.get_text("text")
        if text.strip():
            output_lines.append(text.strip())
        else:
            output_lines.append("[No text found]")

        # Check for images/diagrams
        image_list = page.get_images(full=True)
        if image_list:
            output_lines.append(f"[Note: This page contains {len(image_list)} diagram(s)/image(s)]")

        output_lines.append("")  # Blank line between pages

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"[✓] Extracted {len(doc)} pages and saved to {output_path}")

if __name__ == "__main__":
    pdf_path = "dsa.pdf"  # ← Change this to your actual file
    output_path = "data/pdfoutput.txt"

    extract_text_and_note_images(pdf_path, output_path)