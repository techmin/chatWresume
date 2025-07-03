file_path = 'AS_KB.txt'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        print("reading file") 
        for i, line in enumerate(f, 1):
            print(f"Line {i}: {line.rstrip()}")
except Exception as e:
    print(f"Error reading file: {e}")
