class ResponseData:
    def __init__(self, status, elapsed, headers):
        self.status = status
        self.elapsed = elapsed
        self.headers = headers