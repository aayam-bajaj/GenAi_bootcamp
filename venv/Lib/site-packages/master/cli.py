#!/usr/bin/env python3
"""
NAME
    master -- Deterministic password generator.

USAGE
    master                      With no arguments, prompt for service NAME
    master NAME                 Gets the password for service NAME
    master -l, --list           Lists all stored services
    master -r, --remove NAME    Removes service NAME from the stored list
    master -v, --version        Shows the version
    master -h, --help           Shows this help
"""
import os
import sys
import getpass
import logging
import hashlib
import base64
import re
import subprocess
import shutil # import which

VERSION          = "0.2.6"
USER_HOME        = os.path.expanduser("~")
MASTER_LIST      = f"{USER_HOME}/.config/master/list.txt"
MASTER_LIST      = os.environ.get("MASTER_LIST", MASTER_LIST)
MASTER_DEBUG     = bool(os.environ.get("MASTER_DEBUG"))
MASTER_USERNAME  = os.environ.get("MASTER_USERNAME", "")
MASTER_PASSWORD  = os.environ.get("MASTER_PASSWORD", "")
MASTER_SEPARATOR = os.environ.get("MASTER_SEPARATOR", "-")
MASTER_LENGTH    = int(os.environ.get("MASTER_LENGTH", "6"))
MASTER_CHUNKS    = int(os.environ.get("MASTER_CHUNKS", "6"))




class Clipboard:

    @classmethod
    def copy(cls, text: str):
        if cls.__exists("pbcopy"):
            return cls.__pbcopy(text)

        if cls.__exists("xsel"):
            return cls.__xsel(text)

        return cls.__xclip(text)


    @classmethod
    def __exists(cls, file):
        return bool(shutil.which(file))


    @classmethod
    def __pbcopy(cls, text):
        proc = subprocess.Popen(
            ['pbcopy', 'w'],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        proc.communicate(input=text.encode("utf-8"))


    @classmethod
    def __xclip(cls, text):
        proc = subprocess.Popen(
            ['xclip', '-selection', 'c'],
            stdin=subprocess.PIPE,
            close_fds=True
        )
        proc.communicate(input=text.encode("utf-8"))


    @classmethod
    def __xsel(cls, text):
        proc = subprocess.Popen(
            ['xsel', '-b', '-i'],
            stdin=subprocess.PIPE,
            close_fds=True
        )
        proc.communicate(input=text.encode("utf-8"))


class Master:

    def __init__(self, path: str):
        self.path = path
        self.separator = "-"
        self.length = 6
        self.chunks = 6

        self.services = None
        self.username = None
        self.password = None


    def load(self) -> int:
        if not self.services is None:
            return len(self.services)

        self.services = set()
        if not os.path.isfile(self.path):
            # Logger.warn(f"File {self.path} doesn't exit.")
            return 0

        with open(self.path, "r") as f:
            for line in f.readlines():
                self.services.add(line.strip())

        Logger.debug(f"Loaded file {self.path}")
        return len(self.services)


    def add(self, service: str):
        self.load()
        return self.services.add(service)


    def remove(self, service: str):
        self.load()
        return self.services.discard(service)


    def save(self) -> bool:
        dirName = os.path.dirname(self.path)
        os.makedirs(dirName, exist_ok=True)

        with open(self.path, "w") as f:
            f.write("\n".join(self.services))
        Logger.debug(f"Wrote file {self.path}")


    def generate(self, service: str, counter: int = 0) -> str:
        source = f"{self.username}:{self.password}:{service}:{counter}"
        Logger.debug(f"Source:   {source}")
        hashed = hashlib.sha256()
        hashed.update(bytes(source, "utf8"))
        digest = hashed.digest()
        Logger.debug(f"Digest:   {digest} ({type(digest)} {len(digest)})")
        Logger.debug(f"Hex:      {digest.hex()}")
        encoded = base64.b64encode(digest).decode()
        Logger.debug(f"Encoded:  {encoded} ({type(encoded)})")

        cleaned = re.sub(r"[^0-9A-Za-z]", "", encoded)
        parts = []
        for i in range(self.chunks):
            start = i * self.length
            stop = (i + 1) * self.length
            parts.append(cleaned[start:stop])
        Logger.debug(f"Parts: {parts}")
        password = self.separator.join(parts)
        Logger.debug(f"Password: {password}")
        return password


import os
import sys
import logging


class Logger:

    envDebug = bool(os.environ.get("MASTER_DEBUG"))
    # print(f"--> envDebug: {envDebug}")

    @classmethod
    def trace(cls, *dargs, **dkwargs):
        cls.debug(f"Decor args: {dargs}")
        cls.debug(f"Decor kwargs: {dkwargs}")
        def inner(func):
            cls.debug(f"Running func: {func}")
            def wrap(*args,**kwargs):
                cls.debug(f"Function args: {args}")
                cls.debug(f"Function kwargs: {kwargs}")
                result = func(*args, **kwargs)
                cls.debug(f"Function result: {result}")

                return result
            return wrap
        return inner


    @classmethod
    def debug(cls, text: str):
        if not cls.envDebug: return
        print(f"\033[38;5;242m==> {text}\033[0m", file=sys.stderr)


    @classmethod
    def warn(cls, text: str):
        print(f"\033[33;1m==> {text}\033[0m", file=sys.stderr)


class Cli:

    def __init__(self):
        self.master = Master(MASTER_LIST)
        self.master.chunks = MASTER_CHUNKS
        self.master.length = MASTER_LENGTH
        self.master.separator = MASTER_SEPARATOR


    def ask(self) -> (str, str):
        if len(MASTER_USERNAME) > 0:
            username = MASTER_USERNAME
        else:
            prompt = "Enter your master username: "
            username = getpass.getpass(prompt=prompt)

        # if len(self.PASSWORD) > 0:
        if len(MASTER_PASSWORD) > 0:
            password = MASTER_PASSWORD
        else:
            prompt = "Enter your master password: "
            password = getpass.getpass(prompt=prompt)

        return (username, password)


    @Logger.trace()
    def get(self, service: str, counter: int = 0):
        """Gets the deterministic password for SERVICE."""
        username, password = self.ask()

        self.master.add(service)
        self.master.save()

        self.master.username = username
        self.master.password = password
        random = self.master.generate(service, counter)
        Clipboard.copy(random)
        print(f"Password for \033[32;1m{service}\033[0m was copied.")


    @Logger.trace()
    def start(self):
        """Asks input for a new SERVICE."""
        username, password = self.ask()
        service = input("Enter your service name: ")

        self.master.add(service)
        self.master.save()

        self.master.username = username
        self.master.password = password
        random = self.master.generate(service)
        print(random)

    @Logger.trace()
    def ls(self):
        """Lists all stored services."""
        self.master.load()
        for service in self.master.services:
            print(service)


    @Logger.trace()
    def version(self):
        """Prints the version."""
        print(f"v{VERSION}")


    @Logger.trace()
    def remove(self, service: str):
        """Removes SERVICE from the stored list."""
        self.master.remove(service)
        self.master.save()


def main():
    cli = Cli()
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    args = sys.argv[1:]

    if cmd is None:
        cli.start()
        return

    if cmd in ["-h", "--help", "help"]:
        print(__doc__)
        return

    if cmd in ["-v", "--version", "version"]:
        print(f"v{VERSION}")
        return

    if cmd in ["-l","-ls", "--ls", "--list"]:
        cli.ls()
        return

    if cmd in ["-r", "--rm", "--remove", "-d", "--delete"]:
        name = args[1]
        if name is None:
            print("Usage: master --rm NAME")
            return 1

        return cli.remove(args[1])

    cli.get(cmd)


if __name__ == "__main__":
    exit(main())
