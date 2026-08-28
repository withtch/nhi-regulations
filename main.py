import os
import streamlit as st

# 1. 頁面標題與佈局設定
st.set_page_config(page_title="健保藥品給付規定線上查詢系統", layout="wide", page_icon="🔍")

st.title("🔍 健保藥品成分與給付規定線上查詢系統")
st.caption("自動同步 GitHub 最新健保規範 Markdown 資料集")

# 2. 搜尋輸入框
query = st.text_input("請輸入藥品成分或學名英文關鍵字（例如：celecoxib, zolpidem...）：", placeholder="在此輸入關鍵字...")

# 3. 指定 GitHub 儲存庫內的 Markdown 資料夾相對路徑
DATA_DIR = "./markdown_output"

def search_markdown_files(term):
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    
    term_lower = term.lower()
    
    # 遍歷資料夾下所有 .md 檔案
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        # 找出包含關鍵字的行號
                        matched_indices = [i for i, line in enumerate(lines) if term_lower in line.lower()]
                        
                        if matched_indices:
                            extracted_chunks = []
                            for idx in matched_indices[:3]: # 取前 3 個匹配位置
                                start = max(0, idx - 2)     # 包含標題與前 2 行
                                end = min(len(lines), idx + 15) # 抓取關鍵字下方 15 行條文內容
                                extracted_chunks.append("".join(lines[start:end]))
                            
                            snippet = "\n---\n".join(extracted_chunks)
                            results.append({
                                "file": file, 
                                "path": file_path, 
                                "snippet": snippet
                            })
                except Exception:
                    continue
    return results

# 4. 搜尋結果顯示區塊
if query:
    results = search_markdown_files(query)
    st.subheader(f"搜尋結果：「{query}」（共 {len(results)} 筆相關檔案）")
    
    if results:
        for item in results:
            with st.expander(f"📄 檔案：{item['file']}", expanded=True):
                st.caption(f"路徑：{item['path']}")
                st.markdown("**對應條文與前後文內容：**")
                st.code(item['snippet'], language="markdown")
    else:
        st.warning(f"查無包含「{query}」的健保規範檔案。")