import telebot
import openai
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
bot = telebot.TeleBot(os.environ.get("TELEGRAM_API_KEY"))
lose_context_after = 600   # Lose context after 600 sec
context = ''
last_prompt_time = 0
chat_mode = ''
engine = "text-davinci-003"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(is_persistent=True, resize_keyboard=True, one_time_keyboard=False)
    keyboard.add('Writer', 'Coder', 'New Chat')
    bot.send_message(message.chat.id, "I'm OpenAI ChatGPT bot.", reply_markup=keyboard)

@bot.message_handler(content_types=['text'])  # To get text messages from users
def get_answer(message):
    global context
    global last_prompt_time
    global lose_context_after
    global chat_mode
    global engine

    if message.text == "Writer":
      chat_mode = "Writer"

    if message.text == "Coder":
      chat_mode = "Coder"

    if message.text == "Writer" or message.text == "Coder" or message.text == "New Chat":
      context = ''
      return

    if chat_mode == "Writer":
      engine = "text-davinci-003"

    if chat_mode == "Coder":
      engine = "code-davinci-002"

    response = openai.Completion.create(
            engine=engine,
            prompt=f"{context}Q: {message.text} ->",
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop="###",
        )

    if time.time() - last_prompt_time > lose_context_after:
      context = ''

    context += message.text + ', '
    last_prompt_time = time.time()
    bot.send_message(chat_id=message.from_user.id, text=response['choices'][0]['text'])
    print(response)
    print('>>> ' + context)

while True:
    try:
      bot.polling()
    except Exception as e:
        print(e)
        time.sleep(5)
