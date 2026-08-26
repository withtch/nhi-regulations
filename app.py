import streamlit as st
import sqlite3
import re
import json
import os

st.set_page_config(page_title="健保給付規定精準檢索系統", layout="wide")

st.title("💊 健保藥品給付規定精準檢索系統")
st.caption("✨ 精準切片：全藥品自動章節歸類與二階段篩選")

DB_FILE = "nhi_rules.db"
JSON_FILE = "drug_mapping.json"

# 載入全藥品對照 JSON
CHAPTER_MAPPING = {}
if os.path.exists(JSON_FILE):
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            CHAPTER_MAPPING = json.load(f)
        st.sidebar.success(f"✅ 已成功自動載入 {len(CHAPTER_MAPPING)} 組全藥品章節字典")
    except Exception as e:
        st.sidebar.warning(f"⚠️ 載入 {JSON_FILE} 失敗: {e}")

user_input = st.text_input("🔍 請輸入學名、商品名、藥理分類或條文編號：", "").strip()

if user_input:
    input_upper = user_input.upper()
    
    # 全藥品自動二階段檢索判斷
    if input_upper in CHAPTER_MAPPING:
        target_chapter = CHAPTER_MAPPING[input_upper]["chapter"]
        search_keywords = CHAPTER_MAPPING[input_upper]["keywords"]
        st.info(f"📌 **自動歸類章節**：【第 {target_chapter} 節】 ｜ 💡 **搜尋同義詞/關鍵字**：{', '.join(search_keywords)}")
    else:
        target_chapter = None
        search_keywords = [user_input]

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 執行 SQL 檢索
    if target_chapter:
        kw_clauses = " OR ".join(["content LIKE ?" for _ in search_keywords])
        query = f"SELECT source_file, section_no, ingredient_name, content FROM rules WHERE section_no LIKE ? AND ({kw_clauses}) LIMIT 20"
        params = [f"%{target_chapter}%"] + [f"%{kw}%" for kw in search_keywords]
    else:
        kw_clauses = " OR ".join(["section_no LIKE ? OR ingredient_name LIKE ? OR content LIKE ?" for _ in search_keywords])
        query = f"SELECT source_file, section_no, ingredient_name, content FROM rules WHERE {kw_clauses} LIMIT 20"
        params = []
        for kw in search_keywords:
            params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    st.markdown(f"### 🎯 檢索結果（共命中 **{len(results)}** 大條給付規定）")
    
    if results:
        for source_file, sec_no, ingredient, content in results:
            with st.container():
                st.markdown(f"#### 📜 【{sec_no}】{ingredient}")
                st.caption(f"📁 來源檔案：{source_file}")
                
                # 自動高亮
                highlighted_content = content
                for kw in search_keywords:
                    if len(kw.strip()) >= 2:
                        highlighted_content = re.sub(
                            f"({re.escape(kw)})", 
                            r'<mark style="background-color: #ffe066; padding: 2px 4px; border-radius: 3px; font-weight: bold;">\1</mark>', 
                            highlighted_content, 
                            flags=re.IGNORECASE
                        )
                
                formatted_html = highlighted_content.replace("\n", "<br>")
                st.markdown(
                    f'<div style="font-size: 15px; line-height: 1.8; background-color: #ffffff; padding: 18px; border-radius: 8px; border: 1px solid #dcdcdc; border-left: 6px solid #0d6efd; margin-bottom: 20px;">{formatted_html}</div>', 
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠️ 未找到相關給付條文。")