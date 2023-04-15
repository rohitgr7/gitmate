import configparser
import os
import subprocess
from getpass import getpass

import typer
from halo import Halo
from rich.console import Console

from gitmate.models import predict, predict_commit_message, predict_pr_details
from gitmate.utils import check_gh_cli_installation, check_message_with_user, get_creds

console = Console()

MODEL_OPTIONS = {
    "1": {"name": "GPT3", "openai_model": "davinci"},
    "2": {"name": "GPT3.5", "openai_model": "gpt-3.5-turbo"},
    # '3': {'name': 'GPT4', 'openai_model': 'gpt-4'},
}
app = typer.Typer()


@app.command()
def connect():
    """Registers the Open API Key."""
    openai_key = getpass(prompt="Open AI Key: ")
    input_message = "Pick an option:\n"

    for ix in MODEL_OPTIONS:
        input_message += f'{ix}) {MODEL_OPTIONS[ix]["name"]} ({MODEL_OPTIONS[ix]["openai_model"]})\n'

    input_message += "Your choice: "

    user_input = ""
    while user_input.lower() not in MODEL_OPTIONS:
        user_input = input(input_message)

    model_name = MODEL_OPTIONS[str(user_input)]["name"]

    config = configparser.ConfigParser()
    config["DEFAULT"] = {"openai_key": openai_key, "model_name": model_name}
    config_file = os.path.expanduser("~/.gitmate_creds")
    with open(config_file, "w") as f:
        config.write(f)

    verify()


@app.command()
def verify():
    """Used to verify OpenAI API Key and Model name."""
    creds = get_creds(MODEL_OPTIONS)
    if isinstance(creds, dict):
        console.print(creds["error"], style="bold red")
        return

    with Halo(text="Verifying", spinner="dots"):
        openai_key, model_name = creds
        response = predict("Who are you?", 5, openai_key, model_name)

    if "error" in response:
        console.print(response["error"]["message"], style="bold red")
    else:
        console.print("OpenAI Key and Model verified!", style="bold green")


@app.command()
def commit():
    """Create a commit and auto-generates a commit message."""
    creds = get_creds(MODEL_OPTIONS)
    if isinstance(creds, dict):
        console.print(creds["error"], style="bold red")
        return

    openai_key, model_name = creds
    diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    diff = diff.stdout[:4097]

    if not diff:
        console.print(
            "There are no changes. Please make changes or add those changes using `git add`.",
            style="bold yellow",
        )
        return

    commit_message = predict_commit_message(diff, openai_key, model_name)
    commit_message = check_message_with_user(commit_message, "commit message")
    subprocess.run(["git", "commit", "-m", commit_message])


@app.command()
def create_pr():
    """Create a PR with title and description."""
    cli_installed = check_gh_cli_installation()

    if not cli_installed:
        return

    creds = get_creds(MODEL_OPTIONS)
    if isinstance(creds, dict):
        console.print(creds["error"], style="bold red")
        return

    openai_key, model_name = creds
    commit_messages = subprocess.run(
        ["git", "log", "main..", "--pretty=format:%s", "--reverse"], capture_output=True, text=True
    )
    commit_messages = commit_messages.stdout

    if not commit_messages:
        console.print(
            "No commit messages found. Please add commits using `gitmate commit`.",
            style="bold yellow",
        )
        return

    title, description = predict_pr_details(commit_messages, openai_key, model_name)

    title = check_message_with_user(title, "PR title")
    description = check_message_with_user(description, "PR description")
    subprocess.run(["gh", "pr", "create", "-t", title, "-b", description])
