### app/context_manager.py
class ContextManager:
    def __init__(self):
        self.context = []

    def update_context(self, role, message):
        self.context.append({"role": role, "content": message})
        if len(self.context) > 10:
            self.context.pop(0)

    def get_context_summary(self):
        return "\n".join([f"{entry['role']}: {entry['content']}" for entry in self.context])