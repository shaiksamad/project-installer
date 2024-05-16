class Error(BaseException):
    """Custom Exceptions to raise Errors"""
    pass


class RepositoryNotFound(Error):
    def __init__(self, url, message="Repository Not Found") -> None:
        self.message = f"{message}: {url}"
        super().__init__(self.message)


class ReleaseNotFound(Error):
    def __init__(self, release_name, message="Release Not Found") -> None:
        self.message = f"{message}: {release_name}"
        super().__init__(self.message)


class ArchiveNotFound(Error):
    def __init__(self, url, message="Archive Not Found") -> None:
        self.message = f"{message}: {url}"
        super().__init__(self.message)


