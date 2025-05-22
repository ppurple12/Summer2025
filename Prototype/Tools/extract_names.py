path = 'C:\\Users\\Evanw\\OneDrive\\Documents\\GitHub\\Summer2025\\Prototype\\Inputs\\zemployee_review_mturk_dataset_test_v6_kaggle.csv'

second_elements = set()

with open(path, 'r', encoding='utf-8') as file:
    for line in file:
        values = line.strip().split(",")
        if len(values) > 1:
            cleaned = values[1].strip().strip('"')
            if cleaned:
                second_elements.add(cleaned)

output = ",".join(f'"{value}"' for value in sorted(second_elements))
print(output)