
import tiktoken
from openai import OpenAI
from token_tree import TokenTree

class TokenTreeBuilder():

    def __init__(self):
        self.client = OpenAI()

    def run(self, prompt, model="gpt-3.5-turbo", n=20, max_tokens=10, top_logprobs=10):
        chat_completion = self.client.chat.completions.create(
            model=model,
            n=n,
            max_tokens=max_tokens,
            logprobs=True,
            top_logprobs=top_logprobs,
            messages=[{"role": "user", "content": prompt}],
        )

        TokenTree.next_node_id = 0
        root = TokenTree(0, b"", 0.0)

        encoding = tiktoken.encoding_for_model(model)

        for choice in chat_completion.choices:
            logprobs = choice.logprobs.content

            current_node = root
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
                current_node.gen_count += 1
                TokenTree.max_gen_count = max(TokenTree.max_gen_count, current_node.gen_count)

        return root

