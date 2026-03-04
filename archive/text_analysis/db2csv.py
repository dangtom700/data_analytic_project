import sqlite3
from pathlib import Path

SOURCE_FOLDER = Path("D:/READING LIST")
DESTINATION_FOLDER = SOURCE_FOLDER / "notes"
DB_PATH = "pdf_text.db"


def scan_all_pdf_files(reset=False):
    pdf_files = [f for f in SOURCE_FOLDER.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"]
    if reset:
        return pdf_files
    
    return [f for f in pdf_files if not (DESTINATION_FOLDER / f"BOOK {f.stem}.md").exists()]


def get_random_chunks(db, filename, limit=3):
    query = """
        SELECT chunk_id, chunk_text
        FROM pdf_chunks
        WHERE file_name = ?
        ORDER BY RANDOM()
        LIMIT ?
    """
    return db.execute(query, (filename, limit)).fetchall()


def get_recommendations(db, filename, limit=150, min_distance=0.5):
    query = """
        SELECT target_name AS other, distance
        FROM item_matrix_filtered
        WHERE source_name = ?
          AND distance > ?

        UNION ALL

        SELECT source_name AS other, distance
        FROM item_matrix_filtered
        WHERE target_name = ?
          AND distance > ?

        ORDER BY distance DESC
        LIMIT ?
    """
    rows = db.execute(
        query,
        (filename, min_distance, filename, min_distance, limit)
    ).fetchall()

    return sorted({other for other, _ in rows if other != filename})


def main(reset=False):
    DESTINATION_FOLDER.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as db:
        pdf_list = scan_all_pdf_files(reset = reset)
        storage = len(pdf_list)

        for index, pdf_path in enumerate(pdf_list, start=1):
            pdf_name = pdf_path.name
            base_name = pdf_path.stem
            txt_name = f"{base_name}.txt"

            output_file = DESTINATION_FOLDER / f"BOOK {base_name}.md"
            print(f"Processing {base_name}... ({index} of {storage})")

            chunks = get_random_chunks(db, txt_name)
            recommendations = get_recommendations(db, base_name)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# BOOK: {base_name}\n\n")
                f.write(f"Source: [[{pdf_name}]]\n\n")

                for chunk_id, chunk_text in chunks:
                    f.write(f"> {chunk_id} - {base_name}\n")
                    f.write(f"> {chunk_text.strip()}\n\n")

                if recommendations:
                    f.write("## Recommended Reading\n\n")
                    f.write("| # | PDF | Notes |\n")
                    f.write("|---|-----|-------|\n")

                    for i, rec in enumerate(recommendations, start=1):
                        f.write(
                            f"| {i} | [[{rec}.pdf]] | [[BOOK {rec}.md]] |\n"
                        )

    print("Done.")

def prepare_filtered_table(
    DB_PATH="pdf_text.db",
    DISTANCE_THRESHOLD=0.5,
    reset=True
):
    # Check if reset is requested
    if reset:
        with sqlite3.connect(DB_PATH) as db:
            db.execute("DROP TABLE IF EXISTS item_matrix_filtered;")
            db.commit()
        print("Existing filtered table dropped.")
    
    with sqlite3.connect(DB_PATH) as db:
        db.execute("PRAGMA journal_mode=WAL;")
        db.execute("PRAGMA synchronous=NORMAL;")

        # Create filtered table if it does not exist
        db.execute("""
            CREATE TABLE IF NOT EXISTS item_matrix_filtered (
                source_name TEXT NOT NULL,
                target_name TEXT NOT NULL,
                distance REAL NOT NULL,
                PRIMARY KEY (source_name, target_name)
            );
        """)

        # Optional but strongly recommended indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_imf_source_distance
            ON item_matrix_filtered(source_name, distance DESC);
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_imf_target_distance
            ON item_matrix_filtered(target_name, distance DESC);
        """)

        # Clear existing data to avoid duplicates
        db.execute("DELETE FROM item_matrix_filtered;")

        # One-shot insert
        db.execute(
            """
            INSERT OR IGNORE INTO item_matrix_filtered (source_name, target_name, distance)
            SELECT source_name, target_name, distance
            FROM item_matrix
            WHERE distance > ?;
            """,
            (DISTANCE_THRESHOLD,),
        )

        db.commit()

    print("Filtered table created and populated in one go.")


if __name__ == "__main__":
    reset = True
    prepare_filtered_table(reset = reset)
    main(reset = reset)
