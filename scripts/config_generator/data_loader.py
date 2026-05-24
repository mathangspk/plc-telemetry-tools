import json

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metrics = []
        self.signals = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metrics = data.get("metrics", [])
                self.signals = data.get("signals", [])
        except FileNotFoundError:
            print(f"Warning: File {self.file_path} not found. Starting with empty data.")
        except json.JSONDecodeError:
            print(f"Error: File {self.file_path} is not valid JSON.")

    def get_metrics(self):
        return self.metrics

    def get_signals_by_group(self, group_name):
        """
        Returns a list of signal dictionaries where the signal name contains the group_name.
        Case insensitive.
        """
        group_name_lower = group_name.lower()
        return [s for s in self.signals if group_name_lower in s.get("name", "").lower()]
