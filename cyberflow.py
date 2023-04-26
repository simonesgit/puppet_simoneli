import pandas as pd

def process_file(file_path):
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(('HIGH', 'MEDIUM', 'LOW')):
                line_parts = line.split('\t')
                rating, id, finding, description, source = [part.strip() for part in line_parts]
                i += 1
                line = lines[i].strip()
                if line.startswith('Solution'):
                    i += 1
                    solution = lines[i].strip() if not lines[i].strip().startswith('Location') else ''
                    i += 1
                else:
                    solution = ''
                if i < len(lines) and lines[i].strip().startswith('Location'):
                    i += 1
                    location = lines[i].strip() if not lines[i].strip().startswith(('HIGH', 'MEDIUM', 'LOW')) else ''
                    i += 1
                else:
                    location = ''
                data.append([rating, id, finding, description, source, solution, location])
            else:
                i += 1
    return pd.DataFrame(data, columns=['Rating', 'ID', 'Finding', 'Description', 'Source', 'Solution', 'Location'])

df = process_file('tmp.txt')
print(df)
