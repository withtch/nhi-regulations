import sqlite3
import json
import re

DB_FILE = "nhi_rules.db"
JSON_FILE = "drug_mapping.json"

def generate_chapter_mapping():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 優先抓取非通則的真實章節號 (如 7.1, 1.1.3 等)
    cursor.execute("SELECT section_no, ingredient_name, content FROM rules WHERE section_no != '通則'")
    rows = cursor.fetchall()
    conn.close()
    
    mapping = {}
    
    for sec_no, ing_name, content in rows:
        words = re.findall(r'\b[A-Za-z]{3,}\b', ing_name + " " + content)
        for w in words:
            upper_w = w.upper()
            if upper_w in ["FOR", "AND", "WITH", "TABLETS", "INJECTION", "MG/ML", "USE", "ONLY"]:
                continue
                
            if upper_w not in mapping:
                mapping[upper_w] = {
                    "chapter": sec_no,
                    "keywords": [w]
                }
            else:
                if w not in mapping[upper_w]["keywords"]:
                    mapping[upper_w]["keywords"].append(w)
                    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
        
    print(f"🎉 成功自動生成對照檔！共收錄 {len(mapping)} 個藥物同義詞。")

if __name__ == "__main__":
    generate_chapter_mapping()