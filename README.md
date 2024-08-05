# ToDo-Bot

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat)
![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white&style=flat)
![Twilio](https://img.shields.io/badge/-Twilio-009688?logo=twilio&logoColor=white&style=flat)
![SQLite](https://img.shields.io/badge/-SQLite-009688?logo=sqlite&logoColor=white&style=flat)

ToDo Bot is a task management bot that allows you to manage your tasks through SMS messages. Built by micode1502, this bot enables users to add, view, and delete tasks using a simple text interface. The bot is integrated with Twilio for SMS communication and uses SQLite for task management.

## Features

- **Add Tasks**: Easily add tasks with a title, date, time, and priority.
- **View Tasks**: List all pending tasks.
- **Delete Tasks**: Remove tasks by selecting their number from the task list.

## Technologies

- **Python 3.11.0**: The programming language used for building the bot.
- **Twilio**: SMS service used for communication.
- **SQLite**: Lightweight database used for storing tasks and user information.

## Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/micode1502/ToDo-Bot
   cd todo-bot
   ```

2. **Install Dependencies**

   ```bash
    curl -sSL https://install.python-poetry.org | python3 --
    poetry add fastapi
    poetry add twilio
    poetry add aiosqlite
    poetry add apscheduler
    poetry add python-dotenv
    poetry add uvicorn
    poetry add python-multipart
   ```

3. **Configure Twilio**

   - Sign up for a Twilio account and obtain your Account SID, Auth Token, and a Twilio phone number.
   - Set the environment variables `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_PHONE_NUMBER`.

4. **Run the Bot**

   ```bash
    uvicorn bot.main:app --reload
   ```

## Usage

- **Hello**: Start the interaction or see if you need to add a new task.
- **List Tasks**: See all your current tasks.
- **Add Task**: Provide task details like title, date, time, and priority.
- **Delete Task**: Remove a task by specifying its number from the list.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

This bot was created by micode1502.