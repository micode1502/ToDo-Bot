from db.database import create_db
from bot.utils import get_conversation_state, set_conversation_state, list_user_tasks, delete_task
from bot.scheduler import schedule_task
import re
import random
from datetime import datetime, timedelta

DATE_FORMAT_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TIME_FORMAT_REGEX = re.compile(r'^\d{2}:\d{2}$')

POSITIVE = ["😊", "😃", "🎉", "🌟", "👍", "🙌", "🤗", "💪", "🎊", "✨"]
NEGATIVE = ["❌", "⚠️", "🚫", "😔", "😕", "😢", "😫", "🤯"]

def get_random_emoji_positive():
    return random.choice(POSITIVE)

def get_random_emoji_negative():
    return random.choice(NEGATIVE)

async def handle_message(from_number: str, body: str):
    await create_db()

    message = body.strip().lower()
    print(f"Mensaje recibido: {message}")

    state, task_details = await get_conversation_state(from_number)
    now = datetime.now()

    if state == "waiting_for_task_title":
        task_details['title'] = message
        await set_conversation_state(from_number, "waiting_for_task_date", task_details)
        return f"¿Cuál es la fecha para la tarea? {get_random_emoji_positive()}\n(Formato: YYYY-MM-DD)"

    elif state == "waiting_for_task_date":
        if not DATE_FORMAT_REGEX.match(message):
            return f"Formato de fecha incorrecto. Por favor, usa el formato YYYY-MM-DD. {get_random_emoji_negative()}"
        
        task_date_str = message
        task_date = datetime.strptime(task_date_str, "%Y-%m-%d").date()
        
        if task_date < now.date():
            return f"La fecha debe ser igual o posterior a hoy. {get_random_emoji_negative()}"
        
        task_details['date'] = task_date_str
        await set_conversation_state(from_number, "waiting_for_task_time", task_details)
        return f"¿A qué hora se debe realizar la tarea? {get_random_emoji_positive()}\n(Formato: HH:MM)"
    
    elif state == "waiting_for_task_time":
        if 'date' not in task_details:
            return "No se ha definido una fecha para la tarea. Por favor, vuelve a proporcionar la fecha."

        if not TIME_FORMAT_REGEX.match(message):
            return f"Formato de hora incorrecto. Por favor, usa el formato HH:MM. {get_random_emoji_negative()}"
        
        task_date_str = task_details['date']
        task_date = datetime.strptime(task_date_str, "%Y-%m-%d").date()
        task_time_str = message
        task_time = datetime.strptime(task_time_str, "%H:%M").time()
        
        task_datetime = datetime.combine(task_date, task_time)
        
        if task_datetime < now + timedelta(minutes=5):
            return f"La tarea debe ser programada al menos 5 minutos después del momento actual. {get_random_emoji_negative()}"
        
        task_details['time'] = task_time_str
        await set_conversation_state(from_number, "waiting_for_task_priority", task_details)
        return f"¿Cuál es la prioridad de la tarea? {get_random_emoji_positive()}\n(alta, media, baja)"

    elif state == "waiting_for_task_priority":
        if message in ["alta", "media", "baja"]:
            task_details['priority'] = message
            await set_conversation_state(from_number, None)
            await schedule_task(from_number, task_details)
            return f"¡Tarea añadida exitosamente! {get_random_emoji_positive()}"
        else:
            return f"Prioridad inválida. Por favor, elige entre 'alta', 'media' o 'baja'. {get_random_emoji_negative()}"

    if message in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches"]:
        await set_conversation_state(from_number, "waiting_for_task_confirmation")
        return f"¡Hola! ¿Deseas añadir una tarea? Responde 'sí' para continuar o 'no' para cancelar. {get_random_emoji_positive()}"

    elif state == "waiting_for_task_confirmation":
        if message in ["sí", "si", "yes"]:
            await set_conversation_state(from_number, "waiting_for_task_title")
            return f"Perfecto, dime el título de la tarea. {get_random_emoji_positive()}"
        else:
            await set_conversation_state(from_number, None)
            return f"Entendido. Si necesitas algo más, aquí estoy. {get_random_emoji_positive()}"

    elif message.startswith("que tareas tengo"):
        tasks = await list_user_tasks(from_number)
        if tasks:
            tasks_list = "\n".join(f"{i + 1}. {task}" for i, task in enumerate(tasks))
            await set_conversation_state(from_number, "waiting_for_task_deletion")
            return f'''Tus tareas pendientes {get_random_emoji_positive()}:\n{tasks_list}
                    \n\n¿Deseas eliminar una tarea? Responde 'sí' para continuar o 'no' para cancelar.'''
        else:
            return f"No tienes tareas pendientes. {get_random_emoji_negative()}"

    elif state == "waiting_for_task_deletion":
        if message in ["sí", "si", "yes"]:
            await set_conversation_state(from_number, "waiting_for_task_number")
            return f"Por favor, indica el número de la tarea que deseas eliminar (por ejemplo, '1'). {get_random_emoji_positive()}"
        else:
            await set_conversation_state(from_number, None)
            return f"Entendido. Si necesitas algo más, aquí estoy. {get_random_emoji_positive()}"

    elif state == "waiting_for_task_number":
        if message.isdigit():
            task_number = int(message) - 1
            tasks = await list_user_tasks(from_number)
            if 0 <= task_number < len(tasks):
                task_to_delete = tasks[task_number].split(' - ')[0]
                await delete_task(from_number, task_to_delete)
                await set_conversation_state(from_number, None)
                return f"Tarea eliminada exitosamente. {get_random_emoji_positive()}"
            else:
                return f"Número de tarea inválido. Por favor, elige un número de la lista. {get_random_emoji_negative()}"
        else:
            return f"Por favor, proporciona un número válido. {get_random_emoji_negative()}"

    else:
        return f"Lo siento, solo puedo ayudarte a gestionar tareas pendientes. {get_random_emoji_negative()}"
