from typing import Dict

import requests
from fake_useragent import UserAgent


def get_plate_data(plate_str):
    """
    Get plate data.
    :param plate_str: Plate number.
    :type plate_str: str
    :return: Plate data.
    :rtype: Dict[str, str]
    """
    ua = UserAgent()
    random_ua = ua.random

    headers = {
        'accept': '*/*',
        'accept-language': 'vi,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://checkphatnguoi.vn',
        'priority': 'u=1, i',
        'referer': 'https://checkphatnguoi.vn/',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': random_ua,
    }
    json_data = {
        'bienso': plate_str,
    }

    try:
        response = requests.post('https://api.checkphatnguoi.vn/phatnguoi',
                                 headers=headers, json=json_data
                                 )
        return response.json()
    except Exception as e:
        print(e)


def main():
    while True:
        plate = input("Plate number: ")
        plate_data = get_plate_data(plate)

        if plate_data.get("status") == 1:
            cxp = plate_data.get("data_info", {}).get("chuaxuphat") or 0
            dxp = plate_data.get("data_info", {}).get("daxuphat") or 0
            sum_fault = int(cxp) + int(dxp)
            print(f"Phương tiện {plate} - Vi phạm {sum_fault} lỗi")
            print(f"Chưa xử phạt: {cxp}")
            print(f"Đã xử phạt: {dxp}")

        elif plate_data.get("status") == 2:
            print(f"Phương tiện {plate} - Chưa phát hiện lỗi vi phạm nào")

        elif plate_data.get("status") == 3:
            print(f"Phương tiện {plate} - {plate_data.get("msg")}")


if __name__ == '__main__':
    main()
