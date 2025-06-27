


python
import telebot import os
from telebot import types
import json
from datetime import datetime

# Токен вашего бота
TOKEN = "8032340002:AAHlXYZ8X6lU8tLNIOCUJU4p0GYuwU_jWKU"
bot = telebot.TeleBot(TOKEN)

# База данных БВИП (базовая величина для исчисления пенсий)
BVIP_DATA = {
    "2000-08": 2450, "2001-08": 3430, "2002-04": 3945, "2002-08": 4535,
    "2003-05": 5440, "2004-08": 6530, "2005-05": 7835, "2005-10": 9400,
    "2006-07": 10800, "2006-11": 12420, "2007-08": 15525, "2007-11": 17077.50,
    "2007-12": 18630, "2008-04": 20865, "2008-09": 25040, "2008-11": 26540,
    "2008-12": 28040, "2009-08": 33645, "2009-12": 37680, "2010-08": 45215,
    "2010-12": 49735, "2011-08": 57200, "2011-12": 62920, "2012-08": 72355,
    "2012-12": 79590, "2013-08": 85560, "2013-09": 91530, "2013-12": 93817.50,
    "2014-01": 96105, "2014-09": 107635, "2014-12": 113017.50, "2015-01": 118400,
    "2015-09": 130240, "2016-10": 149775, "2017-12": 172240, "2018-07": 178270,
    "2018-08": 184300, "2018-11": 202730, "2019-08": 223000, "2020-02": 238610,
    "2020-09": 262470, "2021-09": 289000, "2022-05": 324000, "2023-04": 347000,
    "2023-12": 372000, "2024-01": 428000, "2025-07": 471000
}

# Пользовательские данные
user_data = {}

def get_bvip_for_period(year, month):
    """Получить БВИП для конкретного периода"""
    key = f"{year}-{month:02d}"
    # Найти ближайшую дату, не превышающую заданную
    best_key = None
    for date_key in sorted(BVIP_DATA.keys()):
        if date_key <= key:
            best_key = date_key
        else:
            break
    return BVIP_DATA.get(best_key, 471000)  # По умолчанию последнее значение

def calculate_pension(salaries_data, total_experience):
    """Расчёт пенсии по алгоритму"""
    if len(salaries_data) != 60:
        return "Ошибка: нужны данные за 60 месяцев"
    
    # Средняя БВИП за последний год (2025)
    avg_bvip_2025 = 471000
    
    # Расчёт ИКЗ и пересчёт заработков
    recalculated_salaries = []
    
    for salary_info in salaries_data:
        salary = salary_info['salary']
        year = salary_info['year']
        month = salary_info['month']
        
        # Получаем БВИП для этого периода
        bvip_period = get_bvip_for_period(year, month)
        
        # Рассчитываем ИКЗ
        ikz = salary / bvip_period
        
        # Пересчитанный заработок
        recalculated = ikz * avg_bvip_2025
        recalculated_salaries.append(recalculated)
    
    # Среднемесячный пересчитанный доход
    avg_income = sum(recalculated_salaries) / 60
    
    # Применяем ограничения (с 2024 года - не более 12×БВИП)
    max_income = 12 * avg_bvip_2025
    if avg_income > max_income:
        avg_income = max_income
    
    # Базовая пенсия - 55%
    base_pension = avg_income * 0.55
    
    # Надбавка за стаж свыше 25 лет (до 80% максимум)
    if total_experience > 25:
        extra_years = min(total_experience - 25, 25)  # Максимум 25 дополнительных процентов
        additional_percent = extra_years * 0.01
        base_pension = avg_income * (0.55 + additional_percent)
    
    return {
        'pension': round(base_pension, 2),
        'avg_income': round(avg_income, 2),
        'pension_percent': min(55 + max(0, total_experience - 25), 80)
    }

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💰 Расчёт пенсии", "🧾 Порядок выхода")
    markup.row("👤 Для самозанятых", "ℹ️ Справка")
    
    welcome_text = """
👋 Добро пожаловать в бот "Моя пенсия UZ"!

Я помогу рассчитать размер вашей будущей пенсии по законодательству Республики Узбекистан.

📋 Что я умею:
• Автоматический расчёт пенсии
• Консультации по пенсионному законодательству  
• Информация для самозанятых
• Порядок оформления пенсии

Выберите нужную опцию из меню ⬇️
    """
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💰 Расчёт пенсии")
def pension_calculation(message):
    user_id = message.chat.id
    user_data[user_id] = {'step': 'experience'}
    
    bot.send_message(user_id, 
        "📊 Начинаем расчёт пенсии!\n\n"
        "Введите ваш общий трудовой стаж в годах:\n"
        "(например: 30)")

@bot.message_handler(func=lambda message: message.text == "🧾 Порядок выхода")
def retirement_procedure(message):
    procedure_text = """
📋 ПОРЯДОК ВЫХОДА НА ПЕНСИЮ

👥 Возраст выхода на пенсию:
• Мужчины: 60 лет
• Женщины: 55 лет

📅 Минимальный стаж:
• Для полной пенсии: 25 лет
• Для пропорциональной пенсии: от 7 лет

📄 Необходимые документы:
Услуга проактивная

🏢 Подача заявления:
Услуга проактивная

💰 Размер пенсии:
• 55% от среднего заработка
• +1% за каждый год стажа свыше 25 лет
• Максимум 80% от заработка
    """
    
    bot.send_message(message.chat.id, procedure_text)

@bot.message_handler(func=lambda message: message.text == "👤 Для самозанятых")
def self_employed_info(message):
    self_employed_text = """
👤 ПЕНСИЯ ДЛЯ САМОЗАНЯТЫХ

💼 Кто считается самозанятым:
• Индивидуальные предприниматели
• Физические лица, занимающиеся частной практикой
• Адвокаты, нотариусы
• Фермеры

💰 Размер взносов:
• Минимум: 100% от БРВ в год
• Максимум: доход не должен превышать 8 × БВИП в месяц (до 2022)
• 10 × БВИП (2023), 12 × БВИП (с 2024)
• 1 млн.взноса равен 8.3 млн дохода
📋 Особенности:
• Добровольная система участия
• Самостоятельная уплата взносов
• Стаж засчитывается при регулярной уплате
• Размер пенсии зависит от суммы взносов

📞 Рекомендация:
Обратитесь в территориальный орган пенсионного обеспечения для уточнения индивидуальных условий.
    """
    
    bot.send_message(message.chat.id, self_employed_text)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Справка")
def help_info(message):
    help_text = """
ℹ️ СПРАВОЧНАЯ ИНФОРМАЦИЯ

🔍 Основные понятия:

📊 БВИП - Базовая величина для исчисления пенсий
• Устанавливается государством
• Регулярно индексируется
• Текущий размер: 471 000 сум

💡 ИКЗ - Индивидуальный коэффициент заработка
• Отношение зарплаты к БВИП
• Используется для пересчёта заработка

📈 Формула расчёта пенсии:
1. Берутся доходы за любые 5 лет из последних 10
2. Рассчитывается ИКЗ за каждый месяц  
3. Доходы пересчитываются через текущую БВИП
4. Применяются ограничения по максимуму
5. Пенсия = 55% + стажевые надбавки

❓ Частые вопросы:
• Минимальный стаж: 7 лет
• Максимальный процент пенсии: 80%
• Период для расчёта: 60 месяцев подряд

📞 Поддержка: @support (если есть вопросы)
    """
    
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    
    if user_id in user_data:
        step = user_data[user_id].get('step')
        
        if step == 'experience':
            try:
                experience = int(message.text)
                if experience < 0 or experience > 50:
                    bot.send_message(user_id, "❌ Введите корректный стаж (от 0 до 50 лет)")
                    return
                
                user_data[user_id]['experience'] = experience
                user_data[user_id]['step'] = 'salary_period'
                
                bot.send_message(user_id,
                    "📅 Теперь нужно выбрать период для расчёта зарплат.\n\n"
                    "Введите начальный год и месяц для расчёта зарплат "
                    "(любые 5 лет подряд из последних 10 лет работы).\n\n"
                    "Формат: YYYY-MM (например: 2019-01)")
                
            except ValueError:
                bot.send_message(user_id, "❌ Введите стаж числом (например: 25)")
        
        elif step == 'salary_period':
            try:
                year, month = message.text.split('-')
                year = int(year)
                month = int(month)
                
                if year < 2000 or year > 2025 or month < 1 or month > 12:
                    bot.send_message(user_id, "❌ Введите корректную дату (формат: YYYY-MM)")
                    return
                
                user_data[user_id]['start_year'] = year
                user_data[user_id]['start_month'] = month
                user_data[user_id]['step'] = 'demo_calculation'
                
                # Для демонстрации сделаем упрощённый расчёт
                demo_calculation(user_id)
                
            except:
                bot.send_message(user_id, "❌ Введите дату в формате YYYY-MM (например: 2020-01)")

def demo_calculation(user_id):
    """Демонстрационный расчёт с примерными данными"""
    experience = user_data[user_id]['experience']
    start_year = user_data[user_id]['start_year']
    start_month = user_data[user_id]['start_month']
    
    # Создаём демо-данные зарплат (в реальности пользователь будет вводить сам)
    demo_salaries = []
    base_salary = 5000000  # 5 млн сум базовая зарплата для демо
    
    for i in range(60):  # 60 месяцев
        month = start_month + i % 12
        year = start_year + i // 12
        if month > 12:
            month -= 12
            year += 1
        
        # Варьируем зарплату для реалистичности
        salary = base_salary + (i * 50000)  # Рост зарплаты
        
        demo_salaries.append({
            'salary': salary,
            'year': year,
            'month': month
        })
    
    # Рассчитываем пенсию
    result = calculate_pension(demo_salaries, experience)
    
    result_text = f"""
🎉 РЕЗУЛЬТАТ РАСЧЁТА ПЕНСИИ

👤 Трудовой стаж: {experience} лет
📊 Процент пенсии: {result['pension_percent']}%
💰 Среднемесячный доход: {result['avg_income']:,.0f} сум
🏆 Размер пенсии: {result['pension']:,.0f} сум

📋 Расчёт выполнен на основе:
• Доходы за 60 месяцев начиная с {start_year}-{start_month:02d}
• Действующее законодательство РУз
• Текущая БВИП: 471,000 сум

⚠️ Это предварительный расчёт!
Для точного расчёта обратитесь в пенсионный орган с документами о реальных доходах.

💡 Хотите рассчитать ещё раз? Нажмите "💰 Расчёт пенсии"
    """
    
    # Очищаем данные пользователя
    del user_data[user_id]
    
    bot.send_message(user_id, result_text)

if __name__ == '__main__':
    print("🤖 Бот 'Моя пенсия UZ' запущен!")
    bot.polling(none_stop=True, interval=0,timeout=20)


