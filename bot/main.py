from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from bot.handlers import handle_message
from db.database import create_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await create_db()

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    from_number = form_data['From']
    body = form_data['Body']

    reply = await handle_message(from_number, body)

    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)

    # Devolver la respuesta de Twilio correctamente
    return Response(content=str(twilio_resp), media_type="application/xml")
