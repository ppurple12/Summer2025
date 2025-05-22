#getting ids
ids = [f'"{str(i).zfill(5)}"' for i in range(1, 702)]
print(', '.join(ids))