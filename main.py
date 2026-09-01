import pandas as pd
import sqlite3
import streamlit as st

# 頁面標題與佈局
st.set_page_config(page_title="跨院健保給付規定查詢系統", layout="wide")
st.title("💊 跨院健保藥品與給付規定查詢系統")

# 1. 載入資料檔
@st.cache_data
def load_data():
    drugs_df = pd.read_csv("nhi_drugs.csv")
    mapping_df = pd.read_csv("atc_mapping.csv")
    return drugs_df, mapping_df

# 2. 從 SQLite 資料庫擷取指定章節的條文內容
def get_rule_content(section_no):
    try:
        conn = sqlite3.connect("nhi_rules.db")
        cursor = conn.cursor()
        # 查詢符合章節編號的條文內容 (假設欄位名為 section_no 與 content)
        cursor.execute("SELECT section_title, content FROM rules WHERE section_no = ?", (section_no,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0], row[1]
    except Exception as e:
        return None, f"讀取資料庫失敗: {e}"
    return None, None

# 3. 載入 CSV 資料
try:
    drug_df, atc_map_df = load_data()
except Exception as e:
    st.error(f"資料讀取失敗，請確認 nhi_drugs.csv 與 atc_mapping.csv 編碼為 UTF-8：{e}")
    st.stop()

# 4. 搜尋 UI
search_query = st.text_input("請輸入商品名、成分名 (例如: Esomeprazole) 或 ATC 碼：", "Esomeprazole")

if search_query:
    # 模糊比對藥品檔
    results = drug_df[
        drug_df['成分名稱'].astype(str).str.contains(search_query, case=False, na=False) |
        drug_df['藥品名稱'].astype(str).str.contains(search_query, case=False, na=False) |
        drug_df['ATC_CODE'].astype(str).str.contains(search_query, case=False, na=False)
    ]
    
    if not results.empty:
        st.success(f"🔍 找到 {len(results)} 筆相關藥品資料")
        st.dataframe(results[['健保代碼', '藥品名稱', '成分名稱', 'ATC_CODE']], use_container_width=True)
        
        # 取得匹配到的 ATC Code 並轉換為對應章節號
        matched_sections = set()
        for atc_code in results['ATC_CODE'].dropna():
            atc_code = atc_code.strip()
            for length in [5, 4, 3, 1]:
                prefix = atc_code[:length]
                match = atc_map_df[atc_map_df['ATC_PREFIX'] == prefix]
                if not match.empty:
                    # 取得對應的 SECTION_NO (例如 "7.1")
                    sec_no = str(match.iloc[0]['SECTION_NO']).strip()
                    matched_sections.add(sec_no)
                    break
        
        # 顯示對應之健保條文
        st.markdown("---")
        st.subheader("📋 適用健保給付規定詳細條文")
        
        if matched_sections:
            for sec_no in matched_sections:
                title, content = get_rule_content(sec_no)
                if content:
                    st.markdown(f"### 👉 {sec_no} {title if title else ''}")
                    # 使用 expander 或直接文字框呈現長篇規範
                    st.text_area(
                        label="給付規定全文：",
                        value=content,
                        height=400,
                        key=f"rule_{sec_no}"
                    )
                else:
                    # 若 SQLite 內尚未輸入，以警示提醒
                    st.warning(f"對應到章節編號【{sec_no}】，但 nhi_rules.db 資料庫內尚未包含此章節之文字內容。")
        else:
            st.warning("已找到藥品，但該 ATC 碼尚未加入 atc_mapping.csv 進行章節映射。")
    else:
        st.error("未找到符合的藥品資料。")