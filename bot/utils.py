import aiosqlite
from db.models import Task
import json

async def list_user_tasks(phone_number: str):
    tasks = []
    async with aiosqlite.connect('todobot.db') as db:
        async with db.execute('''
                                SELECT tasks.title, tasks.date, tasks.time, tasks.priority 
                                FROM tasks JOIN users ON tasks.user_id = users.id 
                                WHERE users.phone_number = ?''', 
                                (phone_number,)) as cursor:
            async for row in cursor:
                task = Task(None, None, row[0], row[1], row[2], row[3])
                tasks.append(f"{task.title} - {task.date} {task.time} ({task.priority})")
    return tasks

async def get_conversation_state(phone_number):
    async with aiosqlite.connect('todobot.db') as db:
        async with db.execute('''
                                SELECT state, task_details 
                                FROM conversation_state 
                                WHERE phone_number = ?''', 
                                (phone_number,)) as cursor:
            row = await cursor.fetchone()
            if row:
                state, task_details = row
                return state, json.loads(task_details) if task_details else {}
            return None, {}

async def set_conversation_state(phone_number, state, task_details=None):
    task_details_json = json.dumps(task_details) if task_details else None
    async with aiosqlite.connect('todobot.db') as db:
        if task_details_json:
            await db.execute('''
            INSERT INTO conversation_state (phone_number, state, task_details)
            VALUES (?, ?, ?)
            ON CONFLICT(phone_number) DO UPDATE SET state = ?, task_details = ?
            ''', (phone_number, state, task_details_json, state, task_details_json))
        else:
            await db.execute('''
            INSERT INTO conversation_state (phone_number, state)
            VALUES (?, ?)
            ON CONFLICT(phone_number) DO UPDATE SET state = ?
            ''', (phone_number, state, state))
        await db.commit()

async def delete_task(phone_number: str, task_title: str):
    async with aiosqlite.connect('todobot.db') as db:
        async with db.execute('''
            SELECT id FROM users WHERE phone_number = ?
        ''', (phone_number,)) as cursor:
            user_id_row = await cursor.fetchone()
            if user_id_row:
                user_id = user_id_row[0]
                
                await db.execute('''
                    DELETE FROM tasks WHERE user_id = ? AND title = ?
                ''', (user_id, task_title))
                await db.commit()
