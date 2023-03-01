from dataclasses import dataclass
import hashlib
import json
import os
import streamlit as st
import openai

# import numpy as np
# import pandas as pd


@dataclass
class Params:
    prompt: str
    n: int
    max_tokens: int
    temperature: float


def request(params: Params):
    response = openai.Completion.create(
        model="text-davinci-003",
        # model="gpt-3.5-turbo", # when openai supports it ...
        prompt=params.prompt,
        temperature=params.temperature,
        max_tokens=params.max_tokens,
        n=params.n,
    )
    return response


def get_params_from_env():
    apikey = os.environ.get("OPENAI_API_KEY")
    params = {
        "apikey": apikey,
    }
    return params


def update_prompt():
    params = Params(
        prompt=st.session_state.prompt,
        n=st.session_state.n,
        max_tokens=st.session_state.max_tokens,
        temperature=st.session_state.temperature,
    )
    with st.spinner("Wait for it..."):
        data = request(params)
        # st.write(hash_dict(data))
        for i, t in enumerate(data.choices):
            st.write(t.text)
            if i < len(data.choices) - 1:
                st.write(
                    "–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––"
                )


def hash_dict(d):
    data = json.dumps(d, sort_keys=True)
    hh = hashlib.sha256(data.encode()).hexdigest()
    return hh


if __name__ == "__main__":
    params = get_params_from_env()
    openai.api_key = params["apikey"]

    st.set_page_config(layout="wide")

    st.text_area("Prompt", key="prompt", on_change=update_prompt)
    st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.1,
        key="temperature",
    )
    st.slider(
        "Max Tokens", min_value=1, max_value=1000, value=100, step=1, key="max_tokens"
    )
    st.slider("N", min_value=1, max_value=10, value=5, step=1, key="n")
    # st.text_area("Prompt", key="prompt", on_change=update_prompt)
    # st.button("Update Prompt", on_click=update_prompt)
