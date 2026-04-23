import os
import datetime
from tavily import TavilyClient
import google.generativeai as genai
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# API config moved to main execution block

import time
import random

def search_latest_news(tavily_client):
    print("正在使用 Tavily 搜尋最新食品加工 AI 技術...")
    
    # 擴充關鍵字列表，涵蓋不同面向
    keywords = [
        "food processing AI technology", 
        "artificial intelligence in food safety",
        "computer vision food quality inspection",
        "smart food manufacturing AI",
        "generative AI in food industry",
        "AI food supply chain optimization",
        "novel food technology artificial intelligence"
    ]
    
    results = []
    seen_urls = set()
    
    errors = []
    
    for keyword in keywords:
        print(f"搜尋關鍵字: {keyword}")
        try:
            # 使用 Tavily 進行新聞搜尋
            search_res = tavily_client.search(
                query=keyword, 
                search_depth="advanced", 
                topic="news", 
                max_results=3, # 避免資料過多，7 個關鍵字每個取 3 筆，最多 21 筆
                days=30 # 抓取最近 30 天的新聞
            )
            
            # Tavily 回傳的結構是 dict，其中有 'results' 列表
            if search_res and 'results' in search_res:
                new_count = 0
                for res in search_res['results']:
                    href = res.get('url')
                    if href and href not in seen_urls:
                        seen_urls.add(href)
                        results.append(res)
                        new_count += 1
                print(f"  - 找到 {new_count} 筆新資料")
            else:
                print(f"  - 未找到資料")
                
        except Exception as e:
            error_msg = f"搜尋 '{keyword}' 失敗: {str(e)}"
            print(f"  - {error_msg}")
            errors.append(error_msg)

    print(f"搜尋完成。共找到 {len(results)} 筆不重複資料。")
    return results, errors

def generate_digest(search_results):
    print("正在生成摘要報告...")
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 準備搜尋資料內容給 AI
    context_text = ""
    for idx, item in enumerate(search_results, 1):
        # 兼容 Tavily 的結果欄位
        title = item.get('title', 'No Title')
        url = item.get('url', 'No URL')
        snippet = item.get('content', 'No content')
        source = item.get('source', '') # Tavily optional
        date = item.get('published_date', '') # Tavily default date field
        
        context_text += f"{idx}. Title: {title}\n   Source: {source} ({date})\n   URL: {url}\n   Snippet: {snippet}\n\n"

    prompt = f"""
    你是一個專業的食品科技與人工智慧研究員。請根據以下提供的搜尋結果，為我撰寫一份「食品加工 AI 新技術日報」。

    日期：{today}

    要求：
    1. **語言：全繁體中文 (Traditional Chinese)**。
    2. 格式：Markdown。
    3. 內容結構：
        - **前言**：簡短總結今天的發現。
        - **重點技術摘要**：將搜尋結果歸納為幾個重點技術或趨勢（例如：品質檢測、供應鏈優化、新產品開發等）。每個重點下請列出相關的發現。
        - **詳細新聞列表**：列出每則重要新聞的標題、簡短摘要（中文）以及原文連結。
    4. 請確保資訊準確，不要編造。如果資訊不足，請如實說明。
    
    搜尋結果資料：
    {context_text}
    """

    response = model.generate_content(prompt)
    return response.text

def main():
    try:
        # 設定 API Key
        # 如果您在本地執行，請將下方的 "您的_GOOGLE_API_KEY" 和 "您的_TAVILY_API_KEY" 替換為真實的金鑰
        # 注意：請勿將含有真實金鑰的檔案上傳到公開的 GitHub
        GOOGLE_API_KEY_LOCAL = "您的_GOOGLE_API_KEY" 
        TAVILY_API_KEY_LOCAL = "您的_TAVILY_API_KEY"
        
        API_KEY = os.environ.get("GOOGLE_API_KEY") or GOOGLE_API_KEY_LOCAL
        TAVILY_KEY = os.environ.get("TAVILY_API_KEY") or TAVILY_API_KEY_LOCAL
        
        if not API_KEY or API_KEY == "您的_GOOGLE_API_KEY":
            print("錯誤：找不到 GOOGLE_API_KEY。")
            print("請設定環境變數，或是直接修改 main.py 中的 GOOGLE_API_KEY_LOCAL 變數。")
            # 這裡不直接 exit(1)，而是拋出異常以便被下方捕捉並生成報告
            raise ValueError("未設定 GOOGLE_API_KEY 環境變數")
            
        if not TAVILY_KEY or TAVILY_KEY == "您的_TAVILY_API_KEY":
            print("錯誤：找不到 TAVILY_API_KEY。")
            print("請至 https://tavily.com/ 申請免費 API Key 並設定為環境變數，或是修改 TAVILY_API_KEY_LOCAL。")
            raise ValueError("未設定 TAVILY_API_KEY 環境變數")
        
        genai.configure(api_key=API_KEY)
        tavily_client = TavilyClient(api_key=TAVILY_KEY)

        results, errors = search_latest_news(tavily_client)
        
        filename = f"food_ai_digest_{datetime.date.today().strftime('%Y%m%d')}.md"

        if not results:
            print("未找到任何相關資料。將產生含錯誤資訊的報告以便檢查。")
            error_log = "\n".join([f"- {e}" for e in errors]) if errors else "無特定錯誤訊息 (No specific errors recorded)."
            digest_content = f"# 食品加工 AI 新技術日報 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ⚠️ 搜尋失敗或無資料\n\n本日執行搜尋時未找到相關新聞。\n\n### 錯誤紀錄 (Debug Log):\n{error_log}\n\n建議：\n1. 請檢查以上錯誤訊息，確認是否為 IP 封鎖 (403/429) 或連線逾時。\n2. 若顯示無錯誤但無資料，表示放寬後的關鍵字仍無結果，可能需要人工調整。"
        else:
            try:
                digest_content = generate_digest(results)
            except Exception as e:
                print(f"生成摘要時發生錯誤: {e}")
                digest_content = f"# 食品加工 AI 新技術日報 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ⚠️ 生成摘要時發生錯誤\n\n雖然找到了搜尋結果，但在呼叫 AI 生成摘要時發生錯誤。\n\n錯誤訊息：`{str(e)}`\n\n### 搜尋到的資料：\n"
                for i, r in enumerate(results, 1):
                    digest_content += f"{i}. [{r.get('title', 'No Title')}]({r.get('url', '#')})\n"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(digest_content)
            
        print(f"報告已生成：{filename}")

    except Exception as e:
        print(f"執行過程中發生未預期的錯誤: {e}")
        # 發生嚴重錯誤時，產生一個錯誤報告，確保 GitHub Action 後續步驟能抓到檔案
        error_filename = f"food_ai_digest_ERROR_{datetime.date.today().strftime('%Y%m%d')}.md"
        error_content = f"# 食品加工 AI 新技術日報 - 執行錯誤 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ❌ 系統執行失敗\n\n腳本執行過程中發生未預期的錯誤，導致程式終止。\n\n### 錯誤詳細資訊 (Traceback):\n```\n{str(e)}\n```\n\n請檢查 GitHub Action Logs 以獲取更多資訊。"
        
        with open(error_filename, "w", encoding="utf-8") as f:
            f.write(error_content)
        print(f"已生成錯誤報告：{error_filename}")

if __name__ == "__main__":
    main()
