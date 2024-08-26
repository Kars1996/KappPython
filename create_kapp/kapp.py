# region Create-kApp
# Python port of my npm package (old ui)

from typing import Literal, Callable
import sys
import os
import requests
import zipfile
import io
import time

Completed = Literal["confirm", "input"]


#  ! This is an old verion of kprompts, doesn't hve all the new features. Don't use this
class KPrompts:
    """Minified verson of my package to recreate "prompts" on Javascript"""

    def __init__(self) -> None:
        self.fix_colors()
        self.colors = {
            "cyan": "\033[0;96m",
            "green": "\033[0;92m",
            "red": "\033[0;91m",
            "white": "\033[0;97m",
            "grey": "\033[1;30m",
        }

    @staticmethod
    def fix_colors() -> None:
        """Function to fix colors in windows"""
        if not sys.stdout.isatty():
            for _ in dir():
                if isinstance(_, str) and _[0] != "_":
                    locals()[_] = ""
        else:
            if __import__("platform").system() == "Windows":
                kernel32 = __import__("ctypes").windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                del kernel32

    def print(self, text: str) -> None:
        """Custom Print cause normal print is annoying (Could honestly be achived with end="" tho)"""
        sys.stdout.write(f"{self.colors['white']}{text} ")
        sys.stdout.flush()

    def final_print(
        self, question: str, answer: str, password: bool | None = False
    ) -> None:
        """Final message to keep it similar to the NPM package"""
        sys.stdout.write(
            f"{self.colors['green']}√{self.colors['white']} {question} {self.colors['grey']}»{self.colors['white']} {answer}\n"
        )
        sys.stdout.flush()

    def better_input(
        self,
        text: str,
    ) -> str:
        self.print(f"{self.colors['cyan']}? {self.colors['white']}{text}")
        user_input = input(f" {self.colors['grey']}»{self.colors['white']} ")
        sys.stdout.write("\033[F\033[K")
        return user_input

    def prompt(
        self,
        option: Completed,
        message: str,
        validate: Callable[[str], bool] | None = None,
        keep: bool | None = True,
    ) -> str:
        """Main Code"""
        if option == "input":
            try:
                while True:
                    user_input = self.better_input(message)
                    if validate:
                        if validate(user_input):
                            if keep:
                                self.final_print(message, user_input)
                            return user_input
                        else:
                            self.print(
                                f"{self.colors['red']}× Invalid input. Try again.{self.colors['white']}"
                            )
                    else:
                        if keep:
                            self.final_print(message, user_input)
                        return user_input
            except KeyboardInterrupt:
                self.print(
                    f"\r{self.colors['red']}× {self.colors['white']}{message}{self.colors['grey']}» ...{self.colors['white']}\n"
                )

        elif option == "confirm":
            """Simple Confirmaton Script"""
            try:
                while True:
                    user_input = self.better_input(
                        f"{message} {self.colors['grey']}(y/n)"
                    ).lower()
                    if user_input in ["y", "n"]:
                        if keep:
                            self.final_print(message, user_input)
                        return user_input == "y"
                    else:
                        self.print(
                            f"{self.colors['red']}× Please answer with 'y' or 'n'.{self.colors['white']}"
                        )
            except KeyboardInterrupt:
                self.print(
                    f"\r{self.colors['red']}× {self.colors['white']}{message} {self.colors['grey']}(y/n) {self.colors['grey']}» ...{self.colors['white']}\n"
                )

        # ! Typesafety should make sure this doesn't happen but python is goofy
        else:
            raise ValueError(f"Invalid option: {option}")


class CreateKapp:
    def __init__(self, user: str, branch: str) -> None:
        """Config Options"""
        global Prompt
        self.user = user
        self.branch = branch
        self.urls = ["template", "apitemplate", "DJS14Template"]
        self.colors = {
            "cyan": "\033[0;96m",
            "green": "\033[0;92m",
            "red": "\033[0;91m",
            "white": "\033[0;97m",
        }
        Prompt = KPrompts()

    """These are just simple little funny tex formatting thingies"""
    def question(self, prompt: str) -> None:
        return print(f"{self.colors['cyan']}?{self.colors['white']} {prompt}", end="")

    def answer(self, prompt: str, recursive: bool | None = False) -> None:
        prefix = "\r" if recursive else ""
        print(f"{prefix}{self.colors['green']}√{self.colors['white']} {prompt}", end="")

    def angry(self, prompt: str, recursive: bool | None = False) -> None:
        prefix = "\r" if recursive else ""
        return print(
            f"{prefix}{self.colors['red']}×{self.colors['white']} {prompt}", end=""
        )

    def set_path(self, path: str) -> str:
        """Setsthe users path"""
        global found_path # Honestly this could just be returned instead of being global
        if path == ".":
            found_path = os.getcwd()
            return found_path
        if not os.path.isdir(path):
            os.mkdir(path)
        found_path = os.path.abspath(path)
        return found_path

    def download(self, url: str) -> None:
        """Download logic (much simpler on python ngl)"""
        try:
            download_url = f"https://github.com/{self.user}/{url}/archive/refs/heads/{self.branch}.zip"
            Prompt.print(
                f"{self.colors['cyan']}∂ Downloading template {url}...{self.colors['white']}"
            )

            response = requests.get(download_url)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(found_path)
                self.answer("Download and extraction complete!", True)
            else:
                self.angry(f"Failed to download: {response.status_code}", True)
        except Exception as e:
            self.angry(f"Error occurred: {str(e)}")
            time.sleep(2)

    def run(self) -> None:
        """Main CLI bit"""
        folder = Prompt.prompt(
            "input",
            "Setup the project in (specify folder)...?",
            validate=lambda value: len(value) > 0,
        )
        self.set_path(folder)

        scaffold = Prompt.prompt("input", "What scaffold do you want to start with?") # This will useoptoins once i finish it in kapp

        self.download(scaffold if scaffold in self.urls else self.urls[0])
        self.answer("Sucessfully setup project :D")


def main():
    try:
        app = CreateKapp(user="kars1996", branch="master")
        app.run()
    except KeyboardInterrupt:
        app.angry("Shutting Down")


if __name__ == "__main__":
    main()
