import os
import pdfplumber
import csv
import re

images_dir = "./images"
os.makedirs(images_dir, exist_ok=True)

csvs_dir = "./csvs"
os.makedirs(csvs_dir, exist_ok=True)

folder_path = './docs'
os.makedirs(folder_path, exist_ok=True)

pages_dir = "./pages"
os.makedirs(pages_dir, exist_ok=True)

def is_empty_row(row):
    return all(cell is None or cell.strip() == "" for cell in row)

def is_empty_table(table_data):
    if len(table_data) < 2:
        return True
    empty_rows_count = sum(1 for row in table_data if is_empty_row(row))
    if empty_rows_count / len(table_data) > 0.5:
        return True
    return False

def is_sentence(text):
    return re.match(r'^[A-Z0-9].*[.!?…:]\s*$', text.strip())

for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                # if page_number < 2:
                #     continue
                result = ""
                words = page.extract_text_lines()
                text = ""
                size = 0
                last_word = len(words) - 2
                for word_index, word in enumerate(words):
                    if word_index == 0 or word_index >= last_word:
                        continue
                    w_size = int(word["chars"][0]["size"])
                    current_text = word['text'].strip()
                    if is_sentence(current_text):  
                        if text:
                            result += "\n" + text.replace("\n", " ")
                        text = current_text
                    else:
                        if text and (is_sentence(text) or (size != 0 and size != w_size)):
                            result += "\n" + text.replace("\n", " ")
                            text = current_text
                        else:
                            text += " " + current_text
                    size = w_size
                
                if text and is_sentence(text):
                    result += "\n" + text

                txt_filename = f"{pages_dir}/page_{page_number + 1}.txt"
                with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(result)
                
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
