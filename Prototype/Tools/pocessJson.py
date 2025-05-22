import json
import csv

# Open CSV file for writing
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['id', 'content'])  # Header

    # read JSON lines and write to CSV
    with open('Prototype/Tools/training_resumes.json', 'r', encoding='utf-8') as infile:

        for i, line in enumerate(infile, start=1):
            try:
                item = json.loads(line)
                id_str = str(i).zfill(5)  # Zero-padded ID
                writer.writerow([id_str, item.get('content', '')])
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line {i}")

# get names from resumes
import json
names = []

with open('Prototype/Tools/training_resumes.json', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        content = item.get('content', '')
        first_line = content.strip().split('\n')[0]
        names.append(f'"{first_line}"')

# output names as comma-separated values in quotes
print(', '.join(names))

#getting ids
ids = [f'"{str(i).zfill(5)}"' for i in range(1, 702)]
print(', '.join(ids))