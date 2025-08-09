import streamlit as st
import toml
import os
from streamlit_authenticator import Authenticate


def load_config(path: str = "config.toml"):
    if not os.path.exists(path):
        st.error("Missing config.toml for authentication.")
        st.stop()
    with open(path, "r") as f:
        return toml.load(f)


def get_authenticator():
    config = load_config()

    # Use positional arguments instead of keyword arguments
    authenticator = Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )
    return authenticator
