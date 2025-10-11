import json
from pathlib import Path
from datetime import datetime, timezone
class DeckStorage:
    def __init__(self,path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Deck file not found at {self.path}")
        self.cards = self.load()
    def load(self):
        try:
            with self.path.open("r", encoding = "utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid Json file {e}")
        required_keys = {"id", "front", "back", "ease", "interval", "repetitions", "due_at"}
        if not isinstance(data, list):
            raise ValueError("Deck must be a JSON array")
        seen_ids = set()
        for i, card in enumerate (data):
            if not isinstance(card, dict):
                raise ValueError(f"Card at number {i} must be an object")
            missing = required_keys - card.keys()
            if missing:
                raise ValueError(f"Card at number {i} is missing keys: {sorted(missing)}")
            if card["id"] in seen_ids:
                raise ValueError(f"Duplicate card id: {card['id']}") 
            seen_ids.add(card["id"])
            if not isinstance(card["id"],int):
                raise ValueError(f"Card {card['id']}: 'id' must be int") 
            if not isinstance(card["front"], str) or not card["front"].strip():
                raise ValueError(f"Card {card['id']}: 'front' must be a non-empty string")
            if not isinstance(card["back"], str) or not card["back"].strip():
                raise ValueError(f"Card {card['id']}: 'back' must be a non-empty string")
            if not isinstance(card["ease"], (int, float)) or card["ease"] < 1.3:
                raise ValueError(f"Card {card['id']}: 'ease' must be >= 1.3")
            if not isinstance(card["interval"], int) or card["interval"] < 0:
                raise ValueError(f"Card {card['id']}: 'interval' must be a non-negative int")
            if not isinstance(card["repetitions"], int) or card["repetitions"] < 0:
                raise ValueError(f"Card {card['id']}: 'repetitions' must be a non-negative int")
            if not isinstance(card["due_at"], str):
                raise ValueError(f"Card {card['id']}: 'due_at' must be ISO string")   
            try:
                _ = self.parse_iso(card["due_at"])
            except Exception:
                raise ValueError(f"Card {card['id']}: 'due_at' is not a valid ISO datetime: {card['due_at']}")

        return data
    @staticmethod
    def parse_iso(s):
        if not isinstance(s,str):
            raise TypeError(f"Expected string got {type(s).__name__}")
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    
    def get_due(self):
        now = datetime.now(timezone.utc)
        due_now = []
        for card in self.cards:
            due = self.parse_iso(card["due_at"])
            if due <= now:
                due_now.append(card)
        due_now.sort(key = lambda c: self.parse_iso(c["due_at"]))        
        return due_now 
    @staticmethod
    def to_iso(dt):
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
    def save(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Deck file not found at {self.path}")
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(self.cards, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.path)
