from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 필요한 경우 이 값을 변경하세요

@app.route('/')
def index():
    api_key = session.get('api_key', '')
    target_language = session.get('target_language', 'th')
    return render_template('index.html', api_key=api_key, target_language=target_language)

@app.route('/set_api_key', methods=['POST'])
def set_api_key():
    session['api_key'] = request.form['api_key']
    return redirect(url_for('index'))

@app.route('/set_language', methods=['POST'])
def set_language():
    session['target_language'] = request.form['language']
    return redirect(url_for('index'))

@app.route('/translate', methods=['POST'])
def translate():
    api_key = session.get('api_key')
    target_language = session.get('target_language', 'th')
    
    if not api_key:
        return jsonify({"error": "API 키를 설정해 주세요."}), 400

    text = request.form['text']

    # Google AI SDK 설정
    genai.configure(api_key=api_key)

    # 모델 생성
    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
      model_name="gemini-1.5-flash-exp-0827",
      generation_config=generation_config,
      system_instruction=f"페르소나 이름: (Translator)\n\n역할: 모든 입력된 내용을 {target_language}로 번역하는 번역기\n\n언어 지원: 자동 탐지 및 모든어지원 \n\n성격:\n\n정확성: 최대한 정확한 번역을 제공\n신속성: 빠르게 번역 결과를 제공\n이해: 다양한 문맥을 이해하고 자연스러운 번역을 제공\n기능:\n\n자동 언어 감지: 입력된 텍스트의 언어를 자동으로 감지\n{target_language}어 번역: 감지된 언어를 {target_language}어로 번역\n예시:\n\n주의사항: 번역기는 번역만해야합니다. 주의사항같은것을 적지마세요.\n\n입력: “안녕하세요. 어떻게 지내세요?”\n\n출력: “Hello, how are you?”\n\n입력: “Je suis content de vous rencontrer.”\n\n출력: “It's nice to meet you.”\n\n해당하는 언어로 번역하는 코드는 언어코드로 해당됩니다.\n예시:\n사용자: {target_language}: what are you doing?\n번역기: 지금 뭐하고잇어?",
    )

    chat_session = model.start_chat(
      history=[]
    )

    response = chat_session.send_message(text)
    return jsonify({"translation": response.text})

if __name__ == '__main__':
    app.run(debug=True)
