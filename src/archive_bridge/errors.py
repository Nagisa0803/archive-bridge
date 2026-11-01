class BridgeError(Exception):
    """Stable code and credential-free explanation, safe for the local UI."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message
