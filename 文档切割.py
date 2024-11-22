import os

def split_document(input_file_path, output_dir):
    with open(input_file_path, 'r', encoding='latin1') as file:
        lines = file.readlines()

    batch_size = 10
    os.makedirs(output_dir, exist_ok=True)
    
    video_count = 0
    batch_lines = []
    batch_index = 1

    for line in lines:
        if line.startswith("Results for"):
            video_count += 1
            if video_count > batch_size:
                output_file_path = os.path.join(output_dir, f'batch_{batch_index}.txt')
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.writelines(batch_lines)
                print(f'Created {output_file_path}')
                batch_lines = []
                video_count = 1
                batch_index += 1
        batch_lines.append(line)
    
    if batch_lines:
        output_file_path = os.path.join(output_dir, f'batch_{batch_index}.txt')
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(batch_lines)
        print(f'Created {output_file_path}')

if __name__ == '__main__':
    input_file_path = 'unique_text_results_only.txt'
    output_dir = 'batches'
    split_document(input_file_path, output_dir)
