import asyncio
from botInitializer import BotInitializer
from botCommandHandler import BotCommandHandler
from quizData import QuizData
from databaseHandler import DatabaseHandler

API_TOKEN = '' #Токен замазан, так как репозиторий публичный
DB_NAME = 'quiz_bot.db'

async def main():    
    botInitializerClass = BotInitializer(API_TOKEN)
    bot =  botInitializerClass.initializeBot()
    dp = botInitializerClass.initializeDispatcher()
    quizData = QuizData()
    dbHandler = DatabaseHandler(DB_NAME)
    await dbHandler.create_table()
    botCommandHandler = BotCommandHandler(dp, quizData, dbHandler, bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())