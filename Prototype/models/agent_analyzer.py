import numpy as np

class AgentAnalyzer:
    def __init__(self, document):
        self.agent_id = document.get("agent_id")
        self.agent_name = document.get("agent_name")
        self.document = document
        self.text = self._extract_text(document)

    def _extract_text(self, node):
        """
        Recursively extract and flatten all string data from a nested dictionary or list.
        """
        parts = []

        if isinstance(node, dict):
            for value in node.values():
                parts.append(self._extract_text(value))
        elif isinstance(node, list):
            for item in node:
                parts.append(self._extract_text(item))
        elif isinstance(node, (str, int, float)):
            parts.append(str(node))
        # Ignore None, bool, other types

        return " ".join(filter(None, parts))

    def get_text(self):
        return self.text.lower() #returns all lower case for normalization