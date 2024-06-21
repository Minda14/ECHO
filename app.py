from flask import Flask, request, jsonify, render_template
import os
import webbrowser
import requests
import google.generativeai as genai

app = Flask(__name__)

API_KEY_GENAI = "AIzaSyAaQnISuLVRDtQ2GXrbUJuZW1WT1qDyTD4"
API_KEY_WEATHER = "8960ef79eb2c407eaab175232241806"
API_KEY_NEWS = "04b85a69d6be4ee196fcad0f924fb287"
genai.configure(api_key=API_KEY_GENAI)

chatStr = ""

def reset_chat():
    global chatStr
    chatStr = ""

def get_weather(location):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY_WEATHER}&q={location}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_description = data['current']['condition']['text']
        temperature = data['current']['temp_c']
        return f"The current weather in {location} is {weather_description} with a temperature of {temperature}°C."
    else:
        return "Sorry, I couldn't fetch the weather information at the moment."

def get_top_news(location):
    url = f"https://newsapi.org/v2/everything?q={location}&language=en&sortBy=publishedAt&pageSize=10&apiKey={API_KEY_NEWS}"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        headlines = [article['title'] for article in data['articles']]
        return "\n".join([f"{idx + 1}. {headline}" for idx, headline in enumerate(headlines)])
    else:
        return "Sorry, I couldn't fetch the news information at the moment."

def handle_command(query):
    global chatStr
    chatStr += f"User: {query}\nJarvis: "

    if "open jobs".lower() in query.lower():
        webbrowser.open("http://localhost:8501/")
        response = "Opening jobs page for you."
        chatStr += f"{response}\n"
        return response

    if "weather at".lower() in query.lower():
        location = query.lower().split("weather at")[1].strip()
        response = get_weather(location)
        chatStr += f"{response}\n"
        return response

    if "news at".lower() in query.lower():
        location = query.lower().split("news at")[1].strip()
        response = get_top_news(location)
        chatStr += f"{response}\n"
        return response

    sites = {
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.com",
        "google": "https://www.google.com",
    }

    for site, url in sites.items():
        if f"open {site}".lower() in query.lower():
            webbrowser.open(url)
            response = f"Opening {site} for you."
            chatStr += f"{response}\n"
            return response

    if "open facetime".lower() in query.lower():
        os.system("open /System/Applications/FaceTime.app")
        response = "Opening FaceTime for you."
        chatStr += f"{response}\n"
        return response

    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "max_output_tokens": 256,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.0-pro-001",
        generation_config=generation_config
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [query],
            }
        ]
    )

    response = chat_session.send_message(query)
    response_text = response.candidates[0].content.parts[0].text.strip()
    chatStr += f"{response_text}\n"
    return response_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'response': 'Please provide a query to chat.'})

    response_text = handle_command(query)
    return jsonify({'response': response_text})

@app.route('/reset', methods=['POST'])
def reset():
    reset_chat()
    return jsonify({'status': 'Chat history has been reset.'})

if __name__ == '__main__':
    app.run(debug=True)
