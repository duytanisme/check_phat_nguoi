import json
import logging
import os
import queue
import re
import threading
import time
from logging.config import dictConfig
from typing import Dict

import pyttsx3
import requests
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent
from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv()

USER_ID = os.getenv("USER_ID")

FINE_STATUS = {
    "PENDING": "Chưa xử phạt",
    "COMPLETE": "Đã xử phạt",
}

PROPERTIES = {
    "ACTION": "Hành vi vi phạm",
    "STATUS": "Trạng thái",
    "TIME": "Thời gian vi phạm",
}

# Setup custom logging
config_file_path = os.path.join(os.getcwd(), "configs", "logging_cfg.json")
with open(config_file_path) as json_file:
    config = json.load(json_file)
    dictConfig(config)
logger = logging.getLogger("default")


def say_message(message_to_say):
    """
    Say a message in Vietnamese.
    :param message_to_say: Message to say.
    :type message_to_say: str
    """
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
        'accept': '*/*', 'content-type': 'application/json',
        'origin': 'https://checkphatnguoi.vn',
        'referer': 'https://checkphatnguoi.vn/', 'user-agent': ua.random,
    }
    json_data = {'bienso': plate_str}

    try:
        response = requests.post('https://api.checkphatnguoi.vn/phatnguoi',
            headers=headers, json=json_data
        )
        return response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
        return {}


def handle_fault(plate_data):
    faults = plate_data.get("data", [])
    if 0 < len(faults) < 10:
        for fault in faults:
            if fault.get(PROPERTIES["STATUS"]) == FINE_STATUS["PENDING"]:
                fault_time = fault.get(PROPERTIES["TIME"])
                fault_action = fault.get(PROPERTIES["ACTION"])
                logger.info(f"{fault_time}: {fault_action}")


def process_plate_queue():
    while True:
        plate = plate_queue.get()
        if plate is None:
            time.sleep(5)
            continue

        plate_number = plate["plate_number"]
        plate_owner = plate['plate_owner']
        message = f"Đang kiểm tra biển {plate_number} của {plate_owner}..."
        logger.info(message)
        say_message(message)

        plate_data = get_plate_data(plate_number)
        if plate_data.get("status") == 1:
            cxp = plate_data.get("data_info", {}).get("chuaxuphat", 0)
            dxp = plate_data.get("data_info", {}).get("daxuphat", 0)
            sum_fault = int(cxp) + int(dxp)
            message = f"Biển số {plate_number} - Vi phạm {sum_fault} lỗi | Chưa xử phạt: {cxp} | Đã xử phạt: {dxp}"
            logger.info(message)
            say_message(message)
            handle_fault(plate_data)

        elif plate_data.get("status") == 2:
            message = f"Biển số {plate_number} - Không có lỗi vi phạm"
            logger.info(message)
            say_message(message)

        elif plate_data.get("status") == 3:
            message = f"Biển số {plate_number} - {plate_data.get('msg')}"
            logger.info(message)
            say_message(message)

        plate_queue.task_done()
        logger.info("-" * 20)


def get_match_plate(input_message):
    cleaned_message = re.sub(r'[^a-zA-Z0-9]', '', input_message.lower())
    pattern = r"\b\d{2}[A-Za-z]\d?-?\d{4,6}\b"
    return re.search(pattern, cleaned_message)


plate_queue = queue.Queue()

threading.Thread(target=process_plate_queue, daemon=True).start()

client = TikTokLiveClient(unique_id=USER_ID)


@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    logger.info(f"Connected to @{event.unique_id} (Room ID: {client.room_id})")


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    comment = event.comment
    match_plate = get_match_plate(comment)
    if match_plate:
        plate_number = match_plate.group()
        plate_queue.put(
            {"plate_owner": event.user.nickname, "plate_number": plate_number}
        )


if __name__ == "__main__":
    client.run()
