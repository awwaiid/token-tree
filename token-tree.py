#!/usr/bin/env python

from IPython import embed  # For debugging; put `embed()` anywhere
import os
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

class TokenTree:
    # Keep track of a global incrementing node id
    next_node_id = 0

    def __init__(self, token_id, token_bytes, log_prob):
        self.token_id = token_id
        self.token_bytes = token_bytes
        self.log_prob = log_prob
        self.children = {}

        # Assign the node id and increment the global counter
        self.node_id = TokenTree.next_node_id
        TokenTree.next_node_id += 1

    def merge_children(self, token_trees):
        for token_tree in token_trees:
            if token_tree.token_id in self.children.keys():
                self.children[token_tree.token_id].merge_children(token_tree.children.values())
            else:
                self.children[token_tree.token_id] = token_tree

    def __str__(self):
        return f"{self.token_id} -> [{self.children}]"

    def token_utf8_escaped(self):
        return self.token_bytes.decode("utf-8", "backslashreplace").replace('"', '\\"')

    def to_graphviz_node(self):
        output = f"n{self.node_id} [label=\"'{self.token_utf8_escaped()}'\\n[{self.token_id}] @ {round(self.log_prob, 2)}\"]\n"
        for child in self.children.values():
            output += f"n{self.node_id} -> n{child.node_id}\n"
            output += child.to_graphviz_node()
        return output

    def to_graphviz(self):
        # return f"digraph TokenTree {{\nrankdir=LR\n{self.to_graphviz_node()}\n}}"
        return f"""
              digraph G {{
                rankdir=LR;
                node [shape=rectangle];

                {self.to_graphviz_node()}

              }}
            """


if __name__ == "__main__":

    load_dotenv()

    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        # model="gpt-4o",
        model="gpt-3.5-turbo",
        n=20,
        max_tokens=10,
        logprobs=True,
        top_logprobs=10,
        messages=[
            {
                "role": "user",
                "content": "Tell me a short story about a kitten. Do not start with 'Once upon a time.'",
            }
        ],
    )


    # TODO: Create child notes from the top-logprobs also

    root = TokenTree(0, b"", 0.0)

    encoding = tiktoken.encoding_for_model("gpt-4o")

    # for choice in chat_completion.choices:
    #     response = choice.message.content
    #     # print(response)
    #
    #     current_node = root
    #     tokens = encoding.encode(response)
    #     for token in tokens:
    #         # print(token, encoding.decode_single_token_bytes(token))
    #         token_tree = TokenTree(token, encoding.decode_single_token_bytes(token), 0.0)
    #         current_node.merge_children([token_tree])
    #         current_node = current_node.children[token]
    for choice in chat_completion.choices:
        logprobs = choice.logprobs.content
        # print(response)

        current_node = root
        # tokens = encoding.encode(response)
        for logprob in logprobs:

            # Add each of the possible logprobs
            for top_logprob in logprob.top_logprobs:
                token = encoding.encode(top_logprob.token)[0]
                # print(token, encoding.decode_single_token_bytes(token))
                token_tree = TokenTree(token, encoding.decode_single_token_bytes(token), top_logprob.logprob)
                current_node.merge_children([token_tree])

            # Traverse down to the actual selected token, which might have been improbable
            token = encoding.encode(logprob.token)[0]
            token_tree = TokenTree(token, encoding.decode_single_token_bytes(token), logprob.logprob)
            current_node.merge_children([token_tree])

            current_node = current_node.children[token]

    print(root.to_graphviz())

