import openai
import telebot
import json
import os
from flask import Flask, request


with open("keys.json", "r") as read_file:
    data = json.load(read_file)

OPENAI_API_KEY = data["OPENAI_KEY"]
BOT_API_KEY = data["BOT_KEY"]

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_API_KEY)
server = Flask(__name__)

f = open("prompt_text.txt", "w+")
f.write("This is a conversation with an AI assistant.\n")
f.close()


@bot.message_handler(func=lambda message: True)
def aiReply(message):
    text = message.text
    if text.lower() == "restart_the_bot":
        f = open("prompt_text.txt", "w+")
        f.write(
            "The following is a conversation with an AI assistant.\n")
        f.close()
        text = "Hi"

    f = open("prompt_text.txt", "r")
    prompt_text = f.read()
    f.close
    tokens = prompt_text.split()
    if len(tokens) > 300:
        prompt_text = tokens[150:]
        f = open("prompt_text.txt", "w+")
        f.write(prompt_text)
        f.close()
    prompt_text = prompt_text+"\nHuman: "+text+"\nAI:"
    response = openai.Completion.create(engine="davinci", prompt=prompt_text, temperature=0.9,
                                        max_tokens=150, top_p=1, frequency_penalty=0, presence_penalty=0.6, stop=["\n", "Human:", "AI:"])
    response_text = response["choices"][0]["text"]
    tmp = open("prompt_text.txt", "w+")
    tmp.write(prompt_text+response_text)
    tmp.close()
    bot.send_message(message.chat.id, response_text)


@server.route('/' + BOT_API_KEY, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://open-ai-bot.herokuapp.com/' + BOT_API_KEY)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
