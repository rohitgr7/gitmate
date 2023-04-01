import configparser
import os
import subprocess

from rich.console import Console

console = Console()


def check_gh_cli_installation():
    try:
        subprocess.run(["gh", "--version"], capture_output=True)
        return True
    except FileNotFoundError:
        console.print(
            "GitMate requires GitHub CLI is to be installed on this system"
            + " to use `gitmate push`. Please visit https://cli.github.com/ to install it.",
            style="bold red",
        )
        return False


def check_message_with_user(message, message_type):
    user_input = ""
    while user_input.lower() not in ["y", "n"]:
        console.print(f"[bold green]{message_type.title()}:[/bold green] {message}")
        user_input = input("Do you want to proceed? ([Y]/N): ")
        user_input = user_input.strip() or "y"

    if user_input.lower() == "n":
        message = input(f"Please enter a {message_type}: ")

    return message


def get_creds(model_options):
    config = configparser.ConfigParser()
    config_file = os.path.expanduser("~/.gitmate_creds")

    config.read(config_file)

    if not ("openai_key" in config["DEFAULT"] or "model_name" in config["DEFAULT"]):
        return {"error": "GitMate credentials are not set, please use `gitmate connect`."}

    openai_key = config["DEFAULT"]["openai_key"]
    model_name = config["DEFAULT"]["model_name"]

    model_names = [x["name"] for x in model_options.values()]
    if model_name not in model_names:
        return {"error": "GitMate credentials are not set, please use `gitmate connect`."}

    return openai_key, model_name
