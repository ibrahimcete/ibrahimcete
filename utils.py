# utils.py

def print_header(title):
    print("\n" + "="*40)
    print(title)
    print("="*40)

def dedup_list(items):
    return list(set(items))
