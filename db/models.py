from dataclasses import dataclass

@dataclass
class User:
    id: int
    phone_number: str

@dataclass
class Task:
    id: int
    user_id: int
    title: str
    date: str
    time: str
    priority: str

@dataclass
class ConversationState:
    phone_number: str
    state: str
    task_details: str