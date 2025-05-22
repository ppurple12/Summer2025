
                    all_data.append(load_pdf(file_path))
                if fname.endswith(".xlsx"):
                    all_data.extend(load_excel(file_path))  # each row as one item
                elif fname.endswith(".csv"):
                    all_data.extend(load_csv(file_path))    # each row as one item
                elif fname.endswith(".txt"):
                    all_data.append(load_txt(file_path))
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
    
    return all_data

print(load_all_files(r"C:\Users\Evanw\OneDrive\Documents\GitHub\Summer2025\Prototy