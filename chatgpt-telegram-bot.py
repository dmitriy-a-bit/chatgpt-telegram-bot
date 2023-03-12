import telebot
import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
bot = telebot.TeleBot(os.environ.get("TELEGRAM_API_KEY"))
lose_context_after = 600   # Lose context after 600 sec
message_history = []
last_prompt_time = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(is_persistent=True, resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('New Chat')
    bot.send_message(message.chat.id, "I'm OpenAI ChatGPT bot.", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])  # To get text messages from users
def get_answer(message):
    global message_history
    global last_prompt_time
    global lose_context_after

    if message.text == "New Chat":
      message_history = []
      return

    message_history.append({"role": "user", "content": f"{message.text}"})
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message_history
    )
    reply_content = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": f"{reply_content}"})

    if time.time() - last_prompt_time > lose_context_after:
      message_history = []

    last_prompt_time = time.time()

# If answer is too long divide it in small pieces
    if len(response.choices[0].message.content) > 3999:
      long_answer = response.choices[0].message.content
      pieces = []
      for i in range(0, len(long_answer), 3999):
        piece = long_answer[i:i+3999]
        pieces.append(piece)
      for piece in pieces:
        bot.send_message(chat_id=message.from_user.id, text=piece)
    else:
      bot.send_message(chat_id=message.from_user.id, text=response.choices[0].message.content)

    print('>>> ', message_history)

while True:
    try:
      bot.polling()
    except Exception as e:
        print(e)
        time.sleep(5)
