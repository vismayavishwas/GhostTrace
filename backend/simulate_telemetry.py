import time
import httpx

BACKEND_URL = "http://127.0.0.1:8000/api/v1/telemetry/events"

def send_copy_paste_sequence(run_number: int):
    print(f"\n--- Simulating Live Browser Copy-Paste Sequence Run #{run_number} ---")
    
    events = [
        {
            "event_type": "CLICK",
            "active_tab": "Source Document - Google Docs / Word",
            "url": "https://docs.company.com/document/101",
            "target_selector": "#doc-text-body",
            "xpath": "//div[@id='doc-text-body']",
            "bounding_box": {"x": 100, "y": 200, "width": 400, "height": 300},
            "scroll_pos": {"x": 0, "y": 100},
            "coordinates_x": 300.0,
            "coordinates_y": 250.0,
            "app_title": "Google Chrome (Document)"
        },
        {
            "event_type": "COPY",
            "active_tab": "Source Document - Google Docs / Word",
            "url": "https://docs.company.com/document/101",
            "target_selector": "#doc-text-body",
            "xpath": "//div[@id='doc-text-body']",
            "input_masked": "Invoice Item #1042",
            "coordinates_x": 300.0,
            "coordinates_y": 250.0,
            "app_title": "Google Chrome (Document)"
        },
        {
            "event_type": "CLICK",
            "active_tab": "SAP ERP / Word Table Portal",
            "url": "https://sap.company.com/table",
            "target_selector": f"#table-row-{run_number}-cell-1",
            "xpath": f"//tr[{run_number}]/td[1]",
            "bounding_box": {"x": 600, "y": 200 + run_number * 30, "width": 150, "height": 30},
            "coordinates_x": 675.0,
            "coordinates_y": float(215 + run_number * 30),
            "app_title": "Google Chrome (Word Table)"
        },
        {
            "event_type": "PASTE",
            "active_tab": "SAP ERP / Word Table Portal",
            "url": "https://sap.company.com/table",
            "target_selector": f"#table-row-{run_number}-cell-1",
            "xpath": f"//tr[{run_number}]/td[1]",
            "input_masked": "Invoice Item #1042",
            "coordinates_x": 675.0,
            "coordinates_y": float(215 + run_number * 30),
            "app_title": "Google Chrome (Word Table)"
        }
    ]

    for evt in events:
        try:
            res = httpx.post(BACKEND_URL, json=evt, timeout=5.0)
            print(f"  [Transmitted] {evt['event_type']} -> Status {res.status_code}")
        except Exception as e:
            print(f"  [Error] {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    print("=== GhostTrace AI Live Telemetry Event Simulator ===")
    print("Transmitting 3 sequence repetitions to live backend...")
    for i in range(1, 4):
        send_copy_paste_sequence(i)
        time.sleep(1.0)
    print("\n[OK] Completed! GhostTrace backend has processed pattern discovery.")
