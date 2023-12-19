import asyncio

import js as js
from pyodide.http import pyfetch
import json
from datetime import datetime


async def fetch(url, method, payload=None):
    kwargs = {
        "method": method
    }
    if method == "POST":
        kwargs["body"] = json.dumps(payload)
        kwargs["headers"] = {"Content-Type": "application/json"}
    return await pyfetch(url, **kwargs)


def set_timeout(delay, callback):
    def sync():
        asyncio.get_running_loop().run_until_complete(callback())

    asyncio.get_running_loop().call_later(delay, sync)


sender = ''

el_confirm_sender = js.document.getElementById("confirm_sender")
el_send_message = js.document.getElementById("send_message")
el_sender = js.document.getElementById("sender")
el_message_text = js.document.getElementById("message_text")
el_chat_window = js.document.getElementById("chat_window")
el_message_group = js.document.getElementById("message_group")
el_user_list = js.document.getElementById("user_list")

async def delete_message(e):
    id = e.target.id
    if not id:
        id = e.target.parentElement.id
    
    message = js.document.getElementById(f'message_{id}')
    message.remove()
    await fetch(f"/delete_message?id={id}", method="GET")
    
def append_messages(messages):
    el_chat_window.innerHTML = ''
    
    for message in messages:
        el_item = js.document.createElement("li")
        el_item.className = "list-group-item d-flex justify-content-between"
        el_item.id = f'message_{message["id"]}'
        
        el_item.innerHTML = f'<span>[<b>{message["sender"]}</b>]: <span>{message["text"]}</span><span class="badge text-bg-light text-secondary">{datetime.strptime(message["time"], "%a, %d %b %Y %H:%M:%S %Z").strftime("%H:%M")}</span></span>'
        
        if sender == message['sender']:
            el_button = js.document.createElement("button")
            el_button.className = 'btn btn-danger'
            el_button.innerHTML = 'X'
            el_button.id = str(message['id'])
            el_button.onclick = delete_message
            el_item.append(el_button)
        
        el_chat_window.prepend(el_item)

def append_users(users):
    el_user_list.innerHTML = ''
    for user in users:
        item = js.document.createElement("li")
        item.className = "list-group-item"
        
        item.innerHTML = user
        el_user_list.prepend(item)

async def confirm_sender_click(e):
    global sender
    
    sender = el_sender.value
    
    if len(sender) == 0:
        js.alert('Введите имя')
        return
    
    el_sender.disabled = True
    el_send_message.disabled = False
    await load_fresh_messages()
    await load_users()
    
async def send_message_click(e):
    global sender
    
    await fetch(f"/send_message?sender={sender}&text={el_message_text.value}", method="GET")
    
    el_message_text.value = ""

async def logout(e):
    global sender
    
    e.preventDefault()
    e.returnValue = ''
    
    if len(sender) != 0:
        await fetch(f"/logout?sender={sender}", method="GET")

async def load_fresh_messages():
    global sender
    
    result = await fetch(f"/get_messages?sender={sender}", method="GET")
    data = await result.json()
    messages = data["messages"]
    append_messages(messages)
    set_timeout(1, load_fresh_messages)
    
async def load_users():
    result = await fetch("/get_users", method="GET")
    data = await result.json()
    append_users(data)
    set_timeout(1, load_users)


el_send_message.onclick = send_message_click
el_confirm_sender.onclick = confirm_sender_click
js.window.onbeforeunload = logout

# load_users()