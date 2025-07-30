from pathlib import Path

def report_progress(percent: int, step: str = ""):
    print(f"[PROGRESS] {percent} {step}", flush=True)