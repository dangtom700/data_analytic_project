import ollama

with open("finetuned_data.txt", "r", encoding="utf-8") as f:
    dataset = f.readlines()

with open("embedded_output.txt", "w", encoding="utf-8") as f:
    for data in dataset:
        embedded = ollama.embeddings(model='nomic-embed-text', prompt=data)
        print(len(embedded.embedding), end=", ")