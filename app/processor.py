from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary(content):
    try:
        prompt = f"""
        You are an advanced AI system that extracts structured business information from website content.

        Analyze the content and return ONLY a valid JSON object.

        Required JSON format:
        {{
        "summary": "",
        "business_type": "",
        "services": [],
        "target_audience": "",
        "contact_info": {{
            "emails": [],
            "phone_numbers": [],
            "addresses": []
        }},
        "social_links": [],
        "keywords": []
        }}

        Rules:
        - Return ONLY valid JSON
        - Do NOT add explanations or text outside JSON
        - If data not found, use "" or []
        - Keep summary concise (3-5 lines)

        Website Content:
        {content}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        output = response.choices[0].message.content.strip()

        
        data = json.loads(output) #Convert string → JSON safely

        return data

    except Exception as e:
        print("AI Error:", e)

        # fallback response
        return {
            "summary": content[:200],
            "business_type": "Unknown",
            "services": [],
            "target_audience": "",
            "contact_info": {
                "emails": [],
                "phone_numbers": [],
                "addresses": []
            },
            "social_links": [],
            "keywords": []
        }