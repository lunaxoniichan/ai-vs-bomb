import os
import pdfplumber
import csv
import re
from common.constant import *

images_dir = "./images"
os.makedirs(images_dir, exist_ok=True)

csvs_dir = "./csvs"
os.makedirs(csvs_dir, exist_ok=True)

folder_path = './resources'
os.makedirs(folder_path, exist_ok=True)

os.makedirs(DIR_DATA_ETC, exist_ok=True)

def is_empty_row(row):
    return all(cell is None or cell.strip() == "" for cell in row)

def is_empty_table(table_data):
    if len(table_data) < 2:
        return True
    empty_rows_count = sum(1 for row in table_data if is_empty_row(row))
    if empty_rows_count / len(table_data) > 0.5:
        return True
    return False

def matches_pattern(text):
    return re.match(r'^[A-Z0-9].*:$', text) is not None

def process_lines(words):
    result = ""
    prev_size = None
    min_size_threshold = 14  # min threshold size for title
    max_size_threshold = 19  # max threshold size for title
    line_buffer = []
    last_word = len(words) - 2
    for word_index, word in enumerate(words):
        if word_index == 0 or word_index >= last_word:
            continue
        size_text = int(word["chars"][0]["size"])
        current_text = word["text"].strip()

        # Detect a title
        if size_text >= min_size_threshold and size_text < max_size_threshold:
            if line_buffer:
                result += " ".join(line_buffer) + "\n"
                line_buffer = []
            result += f"\n\n# {current_text}\n"
            prev_size = None
            continue

        # Check for the new line rule
        if matches_pattern(current_text):
            text = " ".join(line_buffer)
            if line_buffer and matches_pattern(text):
                result += text + "\n"
            result += "\n" + current_text + "\n"
            line_buffer = []
            prev_size = size_text
            continue

        if current_text.startswith('"'):
            if line_buffer:
                result += " ".join(line_buffer) + "\n"
            result += current_text + "\n"
            line_buffer = []
            prev_size = size_text
            continue

        # If the size is different, flush the buffer and start a new line
        if prev_size is not None and size_text != prev_size:
            if line_buffer:
                result += " ".join(line_buffer) + "\n"
            line_buffer = [current_text]
        else:
            if line_buffer:
                line_buffer.append(current_text)
            else:
                line_buffer = [current_text]

        # If the current text ends with a punctuation
        if current_text.endswith((".", "?", "!", "…")):
            result += " ".join(line_buffer) + "\n"
            line_buffer = []

        prev_size = size_text
    return result

for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                if page_number < 4 or page_number > 10:
                    continue
                words = page.extract_text_lines()
                processed_text = process_lines(words)

                txt_filename = f"{DIR_DATA_ETC}/page_{page_number + 1}.txt"
                with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(processed_text)
                
                for table_index, table in enumerate(page.find_tables()):
                    table_data = table.extract()
                    if is_empty_table(table_data) or table_index == 0:
                        continue
                    csv_filename = f"{csvs_dir}/table_page_{page_number + 1}_table_{table_index + 1}.csv"
                    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        for row in table_data:
                            writer.writerow(row)
                
                page_image = page.to_image()
                for img_index, image in enumerate(page.images):
                    if img_index == 0:
                        continue
                    x0 = image['x0']
                    top = image['top']
                    x1 = image['x1']
                    bottom = image['bottom']
                    pil_image = page_image.original
                    cropped_image = pil_image.crop((x0, top, x1, bottom))
                    cropped_image.save(f"{images_dir}/image_page_{page_number + 1}_image_{img_index + 1}.png", format="PNG")
