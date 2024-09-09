#!/usr/bin/env python

import argparse
import flask
from flask import request, render_template, Blueprint, Flask
import html
import base64
import os

from token_tree_builder import TokenTreeBuilder

from dotenv import load_dotenv
load_dotenv()

# MODEL = "gpt-3.5-turbo"
MODEL = "gpt-4o-mini"
MAXIMUM_NUMBER_OF_RUNS = 100
MAXIMUM_MAX_TOKENS = 50
MAXIMUM_TOP_LOGPROBS = 10
MAXIMUM_PROMPT_SIZE = 500

BASE_PATH = os.environ.get("BASE_PATH", "/")

app = Blueprint("app", __name__, template_folder="templates", static_folder="static")

@app.route("/", methods=["GET"])
def index():
    number_of_runs = int(request.args.get("number_of_runs", 5))
    if number_of_runs > MAXIMUM_NUMBER_OF_RUNS:
        number_of_runs = MAXIMUM_NUMBER_OF_RUNS
    max_tokens = int(request.args.get("max_tokens", 10))
    if max_tokens > MAXIMUM_MAX_TOKENS:
        max_tokens = MAXIMUM_MAX_TOKENS
    top_logprobs = int(request.args.get("top_logprobs", 0))
    if top_logprobs > MAXIMUM_TOP_LOGPROBS:
        top_logprobs = MAXIMUM_TOP_LOGPROBS
    show_token_id = bool(request.args.get("show_token_id") == "true")
    show_log_prob = bool(request.args.get("show_log_prob") == "true")
    show_gen_count = bool(request.args.get("show_gen_count") == "true")
    show_message = bool(request.args.get("show_message") == "true")
    top_down_tree = bool(request.args.get("top_down_tree") == "true")
    seed = int(request.args.get("seed", -1))

    prompt = html.escape(request.args.get(
        "prompt",
        "Once upon a time there was a kitten named "
    ))

    prompt = prompt[:MAXIMUM_PROMPT_SIZE]

    print(f"token_tree_builder.run({prompt}, model={MODEL}, n={number_of_runs}, max_tokens={max_tokens}, top_logprobs={top_logprobs}, seed={seed})")
    token_tree_builder = TokenTreeBuilder()
    tree = token_tree_builder.run(prompt, model=MODEL, n=number_of_runs, max_tokens=max_tokens, top_logprobs=top_logprobs, seed=seed)
    print(f"in app show_token_id = {show_token_id}")
    graphviz = tree.to_graphviz(show_token_id=show_token_id, show_log_prob=show_log_prob, show_gen_count=show_gen_count, show_message=show_message, top_down_tree=top_down_tree)
    print(graphviz)
    encoded_graphviz = base64.b64encode(graphviz.encode('utf-8')).decode('utf-8')
    print(encoded_graphviz)

    return render_template(
            "index.html",
            BASE_PATH=BASE_PATH,
            MODEL=MODEL,
            prompt=prompt,
            number_of_runs=number_of_runs,
            max_tokens=max_tokens,
            top_logprobs=top_logprobs,
            seed=seed,
            show_token_id=show_token_id,
            show_log_prob=show_log_prob,
            show_gen_count=show_gen_count,
            show_message=show_message,
            top_down_tree=top_down_tree,
            encoded_graphviz=encoded_graphviz,
            MAXIMUM_NUMBER_OF_RUNS=MAXIMUM_NUMBER_OF_RUNS,
            MAXIMUM_MAX_TOKENS=MAXIMUM_MAX_TOKENS,
            MAXIMUM_TOP_LOGPROBS=MAXIMUM_TOP_LOGPROBS,
            MAXIMUM_PROMPT_SIZE=MAXIMUM_PROMPT_SIZE,
        )


real_app = Flask(__name__)
real_app.register_blueprint(app, url_prefix=BASE_PATH)

def start_server():
    real_app.run(host="0.0.0.0", debug=True)

def run_one_off():
    token_tree_builder = TokenTreeBuilder()
    tree = token_tree_builder.run("Once upon a time there was a kitten named...", model="gpt-3.5-turbo", n=20, max_tokens=10, top_logprobs=10)
    print(tree.to_graphviz())

def main():
    parser = argparse.ArgumentParser(description="Token Tree Generator")
    parser.add_argument('-s', '--server', action='store_true', help='Start the server')

    args = parser.parse_args()

    if args.server:
        start_server()
    else:
        run_one_off()

if __name__ == "__main__":
    main()
