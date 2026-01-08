class ServiceAlreadyDefinedError(Exception):
    """
    Error thrown when a service was already defined, but the caller expected it to not exist.
    """

    def __init__(self, *, name: str):
        formatted_message = f"Service already defined: {name}"

        super().__init__(formatted_message)
