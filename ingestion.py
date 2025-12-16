import json
import threading
import time
import websocket
from storage import store_tick

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("e") == "trade":
            tick = {
                "symbol": data["s"].lower(),
                "timestamp": data["T"],
                "price": float(data["p"]),
                "size": float(data["q"])
            }
            store_tick(tick)
    except Exception as e:
        print("Message parse error:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed:", close_status_code, close_msg)

def on_open(ws):
    print("WebSocket connection opened")

def start_socket(symbol):
    url = f"wss://fstream.binance.com/ws/{symbol}@trade"

    while True:
        try:
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print(f"Reconnecting {symbol} after error:", e)

        time.sleep(5)  # prevent aggressive reconnects

def start_ingestion(symbols):
    for sym in symbols:
        t = threading.Thread(
            target=start_socket,
            args=(sym,),
            daemon=True
        )
        t.start()
