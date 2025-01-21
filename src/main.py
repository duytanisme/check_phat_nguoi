import os
import queue
import re
import threading
import time
import pyttsx3
from typing import Dict

import requests
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent
from fake_useragent import UserAgent

from dotenv import load_dotenv

load_dotenv()

USER_ID = os.getenv("USER_ID")


def say_message(message_to_say):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # noinspection PyUnresolvedReferences
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 130)

    engine.say(message_to_say)
    engine.runAndWait()


def get_plate_data(plate_str: str) -> Dict[str, str]:
    ua = UserAgent()
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://checkphatnguoi.vn',
        'referer': 'https://checkphatnguoi.vn/',
        'user-agent': ua.random,
    }
    json_data = {'bienso': plate_str}

    try:
        response = requests.post('https://api.checkphatnguoi.vn/phatnguoi',
                                 headers=headers, json=json_data
                                 )
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}


def process_plate_queue():
    while True:
        plate = plate_queue.get()
        if plate is None:
            time.sleep(5)
            continue

        print(f"Processing plate {plate}")
        message = None

        plate_data = get_plate_data(plate)
        if plate_data.get("status") == 1:
            cxp = plate_data.get("data_info", {}).get("chuaxuphat", 0)
            dxp = plate_data.get("data_info", {}).get("daxuphat", 0)
            sum_fault = int(cxp) + int(dxp)
            message = f"Biển số {plate} - Vi phạm {sum_fault} lỗi | Chưa xử phạt: {cxp} | Đã xử phạt: {dxp}"

        elif plate_data.get("status") == 2:
            message = f"Biển số {plate} - Không có lỗi vi phạm"

        elif plate_data.get("status") == 3:
            message = f"Biển số {plate} - {plate_data.get('msg')}"

        print(message)
        say_message(message)

        plate_queue.task_done()
        print("-" * 20)


def get_match_plate(id_string):
    pattern = r"\b\d{2}[A-Za-z]\d?-?\d{4,5}\b"
    return re.search(pattern, id_string)


plate_queue = queue.Queue()

threading.Thread(target=process_plate_queue, daemon=True).start()

client = TikTokLiveClient(unique_id=USER_ID)


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id})")


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    comment = event.comment
    match_plate = get_match_plate(comment)
    if match_plate:
        plate = match_plate.group()
        plate_queue.put(plate)


if __name__ == "__main__":
    client.run()
