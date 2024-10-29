import json
import os

class QuizData:
    quiz_data = []

    def __init__(self):
        self.loadDataFromJson()
    
    def loadDataFromJson(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, 'quiz_data.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            self.quiz_data = json.load(file)
           
    def getQuizData(self):
        return self.quiz_data