import os
import datetime
from duckduckgo_search import DDGS
import google.generativeai as genai

# 設定 API Key
API_KEY = os.environ.get("GOOGLE_API_KEY")

if not API_KEY:
    print("錯誤：找不到 GOOGLE_API_KEY 環境變數。請確認 GitHub Secrets 或本機環境變數已設定。")
    exit(1)

genai.configure(api_key=API_KEY)

def search_latest_news():
    print("正在搜尋最新食品加工 AI 技術...")
    keywords = ["food processing AI technology", "artificial intelligence in food industry", "new food tech AI"]
    results = []
    
    with DDGS() as ddgs:
        for keyword in keywords:
            print(f"搜尋關鍵字: {keyword}")
            # 搜尋過去一個月的結果
            start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            # max_results=5 每個關鍵字取前 5 筆，避免資訊過多
            try:
                search_res = ddgs.text(keyword, max_results=5, timelimit='m') 
                if search_res:
                    results.extend(search_res)
            except Exception as e:
                print(f"搜尋 {keyword} 時發生錯誤: {e}")

    # 去除重複網址
    seen_urls = set()
    unique_results = []
    for res in results:
        if res['href'] not in seen_urls:
            seen_urls.add(res['href'])
            unique_results.append(res)
            
    print(f"共找到 {len(unique_results)} 筆相關資料。")
    return unique_results

def generate_digest(search_results):
    print("正在生成摘要報告...")
    
    today = datetime.date.today().strftime('%Y-%m-%d')
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 準備搜尋資料內容給 AI
    context_text = ""
    for idx, item in enumerate(search_results, 1):
        context_text += f"{idx}. Title: {item.get('title')}\n   URL: {item.get('href')}\n   Snippet: {item.get('body')}\n\n"

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
    results = search_latest_news()
    if not results:
        print("未找到任何相關資料。")
        return

    digest_content = generate_digest(results)
    
    filename = f"food_ai_digest_{datetime.date.today().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(digest_content)
        
    print(f"報告已生成：{filename}")

if __name__ == "__main__":
    main()
