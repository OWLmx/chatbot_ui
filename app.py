import chainlit as cl
from chainlit.server import app
from chainlit.session import Session
from chainlit.context import init_context
from chainlit.input_widget import TextInput, Select

from fastapi import Request
from fastapi.responses import (
    HTMLResponse,
)

import requests
import json

# from chainlit import user_session
session_id = None # TODO: this works only for a POC on localhost... we would need a way to map request with session_id in a real multiuser setting

# URL = "http://localhost:5005/webhooks/rest/webhook"
URL = "http://localhost:5005/webhooks/stoa_app/webhook" # customo channel filtering out context scope flags 



# @cl.on_chat_start
# async def start():
#     print("JJAAAA")
#     await cl.Text(name="simple_text", content="owl xxs", display="side").send()

@cl.on_chat_start
async def start():
    global session_id
    session_id = cl.user_session.get("id")
    print(f"SessionID: {session_id}")


    settings = await cl.ChatSettings(
        [
            TextInput(id="AgentName", label="Agent Name", initial="AI"),
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            )
        ]
    ).send()
    value = settings["AgentName"]
    value = settings["Model"]


    # await cl.Text(content="Here is a page text document", name="text2", display="side").send()

    # elements = [
    #     cl.Text(content="Here is a page text document", name="text1", display="side")
    # ]

    # # Send the same message twice
    # content = "Here is image1, a nice image of a cat! As well as text1 and text2!"

    # await cl.Message(
    #     content=content,
    #     elements=elements
    # ).send()

    # await cl.Message(
    #     content=content,
    # ).send()    



def _process_message(message:str) -> str:
    # payload = {"sender": "chainlit", "message": message} 
    payload = {"sender": "owlmx", "message": message} 

    print(f"\n\n\n==============================")
    print(payload)

    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", URL, headers=headers, data=json.dumps(payload))

    response = json.loads(response.text)

    print(f"-->\n\n{response}\n\n<--")

    return response


@cl.on_message
async def main(message: str):
    # Your custom logic goes here...
    rss = _process_message(message)

    print(f"User session---> {cl.user_session.get('id')}")

    # Send a response back to the user
    for rs in rss:
        await cl.Message(
            content=f"{rs.get('text', '-')}",
        ).send()


# ============== Custom Endpoint for RASA callback ======================
@app.post("/bot")
async def rasa_callback(request: Request):
    # pass
    if not session_id:
        return HTMLResponse("No session id found")

    print(f"C-SessionID: {session_id}")

    # rs = cl.run_sync(request.json())
    rs = await (request.json())
    # session_idx = rs.get('session')
    # print(f"Received session= {session_idx}")
    # cl.user_session.set("id", session_id)
    # print(f"BBBB User session---> {cl.user_session.get('id')}")

    session = Session.get_by_id(session_id)
    init_context(session)
    await cl.Message(
            content=f"{rs.get('text', '-')}",
        ).send()



@app.get("/hello")
async def hello(request: Request):
    if not session_id:
        return HTMLResponse("No session id found")

    print(f"B-SessionID: {session_id}")

    session = Session.get_by_id(session_id)
    init_context(session)

    await cl.Message(content="Hello from custom endpoint").send()




