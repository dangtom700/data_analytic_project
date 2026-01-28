import sqlite3
from pathlib import Path

SOURCE_FOLDER = Path("D:/READING LIST")
DESTINATION_FOLDER = Path("D:/READING LIST/notes")
DB_PATH = "pdf_text.db"


def scan_all_pdf_files():
    return [f for f in SOURCE_FOLDER.iterdir() if f.suffix.lower() == ".pdf"]


def get_random_chunks(db, filename, limit=3):
    """
    Fetch random text chunks belonging to a given file.
    """
    query = """
        SELECT chunk_id, chunk_text
        FROM pdf_chunks
        WHERE file_name = ?
        ORDER BY RANDOM()
        LIMIT ?
    """
    cursor = db.execute(query, (filename, limit))
    return cursor.fetchall()


def main():
    DESTINATION_FOLDER.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as db:
        for pdf_path in scan_all_pdf_files():
            pdf_name = pdf_path.name
            txt_name = pdf_name.replace(".pdf", ".txt")

            output_file = DESTINATION_FOLDER / f"BOOK {pdf_name}.md"
            print(f"Processing {pdf_name}...")

            chunks = get_random_chunks(db, txt_name)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# BOOK: {pdf_name}\n\n")
                f.write(f"Source: [[{pdf_name}]]\n\n")

                for chunk_id, chunk_text in chunks:
                    f.write(f"> {chunk_id} - {pdf_name}\n")
                    f.write(f"> {chunk_text}\n\n\n")

    print("Done.")


if __name__ == "__main__":
    main()
