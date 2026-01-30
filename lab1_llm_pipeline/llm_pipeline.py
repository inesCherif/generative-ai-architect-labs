from openai import OpenAI
from dotenv import load_dotenv
import os
from prompts import SUMMARY_PROMPT

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_pipeline(input_text):
    prompt = SUMMARY_PROMPT.format(text=input_text)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarization assistant"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    text = input("Paste text:\n")
    print(run_pipeline(text))
