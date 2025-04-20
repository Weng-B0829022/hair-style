import os
from dotenv import load_dotenv
from openai import OpenAI
from django.conf import settings

def access_gpt(messages, model='gpt-4'):
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error in GPT API call: {str(e)}")
        raise

def generate_image(prompt):
    load_dotenv(os.path.join(settings.BASE_DIR, '.env'))
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
    )

    try:
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
        raise

def process_qa(question):
    # 構建 GPT 提示詞
    system_prompt = """你是一個專業的問答助手。當收到問題時，你需要：
    1. 提供詳細的答案
    2. 生成一個適合的圖片描述，這個描述將用於生成相關的圖片
    請以 JSON 格式返回，包含 'answer' 和 'image_prompt' 兩個字段。"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # 獲取 GPT 回答
    gpt_response = access_gpt(messages)
    
    # 解析 GPT 回答
    try:
        import json
        response_data = json.loads(gpt_response)
        answer = response_data['answer']
        image_prompt = response_data['image_prompt']
    except json.JSONDecodeError:
        raise ValueError("Invalid GPT response format")

    # 生成圖片
    image_url = generate_image(image_prompt)

    return {
        'question': question,
        'answer': answer,
        'image_url': image_url
    } 