import google.generativeai as genai
import sys

def list_models(api_key):
    try:
        genai.configure(api_key=api_key)
        print("--- 지원되는 모델 목록 ---")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"- {model.name}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python list_models.py <YOUR_API_KEY>")
    else:
        list_models(sys.argv[1])
