import os
import pypandoc
from docx import Document

input_dir = r"D:\健保規範\nhi_files"
output_dir = r"D:\健保規範\markdown_output"

os.makedirs(output_dir, exist_ok=True)


def generate_yaml_header(filename):
    """根據檔名自動生成 YAML 標頭"""
    filename_lower = filename.lower()

    if "chap" in filename_lower or "節" in filename_lower:
        doc_type = "section"
        requires_pre = "false"
    elif "appendix" in filename_lower or "附表" in filename_lower:
        doc_type = "appendix"
        requires_pre = "true"  # 可依需求調整預設值
    else:
        doc_type = "general"
        requires_pre = "false"

    yaml_header = f"""---
doc_id: "{os.path.splitext(filename)[0]}"
doc_type: "{doc_type}"
requires_pre_approval: {requires_pre}
update_date: "115-08-21"
status: "active"
---

"""
    return yaml_header


# 批次轉換並自動寫入 YAML
for filename in os.listdir(input_dir):
    file_path = os.path.join(input_dir, filename)
    name_without_ext, ext = os.path.splitext(filename)
    output_path = os.path.join(output_dir, f"{name_without_ext}.md")

    md_text = ""
    if ext.lower() == ".docx":
        # 轉換 DOCX 邏輯...
        pass
    elif ext.lower() == ".odt":
        try:
            md_text = pypandoc.convert_file(file_path, "markdown")
        except Exception:
            continue
    else:
        continue

    # 將 YAML 標頭放在最前面，再接內文
    full_content = generate_yaml_header(filename) + md_text

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"✅ 自動加上 YAML 標頭並轉存：{output_path}")