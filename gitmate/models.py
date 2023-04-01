import requests
from halo import Halo
from rich.console import Console

console = Console()


def predict_gpt35(prompt, max_tokens, openai_key):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }
    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
    response = response.json()
    if "error" in response:
        return response

    return response["choices"][0]["message"]["content"]


def predict_gpt3(prompt, max_tokens, openai_key):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {openai_key}",
    }
    json_data = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=json_data)
    response = response.json()
    if "error" in response:
        return response

    return response["choices"][0]["text"].strip()


def predict(prompt, max_tokens, openai_key, model_name):
    if model_name == "GPT3.5":
        return predict_gpt35(prompt, max_tokens, openai_key)
    if model_name == "GPT3":
        return predict_gpt3(prompt, max_tokens, openai_key)


def predict_commit_message(diff, openai_key, model_name):
    with Halo(text="Generating Commit Message", spinner="dots"):
        prompt = f"""
        Craft a short and insightful Git commit message of upto 15 words that describes the changes in
        the following diff without any unnecessary context: {diff}
        """
        response = predict(prompt, 50, openai_key, model_name)

    if "error" in response:
        console.print(response["error"]["message"], style="bold red")
    else:
        return response.replace("\n", "")


def predict_pr_details(commit_messages, openai_key, model_name):
    with Halo(text="Generating PR details", spinner="dots"):
        prompt = f"""
        Craft a consice short title and insightful description for a GitHub PR that describes the changes in the
        following based on following commit messages without any unnecessary context: {commit_messages}
        """
        response = predict(prompt, 200, openai_key, model_name)

    if "error" in response:
        console.print(response["error"]["message"], style="bold red")
    else:
        title, description = response.replace("\n", "").split("Description:")
        title = title[7:]
        return title, description
