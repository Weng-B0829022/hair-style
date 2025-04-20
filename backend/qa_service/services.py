import os
from dotenv import load_dotenv
from openai import OpenAI
from django.conf import settings
import requests
import json
import random
from bs4 import BeautifulSoup
import re

ALLOWED_DOMAINS = [
    'www.instagram.com',
    'instagram.com',
]

def access_gpt(messages, model='gpt-4o-2024-08-06'):
    try:
        load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
        )

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in GPT API call: {str(e)}")
        raise

def generate_image(prompt):
    try:
        load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
        client = OpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"Error in Image generation: {str(e)}")
        return None

def process_qa(question):
    system_prompt = """你是一個專業的問答助手。當收到問題時，你需要：
    1. 提供詳細的答案
    2. 生成一個適合的圖片描述，這個描述將用於生成相關的圖片
    請以 JSON 格式返回，包含 'answer' 和 'image_prompt' 兩個字段。"""
    print(question)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    gpt_response = access_gpt(messages)
    
    try:
        response_data = json.loads(gpt_response)
        answer = response_data['answer']
        image_prompt = response_data['image_prompt']
    except json.JSONDecodeError:
        raise ValueError("Invalid GPT response format")

    image_url = generate_image(image_prompt)

    return {
        'question': question,
        'answer': answer,
        'image_url': image_url
    }

def search_beauty_articles(keyword):
    try:
        sites_query = ' OR '.join(f'site:{domain}' for domain in ALLOWED_DOMAINS)
        
        response = requests.post(
            'https://google.serper.dev/search',
            headers={
                'X-API-KEY': '4c93a675a581d2f8e8064bc938d2433fd88fb6f1',
                'Content-Type': 'application/json'
            },
            json={
                'q': sites_query + ' ' + keyword,
                'location': 'Taiwan',
                'num': 20,
                'gl': 'tw',
                'hl': 'zh-tw',
                'tbs': 'qdr:m'
            }
        )
        
        if response.status_code != 200:
            print(f'Serper API error: {response.status_code}')
            print(f'Response: {response.text}')
            return []
            
        data = response.json()
        if not data.get('organic'):
            print('No search results found')
            return []
            
        return data.get('organic', [])[:20]
    except Exception as e:
        print(f'Search error: {str(e)}')
        return []

def fetch_article_content(url, snippet=''):
    try:
        if not any(url.startswith(f'https://{domain}') for domain in ALLOWED_DOMAINS):
            print(f"URL 不是允許的網域: {url}")
            return None
            
        # 直接使用 snippet 作為內容
        post_data = {
            'title': None,
            'content': snippet,
            'hashtags': [],
            'mentions': [],
            'likes': None,
            'comments': None,
            'timestamp': None
        }
        
        return {
            'title': post_data['title'],
            'content': post_data['content'],
            'raw_data': post_data
        }
        
    except Exception as e:
        print(f"處理內容時發生錯誤: {str(e)}")
        return None

def generate_beauty_content(search_results):
    if not search_results:
        print("沒有搜索結果，返回空列表")
        return []
        
    print("開始生成美容內容...")
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    # 定義內容類別和子類別
    content_categories = {
        '髮型趨勢介紹': ['染髮流行色', '剪髮造型趨勢', '韓系流行'],
        '客戶實拍成果': ['剪髮前後對比', '染燙髮後實拍照', '顧客好評回饋'],
        '教學科普文': ['洗髮教學', '吹整教學', '臉型與髮型搭配知識'],
        '美髮產品推薦': ['護髮品推薦', '造型品搭配', '髮型設計產品組合'],
        '品牌門市日常': ['門市日常花絮', '設計師介紹', '限動互動']
    }

    articles = []
    total_categories = len(content_categories)
    
    # 先抓取所有文章的內容
    print("\n抓取所有文章內容...")
    article_contents = []
    for article_index, relevant_article in enumerate(search_results, 1):
        print(f"\n  處理文章 {article_index}/{len(search_results)}")
        print(f"  參考文章: {relevant_article.get('link', '無來源')}")
        
        article_content = fetch_article_content(
            relevant_article.get('link', ''),
            relevant_article.get('snippet', '')  # 傳入 snippet
        )
        if article_content:
            print(f"    ✓ 成功抓取文章內容")
            article_contents.append({
                'url': relevant_article.get('link', ''),
                'title': relevant_article.get('title', ''),
                'snippet': relevant_article.get('snippet', ''),
                'content': article_content.get('content', ''),
                'raw_data': article_content.get('raw_data', {})
            })
        else:
            print(f"    ✗ 無法抓取文章內容")
    
    if not article_contents:
        print("沒有成功抓取到任何文章內容")
        return []
    
    print(f"\n成功抓取 {len(article_contents)} 篇文章內容", article_contents)
    
    # 處理每個類別和子類別
    for category_index, (category, subcategories) in enumerate(content_categories.items(), 1):
        print(f"\n處理類別 {category_index}/{total_categories}: {category} 內容{article_contents}")
        
        # 只取一個子類別
        subcategory = random.choice(subcategories)
        print(f"\n  處理子類別: {subcategory}")
        
        try:
            print("    正在生成 GPT 提示詞...")
            system_prompt = """你是一個專業的美容美髮文案撰寫專家。請根據提供的文章內容，生成符合以下格式的JSON內容：
{
    "title": "主標題",
    "subtitle": "副標題",
    "content": "文章內容",
    "image_prompt": "圖片生成提示詞"
}"""

            # 構建參考文章內容
            reference_articles = []
            for i, article in enumerate(article_contents):
                reference_articles.append(
                    f"文章 {i+1}:\n"
                    f"標題: {article['title']}\n"
                    f"內容摘要: {article['content']}"
                )
            
            reference_content = "\n\n".join(reference_articles)

            user_prompt = f"""請為以下類別生成內容：

類別: {category}
子類別: {subcategory}

參考文章內容：
{reference_content}

內容要求：
1. 主標題：根據類別和子類別生成吸引人的標題
2. 副標題：補充說明主標題的重點
3. 文章內容：綜合所有參考文章的內容，生成一篇完整的文章
4. 圖片提示詞：生成一個詳細的圖片描述，用於生成相關的圖片

風格要求：
- 文章風格要活潑吸睛
- 突出最新髮型趨勢
- 加入實用的建議和技巧
- 使用口語化的表達方式"""

            print("    正在調用 GPT API...")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            print("    正在處理 GPT 回應...")
            content_str = response.choices[0].message.content.strip()
            content_str = content_str.replace('\r', '').replace('\t', '   ')
            
            try:
                content = json.loads(content_str)
                print("    ✓ JSON 解析成功")
            except json.JSONDecodeError as e:
                print(f"    ✗ JSON 解析失敗: {str(e)}")
                print(f"    內容: {content_str}")
                continue
            
            print("    正在生成圖片...")
            image_url = generate_image(content.get('image_prompt', ''))
            if image_url:
                print("    ✓ 圖片生成成功")
            else:
                print("    ✗ 圖片生成失敗，使用預設圖片")
            
            # 添加所有參考文章的資訊
            articles.append({
                'category': category,
                'subcategory': subcategory,
                'title': content.get('title', '未知標題'),
                'subtitle': content.get('subtitle', '未知副標題'),
                'content': content.get('content', '內容生成失敗'),
                'image_url': image_url or 'https://via.placeholder.com/1024x1024.png?text=Image+Generation+Failed',
                'source_articles': article_contents  # 包含所有參考文章的完整資訊
            })
            print(f"    ✓ 成功生成 {category} - {subcategory} 的內容")
            
        except Exception as e:
            print(f"    ✗ 處理失敗: {str(e)}")
            continue

    print(f"\n內容生成完成，共生成 {len(articles)} 篇文章")
    return articles

def process_beauty_query(keyword):
    # 搜尋相關文章
    search_results = search_beauty_articles(keyword)
    
    # 生成內容
    articles = generate_beauty_content(search_results)
    
    return {
        'keyword': keyword,
        'articles': articles
    } 