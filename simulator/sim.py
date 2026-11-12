import os
import random
import time

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEVICE_API_KEY = os.environ["DEVICE_API_KEY"]
INTERVAL = float(os.getenv("SIM_INTERVAL", "3"))
EMPTY_ROOMS = {n.strip() for n in os.getenv("SIM_EMPTY_ROOMS", "Room 3").split(",") if n.strip()}

COMFORT_C = 19.5
HEATER_TARGET_C = 21.5


def next_temperature(temp, room):
    if room["cold_fault"]:
        temp -= 0.4
    if room["heater_on"] and not room["heater_failed"]:
        if temp < HEATER_TARGET_C:
            temp += 0.6
    elif not room["cold_fault"]:
        temp += (COMFORT_C - temp) * 0.05
    temp += random.uniform(-0.05, 0.05)
    return round(max(temp, 8.0), 2)


def main():
    temps = {}
    print(f"Simulator sending to {API_URL} every {INTERVAL}s")
    with httpx.Client(base_url=API_URL, timeout=5, headers={"X-API-Key": DEVICE_API_KEY}) as client:
        while True:
            try:
                resp = client.get("/api/rooms")
                resp.raise_for_status()
                for room in resp.json():
                    temp = next_temperature(temps.get(room["id"], COMFORT_C), room)
                    temps[room["id"]] = temp
                    occupied = room["name"] not in EMPTY_ROOMS
                    client.post("/api/readings", json={
                        "room_id": room["id"], "temperature": temp, "occupied": occupied,
                    }).raise_for_status()
                    heater = " [heater on]" if room["heater_on"] else ""
                    print(f"{room['name']}: {temp:.1f}°C {'occupied' if occupied else 'empty'}{heater}")
            except httpx.HTTPError as exc:
                print(f"API error: {exc}")
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main()