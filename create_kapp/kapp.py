# region Create-kApp
import io
import os
import sys
import time
import zipfile
from typing import Callable, Literal

import requests

Completed = Literal["confirm", "input"]


# Kprompts will be released as its own thing at a later date
class KPrompts:
    """
    Provides simple input and confirmation prompts with custom colors.

    This is a simplified version of the 'prompts' NPM package for Python.
    """

    def __init__(self) -> None:
        """Initializes the prompt class and fixes color formatting for terminals."""
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
        """Enables colored output for Windows terminals if supported."""
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
        """Outputs formatted text with custom colors."""
        sys.stdout.write(f"{self.colors['white']}{text} ")
        sys.stdout.flush()

    def final_print(
        self, question: str, answer: str, password: bool | None = False
    ) -> None:
        """Prints the final message with the user's input, imitating the style of the NPM prompts package."""
        sys.stdout.write(
            f"{self.colors['green']}√{self.colors['white']} {question} {self.colors['grey']}»{self.colors['white']} {answer}\n"
        )
        sys.stdout.flush()

    def better_input(self, text: str) -> str:
        """Displays a formatted input prompt and captures the user's input."""
        self.print(f"{self.colors['cyan']}? {self.colors['white']}{text}")
        user_input = input(f" {self.colors['grey']}»{self.colors['white']} ")
        sys.stdout.write("\033[F\033[K")  # Clears previous input
        return user_input

    def prompt(
        self,
        option: Completed,
        message: str,
        validate: Callable[[str], bool] | None = None,
        keep: bool | None = True,
    ) -> str:
        """
        Displays an input or confirmation prompt based on the provided option.

        Args:
            option (Completed): The prompt type ('input' or 'confirm').
            message (str): The prompt message.
            validate (Callable[[str], bool], optional): A validation function for user input.
            keep (bool, optional): If True, prints the user's answer after validation.

        Returns:
            str: The user's validated input or confirmation response.
        """
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

        else:
            raise ValueError(f"Invalid option: {option}")


class CreateKapp:
    """
    A simple CLI tool for downloading and setting up project templates from GitHub.

    Args:
        user (str): GitHub username.
        branch (str): Branch of the repository to download.
    """

    def __init__(self, user: str, branch: str) -> None:
        """Initializes the CreateKapp class with GitHub user and branch."""
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

    def set_path(self, path: str) -> str:
        """
        Sets the path where the project will be created.

        Args:
            path (str): The folder path where the project will be set up.

        Returns:
            str: The absolute path to the project folder.
        """
        global found_path
        if path == ".":
            found_path = os.getcwd()
            return found_path
        if not os.path.isdir(path):
            os.mkdir(path)
        found_path = os.path.abspath(path)
        return found_path

    def download(self, url: str) -> None:
        """
        Downloads and extracts a project template from GitHub.

        Args:
            url (str): The URL of the GitHub repository template.
        """
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
        """Runs the CreateKapp CLI tool."""
        folder = Prompt.prompt(
            "input",
            "Setup the project in (specify folder)...?",
            validate=lambda value: len(value) > 0,
        )
        self.set_path(folder)

        scaffold = Prompt.prompt("input", "What scaffold do you want to start with?")
        self.download(scaffold if scaffold in self.urls else self.urls[0])
        self.answer("Successfully set up project :D")


def main():
    """Entry point for the CreateKapp CLI tool."""
    try:
        app = CreateKapp(user="kars1996", branch="master")
        app.run()
    except KeyboardInterrupt:
        app.angry("Shutting Down")


if __name__ == "__main__":
    main()
