from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from quizData import QuizData
from databaseHandler import DatabaseHandler

class BotCommandHandler:
    def __init__(self, dp: Dispatcher, quizData: QuizData, dbHandler: DatabaseHandler, bot: Bot):
        self.dp = dp
        self.bot = bot
        self.quizData = quizData.getQuizData()
        self.dbHandler = dbHandler
        self.register_handlers()
        
    def register_handlers(self):
        @self.dp.message(Command("start"))
        async def cmd_start(message: types.Message):
            builder = ReplyKeyboardBuilder()
            builder.add(types.KeyboardButton(text="Начать игру"))
            builder.add(types.KeyboardButton(text="Статистика"))
            await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

        @self.dp.message(F.text == "Начать игру")
        @self.dp.message(Command("quiz"))
        async def cmd_quiz(message: types.Message):
            await message.answer("Давайте начнем квиз! Первый вопрос: ...",  reply_markup=types.ReplyKeyboardRemove())
            await self.new_quiz(message)
            
        @self.dp.message(F.text == "Статистика")
        @self.dp.message(Command("results"))
        async def cmd_quiz(message: types.Message):
            await message.answer("Сейчас покажу вашу статистику!")
            await self.display_results(message.from_user.id)

        @self.dp.callback_query(F.data == "right_answer")
        async def right_answer(callback: types.CallbackQuery):
            user_id = callback.from_user.id
            current_question_index = await self.dbHandler.get_quiz_index(user_id)
            question = self.quizData[current_question_index]
            correct_option = question['correct_option']
            user_answer = question['options'][correct_option]
            
            await callback.message.answer(f"Вы выбрали: {user_answer} - Верно!")
            current_question_index += 1
            await self.dbHandler.update_quiz_index(user_id, current_question_index)

            await self.dbHandler.save_result(user_id, 1)

            if current_question_index < len(self.quizData):
                await self.get_question(callback.message, user_id)
            else:
                await callback.message.answer("Это был последний вопрос. Квиз завершен!")
                await self.display_results(user_id)
                
                builder = ReplyKeyboardBuilder()
                builder.add(types.KeyboardButton(text="Начать игру"))
                builder.add(types.KeyboardButton(text="Статистика"))
                await callback.message.answer("Вы можете начать новый квиз или посмотреть статистику.", reply_markup=builder.as_markup(resize_keyboard=True))
                
            await callback.message.edit_reply_markup()

        @self.dp.callback_query(F.data == "wrong_answer")
        async def wrong_answer(callback: types.CallbackQuery):
            user_id = callback.from_user.id
            current_question_index = await self.dbHandler.get_quiz_index(user_id)

            question = self.quizData[current_question_index]
            correct_option = question['correct_option']
            await callback.message.answer(f"Неправильно. Правильный ответ: {question['options'][correct_option]}.")

            current_question_index += 1
            await self.dbHandler.update_quiz_index(user_id, current_question_index)

            await self.dbHandler.save_result(user_id, 0)

            if current_question_index < len(self.quizData):
                await self.get_question(callback.message, user_id)
            else:
                await callback.message.answer("Это был последний вопрос. Квиз завершен!")
                await self.display_results(user_id)
                
                builder = ReplyKeyboardBuilder()
                builder.add(types.KeyboardButton(text="Начать игру"))
                builder.add(types.KeyboardButton(text="Статистика"))
                await callback.message.answer("Вы можете начать новый квиз или посмотреть статистику.", reply_markup=builder.as_markup(resize_keyboard=True))
                
            await callback.message.edit_reply_markup()

    async def new_quiz(self, message):
        user_id = message.from_user.id
        await self.dbHandler.reset_result(user_id)
        current_question_index = 0
        await self.dbHandler.update_quiz_index(user_id, current_question_index)
        await self.get_question(message, user_id)

    async def get_question(self, message, user_id):
        current_question_index = await self.dbHandler.get_quiz_index(user_id)
        if current_question_index >= len(self.quizData):
            await message.answer("Это был последний вопрос. Квиз завершен!")
            return

        question = self.quizData[current_question_index]
        correct_index = question['correct_option']
        opts = question['options']
        kb = self.generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"{question['question']}", reply_markup=kb)

    def generate_options_keyboard(self, answer_options, right_answer):
        builder = InlineKeyboardBuilder()
        for option in answer_options:
            builder.add(types.InlineKeyboardButton(
                text=option,
                callback_data="right_answer" if option == right_answer else "wrong_answer"  
            ))
        builder.adjust(1)
        return builder.as_markup()
            
    async def display_results(self, user_id):
        score = await self.dbHandler.get_scores(user_id)
        await self.bot.send_message(user_id, f"Ваш результат: {score['score']}")
             
    async def get_question(self, message, user_id):
        current_question_index = await self.dbHandler.get_quiz_index(user_id)
        correct_index = self.quizData[current_question_index]['correct_option']
        opts = self.quizData[current_question_index]['options']
        kb = self.generate_options_keyboard(opts, opts[correct_index])
        await message.answer(f"{self.quizData[current_question_index]['question']}", reply_markup=kb)
    
    