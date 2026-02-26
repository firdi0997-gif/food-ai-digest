import os
import datetime
from ddgs import DDGS  # 已更新為新版 DDGS
from google import genai  # 已更新為新版 google-genai
from dotenv import load_dotenv
import time
import random

# 載入 .env 檔案
load_dotenv()

def search_latest_news():
    print("正在搜尋最新食品加工 AI 技術...")
    
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
    
    # 初始化 DDGS，加入 timeout 控制(15秒)避免無限期卡死
    with DDGS(timeout=15) as ddgs:
        for keyword in keywords:
            print(f"搜尋關鍵字: {keyword}")
            retries = 3
            for attempt in range(retries):
                try:
                    # 隨機延遲，避免被封鎖
                    time.sleep(random.uniform(2, 5))
                    
                    # 優先嘗試新聞搜尋 (News Search)
                    search_res = list(ddgs.news(keyword, region='wt-wt', safesearch='off', max_results=5))
                    
                    # 如果新聞搜尋沒結果，嘗試一般網頁搜尋 (Text Search) - 過去一年 ('y')
                    if not search_res:
                        print(f"  - 新聞搜尋無結果，嘗試一般網頁搜尋 (過去一年)...")
                        time.sleep(random.uniform(1, 3))
                        search_res = list(ddgs.text(keyword, region='wt-wt', safesearch='off', timelimit='y', max_results=5))
                    
                    if search_res:
                        new_count = 0
                        for res in search_res:
                            # 處理不同搜尋方法回傳的索引鍵差異
                            href = res.get('href') or res.get('url')
                            if href and href not in seen_urls:
                                seen_urls.add(href)
                                results.append(res)
                                new_count += 1
                        print(f"  - 找到 {new_count} 筆新資料")
                        break # 成功找到資料，跳出重試迴圈
                    else:
                        print(f"  - 未找到資料")
                        break # 沒報錯但沒資料，也跳出重試
                        
                except Exception as e:
                    error_msg = f"搜尋 '{keyword}' 失敗 (嘗試 {attempt+1}/{retries}): {str(e)}"
                    print(f"  - {error_msg}")
                    errors.append(error_msg)
                    if attempt < retries - 1:
                        time.sleep(5) # 失敗後等待較長時間
                    else:
                        print(f"  - 放棄搜尋關鍵字: {keyword}")

    print(f"搜尋完成。共找到 {len(results)} 筆不重複資料。")
    return results, errors

def generate_digest(search_results, client):
    print("正在生成摘要報告...")
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    # 新版 genai 使用 Client.models.generate_content
    model_name = 'gemini-2.5-flash' # 使用最新的 flash 模型
    
    # 準備搜尋資料內容給 AI
    context_text = ""
    for idx, item in enumerate(search_results, 1):
        # 兼容 news 和 text 搜尋的結果欄位
        title = item.get('title', 'No Title')
        url = item.get('href', item.get('url', 'No URL'))
        snippet = item.get('body', item.get('snippet', 'No content'))
        source = item.get('source', 'Unknown Source')
        date = item.get('date', '')
        
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

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    return response.text

def main():
    try:
        # 設定 API Key
        GOOGLE_API_KEY_LOCAL = "您的_GOOGLE_API_KEY" 
        API_KEY = os.environ.get("GOOGLE_API_KEY") or GOOGLE_API_KEY_LOCAL
        
        if not API_KEY or API_KEY == "您的_GOOGLE_API_KEY":
            print("錯誤：找不到 GOOGLE_API_KEY。")
            raise ValueError("未設定 GOOGLE_API_KEY 環境變數")
        
        # 新版 Google GenAI 戶端初始化
        client = genai.Client(api_key=API_KEY)

        results, errors = search_latest_news()
        
        filename = f"food_ai_digest_{datetime.date.today().strftime('%Y%m%d')}.md"

        if not results:
            print("未找到任何相關資料。將產生含錯誤資訊的報告以便檢查。")
            error_log = "\n".join([f"- {e}" for e in errors]) if errors else "無特定錯誤訊息 (No specific errors recorded)."
            digest_content = f"# 食品加工 AI 新技術日報 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ⚠️ 搜尋失敗或無資料\n\n本日執行搜尋時未找到相關新聞。\n\n### 錯誤紀錄 (Debug Log):\n{error_log}\n\n建議：\n1. 請檢查以上錯誤訊息，確認是否為 IP 封鎖 (403/429) 或連線逾時。\n2. 若顯示無錯誤但無資料，表示放寬後的關鍵字仍無結果，可能需要人工調整。"
        else:
            try:
                digest_content = generate_digest(results, client)
            except Exception as e:
                print(f"生成摘要時發生錯誤: {e}")
                digest_content = f"# 食品加工 AI 新技術日報 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ⚠️ 生成摘要時發生錯誤\n\n雖然找到了搜尋結果，但在呼叫 AI 生成摘要時發生錯誤。\n\n錯誤訊息：`{str(e)}`\n\n### 搜尋到的資料：\n"
                for i, r in enumerate(results, 1):
                    digest_content += f"{i}. [{r.get('title', 'No Title')}](<{r.get('href', '#'>)})\n"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(digest_content)
            
        print(f"報告已生成：{filename}")

    except Exception as e:
        print(f"執行過程中發生未預期的錯誤: {e}")
        error_filename = f"food_ai_digest_ERROR_{datetime.date.today().strftime('%Y%m%d')}.md"
        error_content = f"# 食品加工 AI 新技術日報 - 執行錯誤 ({datetime.date.today().strftime('%Y-%m-%d')})\n\n## ❌ 系統執行失敗\n\n腳本執行過程中發生未預期的錯誤，導致程式終止。\n\n### 錯誤詳細資訊 (Traceback):\n```\n{str(e)}\n```\n\n請檢查 GitHub Action Logs 以獲取更多資訊。"
        
        with open(error_filename, "w", encoding="utf-8") as f:
            f.write(error_content)
        print(f"已生成錯誤報告：{error_filename}")

if __name__ == "__main__":
    main()
