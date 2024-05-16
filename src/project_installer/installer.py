import requests
import os
from pathlib import Path
import tarfile
import logging

from project_installer.errors import *
from project_installer.constants import DEFAULTS

logging.basicConfig(filename="installer.log", 
                    format=logging.BASIC_FORMAT,
                    level=logging.INFO)


class Installer:
    def __init__(self, doc: str, globals: dict) -> None:
        self.source, self.repo, release = doc.strip().split("\n")
        
        # self.repo_url
        self.__get_repo_url()
        logging.info(f"REPO: {self.repo_url}")

        # self.release_url
        # self.release_name
        # self.archive_url
        self.__get_release(release)
        logging.info(f"RELEASE NAME: {self.release_name}")

        self.is_latest = release == 'latest'
        logging.info(f"LATEST: {self.is_latest}")

        self.SOURCE = globals.get("SOURCE", DEFAULTS.SOURCE)
        self.FILES = globals.get("FILES", DEFAULTS.FILES)
        self.IGNORE = globals.get("IGNORE", DEFAULTS.IGNORE)

        
        # set self.INSTALL_PATH
        self.__get_install_path(globals)
        logging.info(f"INSTALL PATH: {self.INSTALL_PATH}")


    def __get_install_path(self, globals: dict):
        DRIVE = globals.get("DRIVE", DEFAULTS.DRIVE)
        PROGRAMFILES = globals.get("PROGRAMFILES", DEFAULTS.PROGRAMFILES)
        PATH = globals.get("PATH", self.repo)
        self.INSTALL_PATH = Path(DRIVE+":/" , PROGRAMFILES, PATH)


    def __download_archive(self) -> Path:
        temp: Path = Path(os.environ['temp']) / self.repo / f"{self.release_name}.tar.gz"
        resp = requests.get(self.archive_url)
        if resp.ok:
            os.makedirs(temp.parent, exist_ok=True)
            temp.write_bytes(resp.content)
            return temp
        else:
            raise ArchiveNotFound(self.archive_url, f"Archive Not Found ({resp.status_code})")
    

    def __ignore_files(self, selected_files):
        # TODO: Add support for wildcard/regex.
        return [file for file in selected_files if file not in self.IGNORE]      


    def install(self):
        if os.environ.get('os') == "Windows_NT":
            # ensuring install path is present.
            os.makedirs(self.INSTALL_PATH, exist_ok=True)
            
            # downloading project from github to temp folder
            archive = self.__download_archive()
            
            with tarfile.open(archive, 'r:gz') as tar:
                # list of files in the archive
                names = tar.getnames()

                # root folder of archive + source folder of installation
                root = Path(names[0], self.SOURCE).as_posix()
                root_len = len(root)
                
                # files to be installed from archive
                selected_files: list[str] = []

                # selecting user defined files from the archive
                for file in self.FILES:
                    file = f"{root}/{file}"
                    if file in names:
                        selected_files.append(file[root_len:].strip("/"))

                # selecting all the files from the archive, if user not defined files.
                if not self.FILES:
                    selected_files = [file[root_len:].strip("/") for file in names if file.startswith(root)]
                
                # remove ignored files from selected files
                selected_files = self.__ignore_files(selected_files)

                for file in selected_files:

                    file_path = self.INSTALL_PATH / file

                    tar_file = tar.getmember(Path(root, file).as_posix())
                    
                    if tar_file.isdir():
                        logging.info(f"MKDIR: {file_path}")
                        os.makedirs(file_path, exist_ok=True)
                        continue

                    if tar_file.isfile():
                        logging.info(f"CREATING: {file_path}")
                        with tar.extractfile(tar_file) as file:
                            file_path.write_bytes(file.read())


    def __get_repo_url(self):
        if self.source == "github":
            url = f"https://github.com/{self.repo}"
            resp = requests.head(url)
            if resp.status_code == 200:
                self.repo_url = url
            else:
                raise RepositoryNotFound(url)

    
    def __get_release(self, release="latest"):
        if self.source == "github":
            release_url = f"{self.repo_url}/releases/{release}"
            resp = requests.head(release_url)

            # if OK (200s) or REDIRECTED (300s), release is present
            if 200 <= resp.status_code < 400:
                self.release_url = release_url if resp.status_code < 300 else resp.headers.get("location")
            else:
                raise ReleaseNotFound(release)
            
            # version name/tag name
            self.release_name = self.release_url.split("/")[-1]
            
            if self.release_name == "releases":
                raise ReleaseNotFound("", "No Releases Present")

            self.archive_url = f"{self.repo_url}/archive/refs/tags/{self.release_name}.tar.gz"

