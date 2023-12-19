import vector_searcher as vs
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from voice_analyzer import speech_to_text


async def handle_main(message: types.Message):
    await message.answer(
        "Привет. Я чат-бот Росатома, помогаю найти всю необходимую информацию по закупкам. Выберите кнопку, чтобы начать поиск:",
        reply_markup=keyboard_main)

    await SearchType.MAIN.set()


async def send_long_message(chat_id, text):
    max_message_length = 4096
    chunks = [text[i:i + max_message_length] for i in range(0, len(text), max_message_length)]
    for chunk in chunks:
        await dp.bot.send_message(chat_id, chunk)


logging.basicConfig(level=logging.INFO)

bot = Bot(token="6773367774:AAE5GKYqbTAtebO3SuoaevC8sMHobduutUI")

dp = Dispatcher(bot, storage=MemoryStorage())

data_path = "content"


class SearchType(StatesGroup):
    VECTOR = State()
    MAIN = State()


# Main keyboard
keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons_main = ["Векторный поиск", "Поиск нейросеть", "Тех поддержка"]
keyboard_main.add(*buttons_main)

# Vector keyboard
keyboard_vector = types.ReplyKeyboardMarkup(resize_keyboard=True)
buttons_vector = ["Главное меню"]
keyboard_vector.add(*buttons_vector)
button_handlers_vector = {
    buttons_vector[0]: handle_main
}


@dp.message_handler(commands=['start'], state=[None, SearchType.MAIN, SearchType.VECTOR])
async def start_command(message: types.Message):
    await handle_main(message)


@dp.message_handler(content_types=types.ContentType.TEXT, state=SearchType.MAIN)
async def handle_main_keyboard(message: types.Message):
    if message.text == "Векторный поиск":
        await SearchType.VECTOR.set()
        await message.answer("Вы выбрали векторный поиск, задайте ваш вопрос", reply_markup=keyboard_vector)
    elif message.text == "Поиск нейросеть":
        await message.answer("Вы выбрали поиск через нейросеть, задайте ваш вопрос", reply_markup=keyboard_main)
    elif message.text == "Тех поддержка":
        await message.answer(
            "Вы выбрали тех поддержку, напишите, ваш вопрос и первый освободившийся специалист поможет Вам",
            reply_markup=keyboard_main)


@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.VOICE], state=SearchType.VECTOR)
async def handle_vector(message: types.Message):
    if message.content_type == types.ContentType.TEXT:
        # Get text message
        user_message = message.text

        if user_message in button_handlers_vector:
            await button_handlers_vector[user_message](message)
        else:
            print(f"Векторный поиск | Вопрос: {user_message}")

            # Get answer
            answer = vs.send_question(question=user_message, path=data_path)

            # Send answer
            if len(answer) > 4096:
                await send_long_message(message.from_user.id, f"Ответ:\n{answer}")
            else:
                await dp.bot.send_message(message.from_user.id, f"Ответ:\n{answer}")
    elif message.content_type == types.ContentType.VOICE:
        await dp.bot.send_message(message.from_user.id, "Получаю Ваше сообщение...")
        # Get voice message
        voice_file_id = message.voice.file_id
        voice_file = await bot.get_file(voice_file_id)
        voice_path = voice_file.file_path
        downloaded_voice = await bot.download_file(voice_path)

        # Save voice message as .mp3
        with open("voice_message.ogg", "wb") as voice_message:
            voice_message.write(downloaded_voice.read())
            voice_message.close()

        await dp.bot.send_message(message.from_user.id, "Изучаю вопрос...")

        voice_question = speech_to_text(sound="voice_message.ogg", model=model)

        await dp.bot.send_message(message.from_user.id, f"Ваш вопрос: {voice_question}")
        print(f"Векторный поиск | Вопрос голосом: {voice_question}")

        # Get answer
        answer = vs.send_question(question=voice_question, path=data_path)

        # Send answer
        if len(answer) > 4096:
            await send_long_message(message.from_user.id, f"Ответ:\n{answer}")
        else:
            await dp.bot.send_message(message.from_user.id, f"Ответ:\n{answer}")


if __name__ == '__main__':
    from aiogram import executor
    from whisper import load_model

    # Load speech-to-text model
    print("Whisper model loading...")
    model = load_model("medium.pt")
    print("Model loaded")

    executor.start_polling(dp, skip_updates=True)
