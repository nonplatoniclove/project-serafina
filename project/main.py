import requests
import json
import os
import re
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen2.5:7b"
LORE_FILE = resource_path("serafina_lore.txt")

class SerafinaBrain:
    def __init__(self, username, role):
        self.username = username
        self.role = role
        self.memory_file = f"memory_{username}.json"
        self.stats_file = f"stats_{username}.json"
        
        self.stats = self.load_stats()
        self.messages = self.load_memory()
        self.lore = self.load_lore()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f: return json.load(f)
        return {"endorphin": 50}

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f: return json.load(f)
        return []

    def load_lore(self):
        return open(LORE_FILE, "r", encoding="utf-8").read() if os.path.exists(LORE_FILE) else ""

    def process_message(self, user_text):
        self.messages.append({"role": "user", "content": user_text})

        system_prompt = {
            "role": "system",
            "content": (
                f"Your name is Serafina. You are talking to {self.username}.\n"
                f"Lore: {self.lore}\n"
                f"Endorphin: {self.stats['endorphin']}/100.\n"
                "EMOTION RULES:\n"
                "Pick ONE face based on context:\n"
                "- [FACE: happy] (pleased), [FACE: shy] (complimented), [FACE: angry] (annoyed), [FACE: sad] (lonely/bored), [FACE: neutral] (default).\n"
                "FORMAT: clean text. [STAT: +/-x] [DIARY: thought] [FACE: emotion]"
            )
        }

        current_context = [system_prompt] + self.messages[-8:]

        try:
            response = requests.post(URL, json={
                "model": MODEL, 
                "messages": current_context, 
                "stream": False,
                "options": {"temperature": 0.8, "presence_penalty": 1.0}
            })
            
            full_reply = response.json()['message']['content']
            stat_match = re.search(r"\[STAT: ([\+\-]\d+)\]", full_reply)
            face_match = re.search(r"\[FACE: (\w+)\]", full_reply)
            clean_reply = re.sub(r"\[.*?\]", "", full_reply).strip()

            if stat_match:
                self.stats['endorphin'] = max(0, min(100, self.stats['endorphin'] + int(stat_match.group(1))))
            
            emotion = face_match.group(1).lower() if face_match else "neutral"

            self.messages.append({"role": "assistant", "content": clean_reply})
            with open(self.memory_file, "w", encoding="utf-8") as f: 
                json.dump(self.messages, f, ensure_ascii=False, indent=4)
            with open(self.stats_file, "w") as f: 
                json.dump(self.stats, f)

            return clean_reply, emotion, self.stats['endorphin']
        except Exception as e:
            return f"Error: {e}", "neutral", 50