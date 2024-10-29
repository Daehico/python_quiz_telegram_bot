from aiogram import Bot, Dispatcher, types
import logging

class BotInitializer:
    
    def __init__(self, api_token):
        self.api_token = api_token
        
    def initializeBot(self):
        logging.basicConfig(level=logging.INFO)
        return Bot(self.api_token)
    
    def initializeDispatcher(self):  
        return Dispatcher()