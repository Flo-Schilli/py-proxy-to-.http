class QueryDto:
    def __init__(self,
                 headers: dict[str, str] | None = None,
                 params: dict[str, str] | None = None,
                 payload: dict | None = None):

        self.headers: dict[str, str] | None = headers
        self.params: dict[str, str] | None = params
        self.payload: dict[str, str] | None = payload

