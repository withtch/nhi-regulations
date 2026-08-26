import os
import re
import sqlite3
import pdfplumber

DB_FILE = "nhi_rules.db"
DOWNLOAD_DIR = "nhi_files"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS rules')
    cursor.execute('''
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT,
            section_no TEXT,
            ingredient_name TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def split_text_into_sections(full_text):
    # 正則表達式：捕捉行首或文字間的「數字.數字.」大章節 (例: 7.1. 或 1.1.)
    pattern = r'(?=(?:\n|\s{2,})\d+\.\d+(?:\.\d+)*\.\s+)'
    
    raw_chunks = re.split(pattern, full_text)
    sections = []
    
    for chunk in raw_chunks:
        chunk_clean = chunk.strip()
        if len(chunk_clean) < 15:
            continue
            
        lines = chunk_clean.split("\n")
        header_line = lines[0].strip()
        
        # 捕捉標準章節號 (如 7.1 或 1.1.3)
        match = re.search(r'(\d+\.\d+(?:\.\d+)*\.)\s*(.*)', header_line)
        if match:
            sec_no = match.group(1).rstrip('.')
            ing_name = match.group(2) if match.group(2) else header_line
        else:
            sec_no = "通則"
            ing_name = header_line[:40]
            
        # 排除目錄頁（目錄頁通常會有大量的點點點或頁碼）
        if "........." in chunk_clean or "............" in chunk_clean:
            continue
            
        sections.append((sec_no, ing_name, chunk_clean))
        
    return sections

def parse_pdf_file(file_path, file_title):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    full_doc_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_doc_text += "\n\n" + text
    except Exception as e:
        print(f"❌ 解析 PDF 失敗 ({file_path}): {e}")
        conn.close()
        return 0

    sections = split_text_into_sections(full_doc_text)
    
    count = 0
    for sec_no, ing_name, content in sections:
        cursor.execute(
            "INSERT INTO rules (source_file, section_no, ingredient_name, content) VALUES (?, ?, ?, ?)",
            (file_title, sec_no, ing_name, content)
        )
        count += 1

    conn.commit()
    conn.close()
    return count

if __name__ == "__main__":
    init_db()
    
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    all_local_pdfs = [
        os.path.join(DOWNLOAD_DIR, f) 
        for f in os.listdir(DOWNLOAD_DIR) 
        if f.lower().endswith(".pdf")
    ]

    if not all_local_pdfs:
        print(f"❌ 在 {DOWNLOAD_DIR} 資料夾內找不到任何 PDF 檔案。")
    else:
        print(f"📂 開始執行精準硬拆...")
        total_sections = 0
        for pdf_path in all_local_pdfs:
            fname = os.path.basename(pdf_path)
            rows = parse_pdf_file(pdf_path, fname)
            print(f"  └─ {fname} 解析完成，成功拆解出 {rows} 個獨立章節區塊")
            total_sections += rows

        print(f"\n🎉 資料庫重建完成！共產生 {total_sections} 個章節區塊！")