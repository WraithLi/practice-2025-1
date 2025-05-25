import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Загрузка персонажей
with open("characters.json", "r", encoding="utf-8") as f:
    CHARACTERS = json.load(f)

# Настройка бота
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния игры
class GameState(StatesGroup):
    playing = State()

# База данных для статистики
user_stats = {}

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎭 Привет! Я бот для игры 'Кто я?'\n\n"
        "Я загадаю персонажа, а ты должен угадать его, задавая вопросы, "
        "на которые можно ответить 'Да', 'Нет' или 'Не знаю'.\n\n"
        "Например:\n"
        "- Ты человек?\n"
        "- Ты из фильма?\n"
        "- Ты существуешь в реальной жизни?\n\n"
        "Чтобы начать игру, напиши /play"
    )


# Команда /play - начало игры
@dp.message(Command("play"))
async def play_game(message: types.Message, state: FSMContext):
    await state.set_state(GameState.playing)
    character = random.choice(CHARACTERS)
    await state.update_data(
        character=character,
        questions=0
    )
    await message.answer(
        f"🎮 Игра началась! Я загадал персонажа.\n"
        "Задавай вопросы, на которые можно ответить 'Да', 'Нет' или 'Не знаю'.\n\n"
        "Чтобы сдаться, напиши /surrender"
    )

# Работает ВНЕ игры команда help
@dp.message(Command("help"), ~StateFilter(GameState.playing))
async def help_cmd(message: types.Message):
    await message.answer("Помощь: /play - начать игру")



@dp.message(Command("hint"), StateFilter(GameState.playing))
async def hint_in_game(message: types.Message, state: FSMContext):
    data = await state.get_data()
    character = data["character"]

    # Пример логики подсказки
    if character in ["Человек-паук", "Тони Старк", "Дракула", "Шрек", "Геральт",
                                       "Шерлок Холмс", "Кот в сапогах", "Леон Кеннеди",
                                       "Капитан Джек Воробей", "Губка Боб Квадратные Штаны",
                                       "Карлсон", "Джокер"]:
        hint = "Персонаж — мужчина"
    elif character in ["Рапунцель", "Джульетта"]:
        hint = "Персонаж — девушка"
    else:
        hint = "Персонаж — неизвестного пола"

    await message.answer(f"🔍 Подсказка: {hint}")

# Сдаться
@dp.message(Command("surrender"), StateFilter(GameState.playing))
async def surrender(message: types.Message, state: FSMContext):
    if await state.get_state() != GameState.playing.state:
        return await message.answer("Игра не начата. Напиши /play")

    data = await state.get_data()
    await message.answer(f"😔 Ты сдался... Это был {data['character']}.\nПопробуешь ещё раз? /play")
    await state.clear()


# Обработка вопросов
@dp.message(GameState.playing)
async def handle_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    character = data["character"]
    questions = data["questions"] + 1
    question = message.text.lower()

    # Проверка на команды
    if question.startswith("/"):
        return

    # Обновляем статистику вопросов
    await state.update_data(questions=questions)

    # Проверяем, угадал ли игрок персонажа
    if character.lower() in question:
        user_id = message.from_user.id
        user_stats[user_id] = user_stats.get(user_id, 0) + 1
        await message.answer(
            f"🎉 Правильно! Это {character}!\n"
            f"Ты угадал за {questions} вопросов.\n\n"
            f"Всего побед: {user_stats[user_id]}\n"
            f"Сыграем ещё? /play"
        )
        await state.clear()
        return

    # Логика ответов на вопросы (только если персонаж не угадан)
    answer = "Не знаю"

    if "человек" in question:
        answer = "Да" if character in ["Леон Кеннеди", "Шерлок Холмс", "Джульетта", "Тони Старк", "Карлсон",
                                       "Капитан Джек Воробей", "Джокер", "Человек-паук", "Геральт", "Рапунцель"] \
            else "Нет"
    elif "животное" in question or "зверь" in question or "кот" in question:
        answer = "Да" if character in ["Кот в сапогах"] else "Нет"
    elif "мульт" in question or "мультик" in question:
        answer = "Да" if character in ["Губка Боб Квадратные Штаны", "Шрек", "Рапунцель",
                                       "Кот в сапогах", "Карлсон"] else "Нет"
    elif "игр" in question:
        answer = "Да" if character in ["Леон Кеннеди", "Геральт"] else "Нет"
    elif "кино" in question or "фильм" in question:
        answer = "Да" if character in ["Человек-паук", "Тони Старк", "Капитан Джек Воробей", "Шрек",
                                       "Джокер", "Шерлок Холмс"] else "Нет"
    elif "книг" in question or "литератур" in question:
        answer = "Да" if character in ["Геральт", "Шерлок Холмс", "Джульетта", "Дракула"] else "Нет"
    elif "реальн" in question or "существ" in question:
        answer = "Да" if character in ["Дракула"] else "Нет"
    elif "супергерой" in question or "супер-герой" in question:
        answer = "Да" if character in ["Человек-паук", "Тони Старк"] else "Нет"
    elif "монстр" in question or "чудовищ" in question:
        answer = "Да" if character in ["Дракула", "Шрек"] else "Нет"
    elif "пират" in question:
        answer = "Да" if character == "Капитан Джек Воробей" else "Нет"
    elif "ведьмак" in question:
        answer = "Да" if character == "Геральт" else "Нет"
    elif "мужчина" in question or "мужск" in question:
        answer = "Да" if character in ["Человек-паук", "Тони Старк", "Дракула", "Шрек", "Геральт",
                                       "Шерлок Холмс", "Кот в сапогах", "Леон Кеннеди",
                                       "Капитан Джек Воробей", "Губка Боб Квадратные Штаны",
                                       "Карлсон", "Джокер"] else "Нет"
    elif "женщ" in question or "женск" in question or "дев" in question:
        answer = "Да" if character in ["Рапунцель", "Джульетта"] else "Нет"
    elif "принц" in question:
        answer = "Да" if character == "Рапунцель" else "Нет"
    elif "летать" in question or "летает" in question:
        answer = "Да" if character == "Карлсон" else "Нет"

    await message.answer(answer)


# Статистика
@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    wins = user_stats.get(message.from_user.id, 0)
    await message.answer(f"🏆 Твоё количество побед: {wins}")



# Запуск бота
if __name__ == "__main__":
    dp.run_polling(bot, skip_updates=True)
