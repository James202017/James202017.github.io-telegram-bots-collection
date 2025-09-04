import logging
import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

try:
    import ssl
except ModuleNotFoundError:
    ssl = None
    logging.error("Модуль SSL не найден. Проверьте наличие OpenSSL в вашей системе.")

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command

# Настройка логирования
log_filename = f'bot_{datetime.now().strftime("%Y%m%d")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение значений из переменных окружения
API_TOKEN = os.getenv('BOT_TOKEN_INV')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Проверка наличия необходимых переменных окружения
if not API_TOKEN:
    raise ValueError("BOT_TOKEN_INV не найден в .env файле")
if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в .env файле")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    raise ValueError("ADMIN_CHAT_ID должен быть числом")

# Проверка SSL
if ssl is None:
    sys.exit("Ошибка: Модуль SSL недоступен. Установите OpenSSL или используйте среду с поддержкой SSL.")

# Инициализация бота
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class InvestForm(StatesGroup):
    direction = State()
    amount = State()
    term = State()
    comment = State()
    contact = State()

# Клавиатуры
def get_invest_keyboard():
    """Создает клавиатуру для выбора направления инвестиций"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🏢 Коммерческая недвижимость"))
    keyboard.add(KeyboardButton("🏠 Жилая недвижимость"))
    keyboard.add(KeyboardButton("🏗️ Новостройки"))
    keyboard.add(KeyboardButton("🌍 Зарубежная недвижимость"))
    keyboard.add(KeyboardButton("💼 Инвестиционные фонды"))
    return keyboard

def get_amount_keyboard():
    """Создает клавиатуру для этапа ввода суммы"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🔙 Назад к выбору направления"))
    keyboard.add(KeyboardButton("🔄 Начать заново"))
    return keyboard

def get_term_keyboard():
    """Создает клавиатуру для этапа ввода срока"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🔙 Назад к сумме"))
    keyboard.add(KeyboardButton("🔄 Начать заново"))
    return keyboard

def get_comment_keyboard():
    """Создает клавиатуру для этапа комментария"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🔙 Назад к сроку"))
    keyboard.add(KeyboardButton("🔄 Начать заново"))
    return keyboard

def get_contact_keyboard():
    """Создает клавиатуру для этапа контактов"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton("🔙 Назад к комментарию"))
    keyboard.add(KeyboardButton("🔄 Начать заново"))
    return keyboard

# Валидация опций
VALID_OPTIONS = [
    "🏗️ 1. Новостройки (доход до 3 млн руб и выше)",
    "🌍 2. Зарубежная недвижимость",
    "💎 3. Выкуп лотов ниже рынка",
    "💰 4. Вклады под 29% годовых"
]

# Тексты сообщений
WELCOME_MESSAGE = (
    "<b>🎉 Добро пожаловать в мир выгодных инвестиций!</b>\n\n"
    "💼 С помощью этого умного помощника вы можете оставить заявку на самые перспективные инвестиционные предложения!\n\n"
    "🚀 <b>Наши топ-направления:</b>\n"
    "🌍 Зарубежная недвижимость\n"
    "💰 Вклады под 29% годовых\n"
    "📈 Пассивный доход от 100,000₽/месяц\n\n"
    "✨ Пожалуйста, заполняйте все поля внимательно и максимально подробно, "
    "чтобы наши <b>эксперты-консультанты</b> могли связаться с вами и предложить идеальное решение! 🎯"
)

RECOMMENDATIONS = (
    "📋 <b>Важные рекомендации для успешной заявки:</b>\n\n"
    "✅ Указывайте максимум информации о ваших целях\n"
    "📝 Все поля обязательны для заполнения\n"
    "🎯 Мы подберем <b>персональное</b> выгодное решение\n"
    "⚡ Быстрая обработка заявки в течение 2-х часов\n"
    "🔒 Полная конфиденциальность ваших данных\n\n"
    "💡 <i>Чем подробнее информация, тем точнее наше предложение!</i>"
)

def format_amount(amount: str) -> str:
    """Форматирует сумму для отображения"""
    try:
        num = float(amount.replace(' ', '').replace(',', '.'))
        return f"{num:,.2f}".replace(',', ' ').replace('.', ',')
    except ValueError:
        return amount

@dp.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    try:
        # Получаем параметр start из команды
        start_param = message.get_args() if hasattr(message, 'get_args') else ''
        logger.info(f"Пользователь {message.from_user.id} запустил бота с параметром: {start_param}")
        
        # Улучшенное приветственное сообщение с презентацией услуг
        enhanced_welcome = (
            f"💰 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n"
            "📈 <b>Инвестиции в недвижимость - ваш путь к финансовой свободе</b>\n\n"
            "🎯 <b>Наши преимущества:</b>\n"
            "• 💎 Доходность от 12% годовых\n"
            "• 🛡️ Минимальные риски и гарантии\n"
            "• 📊 Профессиональная аналитика рынка\n"
            "• 🏗️ Проверенные застройщики и проекты\n"
            "• 💼 Индивидуальное сопровождение\n"
            "• 📋 Полная юридическая поддержка\n\n"
        )
        
        # Персонализированное приветствие в зависимости от источника
        if start_param == 'investicii':
            welcome_msg = "🎯 <b>Отлично! Вы перешли из раздела инвестиций на сайте!</b>\n\n" + enhanced_welcome + WELCOME_MESSAGE
        else:
            welcome_msg = enhanced_welcome + WELCOME_MESSAGE
            
        await message.answer(welcome_msg)
        await message.answer(RECOMMENDATIONS)
        await state.set_state(InvestForm.direction)
        await message.answer("🚀 <b>Выберите направление инвестиций:</b>", reply_markup=get_invest_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в команде start: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(F.text.in_(["🔙 Назад к выбору направления", "🔙 Назад к сумме", "🔙 Назад к сроку", "🔙 Назад к комментарию", "🔄 Начать заново"]))
async def navigation_handler(message: types.Message, state: FSMContext):
    try:
        if message.text == "🔄 Начать заново":
            await state.set_state(InvestForm.direction)
            await message.answer(
                "🔄 <b>Начинаем заново!</b>\n\n🚀 Выберите направление инвестиций:",
                reply_markup=get_invest_keyboard()
            )
        elif message.text == "🔙 Назад к выбору направления":
            await state.set_state(InvestForm.direction)
            await message.answer(
                "🚀 <b>Выберите направление инвестиций:</b>",
                reply_markup=get_invest_keyboard()
            )
        elif message.text == "🔙 Назад к сумме":
            await state.set_state(InvestForm.amount)
            await message.answer(
                "💰 <b>Укажите желаемую сумму инвестиций:</b>\n\n💡 <i>Например: 500000, 1000000, 5000000</i>",
                reply_markup=get_amount_keyboard()
            )
        elif message.text == "🔙 Назад к сроку":
            await state.set_state(InvestForm.term)
            await message.answer(
                "⏰ <b>Укажите желаемый срок инвестиций:</b>\n\n📅 Например: 1 год, 2 года, 5 лет\n💡 Чем дольше срок - тем выше доходность",
                reply_markup=get_term_keyboard()
            )
        elif message.text == "🔙 Назад к комментарию":
            await state.set_state(InvestForm.comment)
            await message.answer(
                "💭 <b>Дополнительные пожелания:</b>\n\n✨ Есть ли особые требования к проекту?\n🎯 Предпочтения по локации?\n❓ Дополнительные вопросы?",
                reply_markup=get_comment_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка в навигации: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(InvestForm.direction)
async def process_direction(message: types.Message, state: FSMContext):
    try:
        direction_options = [
            "🏢 Коммерческая недвижимость",
            "🏠 Жилая недвижимость", 
            "🏗️ Новостройки",
            "🌍 Зарубежная недвижимость",
            "💼 Инвестиционные фонды"
        ]
        
        if message.text not in direction_options:
            await message.answer(
                "❗Пожалуйста, выберите вариант из списка.",
                reply_markup=get_invest_keyboard()
            )
            return
        
        logger.info(f"Пользователь {message.from_user.id} выбрал направление: {message.text}")
        await state.update_data(direction=message.text)
        await state.set_state(InvestForm.amount)
        await message.answer(
            "💰 <b>Отлично!</b> Теперь укажите желаемую сумму инвестиций:\n\n"
            "💡 <i>Например: 500000, 1000000, 5000000</i>",
            reply_markup=get_amount_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке направления: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(InvestForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Это поле обязательно. Укажите сумму.")
            return
        
        # Проверка на числовое значение
        try:
            amount = float(message.text.replace(' ', '').replace(',', '.'))
            if amount <= 0:
                raise ValueError
            formatted_amount = format_amount(message.text)
        except ValueError:
            await message.answer("❗Пожалуйста, введите корректную сумму числом.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} указал сумму: {formatted_amount}")
        await state.update_data(amount=formatted_amount)
        await state.set_state(InvestForm.term)
        await message.answer(
            "⏰ <b>Укажите желаемый срок инвестиций:</b>\n\n📅 Например: 1 год, 2 года, 5 лет\n💡 Чем дольше срок - тем выше доходность",
            reply_markup=get_term_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке суммы: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(InvestForm.term)
async def process_term(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Пожалуйста, укажите срок.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} указал срок: {message.text}")
        await state.update_data(term=message.text)
        await state.set_state(InvestForm.comment)
        await message.answer(
            "💭 <b>Дополнительные пожелания:</b>\n\n✨ Есть ли особые требования к проекту?\n🎯 Предпочтения по локации?\n❓ Дополнительные вопросы?",
            reply_markup=get_comment_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке срока: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

@dp.message(InvestForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    try:
        logger.info(f"Пользователь {message.from_user.id} добавил комментарий")
        await state.update_data(comment=message.text)
        await state.set_state(InvestForm.contact)
        
        await message.answer(
            "📞 <b>Почти готово!</b> Укажите ваше имя и номер телефона для связи:\n\n"
            "👤 <i>Например: Иван Петров, +7 (999) 123-45-67</i>\n\n"
            "🔒 Ваши данные надежно защищены и используются только для связи с вами!",
            reply_markup=get_contact_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке комментария: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")









@dp.message(InvestForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    try:
        if not message.text.strip():
            await message.answer("❗Контактные данные обязательны.")
            return
        
        logger.info(f"Пользователь {message.from_user.id} отправил контактные данные")
        await state.update_data(contact=message.text)
        data = await state.get_data()

        summary = (
            f"💰 <b>📥 Новая заявка на инвестиции:</b>\n\n"
            f"🎯 <b>Направление:</b> {data.get('direction')}\n"
            f"💵 <b>Сумма:</b> {data.get('amount')}\n"
            f"⏰ <b>Срок:</b> {data.get('term')}\n"
            f"💭 <b>Комментарий:</b> {data.get('comment')}\n"
            f"📞 <b>Контакт:</b> {data.get('contact')}\n\n"
            f"👤 От: {message.from_user.full_name} (ID: {message.from_user.id})\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
        await message.answer(
            "✅ <b>Отлично! Ваша инвестиционная заявка принята!</b>\n\n"
            "🎯 Наш инвестиционный консультант свяжется с вами в течение 30 минут\n"
            "📊 Подготовим персональную презентацию проектов\n"
            "💎 Покажем варианты с доходностью от 12% годовых\n"
            "📋 Проведем бесплатную консультацию\n\n"
            "💰 <i>Ваши инвестиции - наша ответственность!</i>",
            reply_markup=get_invest_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка в обработке контакта: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

async def main():
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise
