import os
import re
import streamlit as st

st.set_page_config(page_title="健保藥品給付規定線上查詢系統", layout="wide", page_icon="🔍")

st.title("🔍 健保藥品成分與給付規定線上查詢系統")
st.caption("自動同步 GitHub 最新健保規範 Markdown 資料集")

# 學名/商品名同義詞對照字典
SYNONYM_MAP = {
    "calcium carbonate": "calcium",
    "碳酸鈣": "calcium",
    "口服鈣": "calcium",
    "oral calcium salt": "calcium",
    "celecoxib": "celecoxib",
    "celebrex": "celecoxib",
    "zolpidem": "zolpidem",
    "stilnox": "zolpidem"
}

query = st.text_input("請輸入藥品成分或學名英文關鍵字（例如：calcium carbonate, celecoxib...）：", placeholder="在此輸入關鍵字...")

DATA_DIR = "./markdown_output"

def clean_extra_newlines(text):
    """清除多餘的連續空行，將 2 個以上的換行壓縮為 1 個換行"""
    text = re.sub(r'\n\s*\n+', '\n', text)
    # 清除 Markdown 引用符號 '>' 後面不必要的空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def search_markdown_files(term):
    results = []
    if not os.path.exists(DATA_DIR):
        return results
    
    term_clean = term.strip().lower()
    search_terms = [term_clean]
    
    if term_clean in SYNONYM_MAP:
        mapped_term = SYNONYM_MAP[term_clean]
        if mapped_term not in search_terms:
            search_terms.append(mapped_term)
            st.info(f"💡 系統自動關聯同義詞/類別查詢：**{mapped_term}**")

    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                        matched_indices = []
                        for idx, line in enumerate(lines):
                            line_lower = line.lower()
                            if any(st_term in line_lower for st_term in search_terms):
                                matched_indices.append(idx)
                        
                        if matched_indices:
                            extracted_chunks = []
                            for idx in matched_indices[:3]:
                                start = max(0, idx - 2)
                                end = min(len(lines), idx + 45) # 擴大抓取範圍，確保 3. 及 4. 點完整呈現
                                
                                raw_chunk = "".join(lines[start:end])
                                # 自動壓縮過多的空行
                                cleaned_chunk = clean_extra_newlines(raw_chunk)
                                extracted_chunks.append(cleaned_chunk)
                            
                            snippet = "\n\n---\n\n".join(extracted_chunks)
                            results.append({
                                "file": file, 
                                "path": file_path, 
                                "snippet": snippet
                            })
                except Exception:
                    continue
    return results

if query:
    results = search_markdown_files(query)
    st.subheader(f"搜尋結果：「{query}」（共 {len(results)} 筆相關檔案）")
    
    if results:
        for item in results:
            with st.expander(f"📄 檔案：{item['file']}", expanded=True):
                st.caption(f"路徑：{item['path']}")
                st.markdown("**對應條文內容：**")
                # 使用 markdown 格式渲染，並去除過大的區塊間距
                st.markdown(item['snippet'])
    else:
        st.warning(f"查無包含「{query}」的健保規範檔案。")