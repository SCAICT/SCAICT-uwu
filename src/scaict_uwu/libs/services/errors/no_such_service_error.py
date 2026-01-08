class NoSuchServiceError(Exception):
    """
    Error thrown when the requested service is not known.
    """

    def __init__(self, *, name: str):
        formatted_message = f"No such service: {name}"

        super().__init__(formatted_message)
