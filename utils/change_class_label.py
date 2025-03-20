import os
import argparse
import shutil
import datetime

def normalize_word(word):
    return word.lower().replace(" ", "_")

def process_classes_file(file_path, input_word, replace_word):
    backup_created = False
    normalized_input = normalize_word(input_word)

    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    modified_lines = []
    changed = False
    
    for line in lines:
        if input_word.lower() == normalize_word(line):
            changed = True
            print(input_word, line)
            modified_lines.append(replace_word)
        else:
            modified_lines.append(line)

    print(modified_lines)

    if changed:
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(dir_name, f"orig_classes_{timestamp}.txt")
        shutil.copy(file_path, backup_path)
        backup_created = True
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(modified_lines) + "\n")
    
    return backup_created

def rename_image_files(base_path, input_word, replace_word):
    normalized_input = normalize_word(input_word) + ".png"
    replace_file_name = replace_word + ".png"
    
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            for file_name in os.listdir(item_path):
                if normalize_word(file_name) == normalized_input:
                    old_file_path = os.path.join(item_path, file_name)
                    new_file_path = os.path.join(item_path, replace_file_name)
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed {old_file_path} -> {new_file_path}")

def main():
    parser = argparse.ArgumentParser(description='Replace words in classes.txt and rename matching images.')
    parser.add_argument('--label', type=str, default='classes.txt', help='Path to the classes.txt file')
    parser.add_argument('--input_word', "-i", type=str, required=True, help='Word to be replaced')
    parser.add_argument('--replace_word', "-r", type=str, required=True, help='Replacement word')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.label):
        print(f"Error: {args.label} not found.")
        return
    
    base_path = os.path.dirname(os.path.abspath(args.label))
    
    changed = process_classes_file(args.label, args.input_word, args.replace_word)
    if changed:
        print(f"Updated {args.label} and created a backup.")
    
    rename_image_files(base_path, args.input_word, args.replace_word)
    print("Processing completed.")

if __name__ == '__main__':
    main()
