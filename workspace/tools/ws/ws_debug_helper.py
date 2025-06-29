# workspace/tools/ws/ws_debug_helper.py

import time
from collections import defaultdict
from threading import Lock

_debug_start_times = {}
_debug_arrival_times = {}
_retry_failures = []
_debug_lock = Lock()


def mark_task_start(oid: str):
    """標記任務開始時間（由子控在 run_task 開頭呼叫）"""
    with _debug_lock:
        _debug_start_times[oid] = time.time()


def mark_callback_arrival(oid: str, event_name: str):
    """記錄某個封包事件抵達的時間與延遲秒數"""
    now = time.time()
    with _debug_lock:
        start = _debug_start_times.get(oid)
        if start:
            elapsed = now - start
            print(f"[⏱ DEBUG] oid={oid} event={event_name} arrived after {elapsed:.2f}s")
        else:
            print(f"[⏱ DEBUG] oid={oid} event={event_name} arrived but no start time")
        _debug_arrival_times.setdefault(oid, []).append((event_name, now))


def register_retry_failure(oid: str, account: str, game: str):
    """記錄 retry 最多仍失敗的 oid 對應資訊"""
    with _debug_lock:
        _retry_failures.append({
            "oid": oid,
            "account": account,
            "game": game
        })


def print_task_timing_summary():
    """印出所有任務的 callback 到達時序摘要與平均 join_room 時間"""
    with _debug_lock:
        print("\n====== WS Task Timing Summary ======")
        total_time = 0
        count = 0
        for oid in sorted(_debug_start_times):
            start = _debug_start_times[oid]
            arrivals = _debug_arrival_times.get(oid, [])
            for event, ts in arrivals:
                elapsed = ts - start
                print(f"oid={oid} event={event} +{elapsed:.2f}s")
                if event == "join_room":
                    total_time += elapsed
                    count += 1
        print("===================================")
        if count:
            avg = total_time / count
            print(f"📊 join_room 平均處理時間：{avg:.2f} 秒 (樣本數: {count})\n")
        else:
            print("⚠️ 無 join_room 封包樣本可計算平均時間\n")


def print_retry_failure_summary():
    """統計並列出所有 retry 最終仍失敗的任務資訊"""
    with _debug_lock:
        if not _retry_failures:
            print("✅ 無 retry 失敗記錄\n")
            return

        print("\n====== Retry Failure Summary ======")
        for item in _retry_failures:
            print(f"❌ oid={item['oid']} account={item['account']} game={item['game']}")
        print(f"📌 共 {len(_retry_failures)} 筆 retry 失敗\n")

def buffer_on_message(ws, message: str):
    """緩衝 WebSocket 收到的原始封包（供除錯用）"""
    if not hasattr(ws, "_message_buffer"):
        ws._message_buffer = []
    ws._message_buffer.append(message)
