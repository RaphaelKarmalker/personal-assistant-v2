import time

class ContextManager:
    def __init__(self):
        self.context = []
        self.last_update_time = None  # Zeitstempel des letzten Updates

    def update_context(self, role, message):
        current_time = time.time()
        self.last_update_time = current_time

        self.context.append({"role": role, "content": message})
        if len(self.context) > 10:
            self.context.pop(0)

    def get_context_summary(self):
        current_time = time.time()

        # Wenn das letzte Update mehr als 2 Minuten zurückliegt, lösche den Kontext
        if self.last_update_time is None or (current_time - self.last_update_time) > 120:
            self.context = []
            return ""
        
        return "\n".join([f"{entry['role']}: {entry['content']}" for entry in self.context])
