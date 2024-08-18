from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    # Mocked response instead of calling the OpenAI API
    bot_reply = f"Mocked response to: {user_message}"

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True)
