#!/usr/bin/env python

import os
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="gpt-4o",
)

print(chat_completion.choices[0].message.content)

encoding = tiktoken.get_encoding_for_model("gpt-4o")
tokens = encoding.encode("Hello, world!")
encoding.decode_single_token_bytes(token)

