import pandas as pd
import streamlit as st

# 1. 載入資料檔 (建議加 cache 提升速度)
@st.cache_data
def load_data():
    drugs_df = pd.read_csv("nhi_drugs.csv")
    mapping_df = pd.read_csv("atc_mapping.csv")
    return drugs_df, mapping_df

try:
    drug_df, atc_map_df = load_data()
except Exception as e:
    st.error(f"資料讀取失敗，請確認檔案編碼與路徑：{e}")
    st.stop()

# 2. ATC 動態比對函式
def get_nhi_section(atc_code):
    if not isinstance(atc_code, str):
        return None
    atc_code = atc_code.strip()
    
    # 從前綴長度 5 碼開始向下比對 (如 A02BC)
    for length in [5, 4, 3, 1]:
        prefix = atc_code[:length]
        match = atc_map_df[atc_map_df['ATC_PREFIX'] == prefix]
        if not match.empty:
            return match.iloc[0]['SECTION_TITLE']
    return None

# 3. Streamlit 查詢介面
st.title("跨院健保藥品與給付規定查詢系統")
search_query = st.text_input("請输入商品名、成分名 (例: Esomeprazole) 或 ATC 碼：", "Esomeprazole")

if search_query:
    # 模糊查詢
    results = drug_df[
        drug_df['成分名稱'].astype(str).str.contains(search_query, case=False, na=False) |
        drug_df['藥品名稱'].astype(str).str.contains(search_query, case=False, na=False) |
        drug_df['ATC_CODE'].astype(str).str.contains(search_query, case=False, na=False)
    ]
    
    if not results.empty:
        st.success(f"找到 {len(results)} 筆藥品資料：")
        st.dataframe(results[['健保代碼', '藥品名稱', '成分名稱', 'ATC_CODE']])
        
        # 比對給付規定章節
        found_sections = set()
        for code in results['ATC_CODE'].dropna():
            sec_title = get_nhi_section(code)
            if sec_title:
                found_sections.add(sec_title)
        
        st.subheader("📋 適用健保給付規定章節")
        if found_sections:
            for sec in found_sections:
                st.info(f"👉 **{sec}**")
        else:
            st.warning("已找到藥品，但該 ATC 碼尚未加入 atc_mapping.csv 中。")
    else:
        st.error("未找到符合的藥品資料。")