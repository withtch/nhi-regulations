import os
import re
import streamlit as st

st.set_page_config(page_title="健保藥品給付規定線上查詢系統", layout="wide", page_icon="🔍")

st.title("🔍 健保藥品成分與給付規定線上查詢系統")
st.caption("自動同步 GitHub 最新健保規範 Markdown 資料集")

# 1. 學名 / 商品名同義詞對照字典
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

def clean_and_extract_section(lines, matched_idx):
    """
    從匹配位置開始，抓取完整條文內容，直到遇到下一個章節標題（如 3.3.5）為止
    """
    extracted_lines = []
    
    # 判斷條文開頭（往前向上抓取 1 行，確保涵蓋標題）
    start = max(0, matched_idx)
    
    # 用正則表達式識別「下一個條文標題」的模式（如 3.3.5. 或 通則標題）
    # 避免抓到不屬於該成分的內容
    header_pattern = re.compile(r'^\s*>?\s*\d+\.\d+\.\d+\.')

    for i in range(start, len(lines)):
        line = lines[i].strip()
        
        # 移除 Markdown 引用符號 '>'
        line = re.sub(r'^>\s*', '', line)
        
        # 如果已經抓了內容，且遇到「下一個條文標題」（例如 3.3.5.），則立即停止抓取
        if len(extracted_lines) > 0 and header_pattern.match(line):
            # 確保不是原本匹配的那一行
            if i != matched_idx:
                break

        if line: # 排除純空白行
            extracted_lines.append(line)
            
        # 安全機制：單一條文最多抓取 30 行非空白文字
        if len(extracted_lines) >= 30:
            break

    return "\n".join(extracted_lines)

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
                            for idx in matched_indices[:2]: # 取前 2 個匹配區塊
                                chunk = clean_and_extract_section(lines, idx)
                                if chunk:
                                    extracted_chunks.append(chunk)
                            
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
                # 使用 code 區塊呈現緊湊文字，防止系統拉大段落間距
                st.code(item['snippet'], language="text")
    else:
        st.warning(f"查無包含「{query}」的健保規範檔案。")