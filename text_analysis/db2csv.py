import sqlite3
import csv

conn = sqlite3.connect('pdf_text_2025_07_28.db')
c = conn.cursor()
c.execute('''
    SELECT target_name, source_name, distance
    FROM item_matrix
''')
rows = c.fetchall()

with open('item_matrix.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['target_name', 'source_name', 'distance'])
    writer.writerows(rows)