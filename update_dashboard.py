import os
import json
import re

def generate_index():
    reports_dir = os.path.join("docs", "reports")
    output_file = os.path.join("docs", "reports.json")
    
    if not os.path.exists(reports_dir):
        print(f"Directory {reports_dir} does not exist. Creating empty index.")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    reports = []
    
    # 遍歷 reports 資料夾
    for filename in os.listdir(reports_dir):
        if filename.endswith(".md"):
            # 解析日期
            # 格式: food_ai_digest_20260215.md
            date_match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
            date_display = filename
            sort_key = filename
            
            if date_match:
                date_display = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                sort_key = date_match.group(0) # 20260215
                
            reports.append({
                "name": filename,
                "date": date_display,
                "url": f"reports/{filename}",
                "sort_key": sort_key
            })
    
    # 按日期倒序排列 (最新的在最前)
    reports.sort(key=lambda x: x["sort_key"], reverse=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print(f"Index generated with {len(reports)} reports.")

if __name__ == "__main__":
    generate_index()
