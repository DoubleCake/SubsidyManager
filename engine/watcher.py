# engine/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class RuleFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith((".json")):
            from engine.rule_loader import RuleLoader
            RuleLoader.reload()
            print("规则已热更新")

def start_watch(cfg_dir="config"):
    obs = Observer()
    obs.schedule(RuleFileHandler(), cfg_dir, recursive=False)
    threading.Thread(target=obs.start, daemon=True).start()