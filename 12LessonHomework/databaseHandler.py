import aiosqlite

class DatabaseHandler:
    def __init__(self, db_name):
        self.db_name = db_name 

    async def create_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
            await db.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0)''')
            await db.commit()
            
    async def update_quiz_index(self, user_id, index):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
            await db.commit()
            
    async def get_quiz_index(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id, )) as cursor:
                results = await cursor.fetchone()
                if results is not None:
                    return results[0]
                else:
                    return 0
    
    async def save_result(self, user_id, score):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO users (user_id, score) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET score = score + excluded.score
            ''', (user_id, score))
            await db.commit()
    
    async def reset_result(self, user_id):
         async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE users SET score = ? WHERE user_id = ?', (0, user_id))
            await db.commit()

    async def get_scores(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT user_id, score FROM users WHERE user_id = ?', (user_id, )) as cursor:
                result = await cursor.fetchone()
                if result: 
                    return {'user_id': result[0], 'score': result[1]}
                else:
                    return {'user_id': user_id, 'score': 0}