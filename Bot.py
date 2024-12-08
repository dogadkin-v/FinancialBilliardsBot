import os
from dotenv import load_dotenv
from telebot import types, TeleBot
from Users import Users
from FileWorker import DataWorker

load_dotenv()

def format_number(num):
    return f"{num:.1f}".rstrip('0').rstrip('.')

class ChatBot:
    def __init__(self, api_token):
        self.bot = TeleBot(api_token)
        self.chat_instances = {}
        self.file = DataWorker()

        @self.bot.message_handler(content_types=['new_chat_members'])
        def welcome_new_member(message):
            for new_member in message.new_chat_members:
                if new_member.id == self.bot.get_me().id:
                    chat_id = message.chat.id
                    chat_instance = ChatInstance(chat_id)
                    self.chat_instances[chat_id] = chat_instance
                    self.file.create(chat_id)
                    self.bot.send_message(chat_id, "Ваш финансовый помощник добавлен в группу. Пожалуйста зарегистрируейте участников игры!")

        @self.bot.chat_member_handler(func=lambda message: True)
        def chat_member_handler(message):
            # Проверяем, является ли бот участником чата и был ли он удален
            if message.new_chat_member.user.id == self.bot.get_me().id:
                if message.new_chat_member.status == 'left':
                    chat_id = message.chat.id
                    self.file.remove(chat_id)
                    print(f"Бот был удален из чата: {chat_id}")

        @self.bot.message_handler(commands=['reg'])
        def start_message(message):
            chat_id = message.chat.id
            if chat_id in self.chat_instances:
                reg_text = self.chat_instances[chat_id].add_user(message)
                self.chat_instances[chat_id].save(self.file)
                self.bot.send_message(chat_id, reg_text)
            else:
                self.bot.send_message(chat_id, "Я не знаю ничего об этом чате.")

        def restore_chat(chat_id):
            if not self.chat_instances:
                data = self.file.load(chat_id)
                self.chat_instances[chat_id] = ChatInstance(chat_id, data)

        @self.bot.message_handler(commands=['game'])
        def start_message(message):
            chat_id = message.chat.id
            restore_chat(chat_id)
            self.chat_instances[chat_id].game(message, self.bot)

        @self.bot.message_handler(commands=['getresult'])
        def start_message(message):
            chat_id = message.chat.id
            restore_chat(chat_id)
            self.chat_instances[chat_id].get_result(message, self.bot)

        @self.bot.message_handler(commands=['pay'])
        def start_message(message):
            chat_id = message.chat.id
            restore_chat(chat_id)
            self.chat_instances[chat_id].pay(message, self.bot)
            self.chat_instances[chat_id].save(self.file)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handlers(call: types.CallbackQuery):
            chat_id = call.message.chat.id
            self.chat_instances[chat_id].callback_handlers(call, self.bot)
            self.chat_instances[chat_id].save(self.file)

    def run(self):
        self.bot.polling(none_stop=True)

class ChatInstance:
    def __init__(self, chat_id, users_data=None):
        self.chat_id = chat_id
        self.users = Users(users_data)

    def add_user(self, message):
        self.users.add_user({
            'id': message.from_user.id,
            'name': message.from_user.full_name
        })
        return f'Пользователь: {message.from_user.full_name} успешно зарегистрирован!'

    def save(self, file):
        file.save(self.chat_id, self.users.users)

    def game(self, message, bot):
        bot.send_message(message.chat.id, 'Выберите победителя:', reply_markup=self.game_keyboard())

    def get_result(self, message, bot):
        loser = self.users.get_loser()
        if loser is None:
            text = 'Никто ничего не должен'
        else:
            main_message = f'{loser["name"]} должен {format_number(loser["sum_debt"])}'
            bonus_message = f'+ коммиссия {format_number(loser["debt_bonus"])} руб.' if loser['debt_bonus'] else ''
            text = f'{main_message} {bonus_message}'
        bot.send_message(message.chat.id, text)

    def pay(self, message, bot):
        self.users.pay_off_debt()
        text = f'Пользователь {message.from_user.full_name} обнулил долг'
        bot.send_message(message.chat.id, text)
        self.get_result(message, bot)

    def game_keyboard(self):
        return types.InlineKeyboardMarkup(
            keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=user['name'],
                        callback_data=user["id"]
                    )
                ]
                for user in self.users.get_users()
            ]
        )

    def callback_handlers(self, call: types.CallbackQuery, bot):
        self.users.set_win(int(call.data))
        self.get_result(call.message, bot)



if __name__ == "__main__":
    API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_bot = ChatBot(API_TOKEN)
    chat_bot.run()