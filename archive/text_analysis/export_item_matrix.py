import sqlite3
import csv

def export_in_batches(db_path, output_file, batch_size=5000):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query (this puts the DB in a "ready" state but doesn't load data yet)
    cursor.execute("SELECT * FROM item_matrix")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 1. Write the Header
        # cursor.description contains column info. We extract the names (index 0).
        headers = [description[0] for description in cursor.description]
        writer.writerow(headers)
        
        # 2. Loop in Batches
        while True:
            # Fetch a specific number of rows
            rows = cursor.fetchmany(batch_size)
            
            # If fetchmany returns an empty list, we have reached the end
            if not rows:
                break
                
            # Write this batch to the CSV
            writer.writerows(rows)

    conn.close()
    print("Export complete.")

def import_in_batches(db_path, input_file, batch_size=10000):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # 1. Read the Header
        headers = next(reader)  # This reads the first line (header)
        
        # 2. Loop in Batches
        batch = []
        for row in reader:
            batch.append(row)
            if len(batch) >= batch_size:
                # Insert this batch into the database
                cursor.executemany("INSERT INTO item_matrix VALUES (?, ?, ?, ?)", batch)  # Adjust placeholders as needed
                conn.commit()
                batch = []  # Clear the batch
        
        # Insert any remaining rows
        if batch:
            cursor.executemany("INSERT INTO item_matrix VALUES (?, ?, ?, ?)", batch)  # Adjust placeholders as needed
            conn.commit()
# Usage
# export_in_batches('pdf_text.db', 'item_matrix.csv')
import_in_batches('data/pdf_text.db', 'data/item_matrix.csv')