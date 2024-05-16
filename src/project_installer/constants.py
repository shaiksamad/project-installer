

RECOGNISED_CONST = (
    # recognised constants
    "DRIVE", # (optional) Drive letter. (C)
    "PROGRAMFILES", # (optional) Folder name contains Program Files. ("Python Programs", "Organization Name"..)
    "PATH", # (optional) Path inside the program files folder. ("Product Name")
    "SOURCE", # (optional) source folder, from which content is fetched and installed in choosen PATH
    "FILES",  # (optional) list of files from the SOURCE folder, to be installed 
    "IGNORE", # (optional) list of file to be ignored from installing.
)


class DEFAULTS:
    DRIVE: str = "C"
    PROGRAMFILES: str = "Python Programs"
    PATH: str = ""
    SOURCE: str = ""
    FILES: list = []
    IGNORE: list = []

