from apscheduler.schedulers.asyncio import AsyncIOScheduler
from twilio.rest import Client
from datetime import datetime
import aiosqlite
from config.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

scheduler = AsyncIOScheduler()
scheduler.start()

def send_reminder(phone_number, task_title, task_date, task_time, task_priority):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Recuerdo de la tarea pendiente 😃😊:\nTítulo: {task_title}\nFecha: {task_date}\nHora: {task_time}\nPrioridad: {task_priority}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"Mensaje enviado a {phone_number}: {message.sid}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

async def schedule_task(phone_number, task_details):
    task_time_str = f"{task_details['date']} {task_details['time']}"
    
    try:
        task_time = datetime.strptime(task_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"Error en el formato de fecha/hora: {task_time_str}")
        return
    
    async with aiosqlite.connect('todobot.db') as db:
        async with db.execute('SELECT id FROM users WHERE phone_number = ?', (phone_number,)) as cursor:
            user = await cursor.fetchone()
            if user is None:
                await db.execute('INSERT INTO users (phone_number) VALUES (?)', (phone_number,))
                await db.commit()
                async with db.execute('SELECT id FROM users WHERE phone_number = ?', (phone_number,)) as cursor2:
                    user = await cursor2.fetchone()
        
        user_id = user[0]
        await db.execute('''
                        INSERT INTO tasks (user_id, title, date, time, priority) 
                        VALUES (?, ?, ?, ?, ?)''',
                        (user_id, task_details['title'], task_details['date'], 
                        task_details['time'], task_details['priority']))
        await db.commit()

    scheduler.add_job(
        send_reminder,
        'date',
        run_date=task_time,
        args=[phone_number, task_details['title'], task_details['date'], task_details['time'], task_details['priority']]
    )
    print(f"Tarea programada para {task_time}.")
