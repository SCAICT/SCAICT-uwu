class CannotReplaceActiveServiceError(Exception):
    """
    Error thrown when trying to replace an already active service.
    """

    def __init__(self, *, name: str):
        formatted_message = f"Cannot replace an active service: {name}"

        super().__init__(formatted_message)
