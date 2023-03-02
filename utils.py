from dataclasses import dataclass
import logging
import os

import openai


def new_logger(name: str) -> logging.Logger:
    log = logging.getLogger("my_logger")
    log.setLevel(logging.INFO)
    # current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    return log


def get_params_from_env():
    apikey = os.environ.get("OPENAI_API_KEY")
    params = {
        "apikey": apikey,
    }
    return params


@dataclass
class RequestParams:
    prompt: str
    n: int
    max_tokens: int
    temperature: float


def request(params: RequestParams):
    # response = openai.Completion.create(
    #     # model="text-davinci-003",
    #     model="gpt-3.5-turbo",  # when openai supports it ...
    #     prompt=params.prompt,
    #     temperature=params.temperature,
    #     max_tokens=params.max_tokens,
    #     n=params.n,
    # )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                # {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": params.prompt},
            ],
            n=params.n,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
        )
    except TimeoutError as e:
        print("timeout")

    results = []
    # print(response)
    for c in response["choices"]:
        text = c["message"]["content"]
        results.append(text)
    return results
