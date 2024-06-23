#!/usr/bin/env python

import argparse
from dotenv import load_dotenv
from token_tree_builder import TokenTreeBuilder

import flask
from flask import request
import html
import base64

MODEL = "gpt-3.5-turbo"
MAXIMUM_NUMBER_OF_RUNS = 50
MAXIMUM_MAX_TOKENS = 10
MAXIMUM_TOP_LOGPROBS = 10
MAXIMUM_PROMPT_SIZE = 500

app = flask.Flask(__name__)

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

    prompt = html.escape(request.args.get(
        "prompt",
        "Once upon a time there was a kitten named "
    ))

    prompt = prompt[:MAXIMUM_PROMPT_SIZE]

    print(f"token_tree_builder.run({prompt}, model={MODEL}, n={number_of_runs}, max_tokens={max_tokens}, top_logprobs={top_logprobs})")
    token_tree_builder = TokenTreeBuilder()
    tree = token_tree_builder.run(prompt, model=MODEL, n=number_of_runs, max_tokens=max_tokens, top_logprobs=top_logprobs)
    print(f"in app show_token_id = {show_token_id}")
    graphviz = tree.to_graphviz(show_token_id=show_token_id, show_log_prob=show_log_prob)
    print(graphviz)
    encoded_graphviz = base64.b64encode(graphviz.encode('utf-8')).decode('utf-8')
    print(encoded_graphviz)

    return f"""
        <h1>Generate a tree of tokens!</h1>
        <p>Enter a prompt. We'll explore the tokens that get generated in response. At each token we can see what the token's ID is, how it is represented in text, and what some possible next-tokens are.</p>
        <form method="get" action="/">
            <label for="prompt">Prompt:</label>
            <br/>
            <textarea name="prompt" cols=80 rows=5>{prompt}</textarea>
            <br/>
            <label for="number_of_runs">number_of_runs:</label>
            <input type="text" name="number_of_runs" value="{number_of_runs}" size=5 />
            <label for="max_tokens">max_tokens:</label>
            <input type="text" name="max_tokens" value="{max_tokens}" size=5 />
            <label for="top_logprobs">top_logprobs:</label>
            <input type="text" name="top_logprobs" value="{top_logprobs}" size=5 />
            <br/>
            <input type="checkbox" name="show_token_id" value="true" {"checked" if show_token_id else ""} />
            <label for="show_token_id">Show token_id</label>
            <input type="checkbox" name="show_log_prob" value="true" {"checked" if show_log_prob else ""} />
            <label for="show_log_prob">Show log prob</label>
            <input type="submit" value="Go!" />
        </form>
    """ + """
        <div id="graphviz"></div>

        <script src="https://unpkg.com/@viz-js/viz"></script>

        <script>
            function renderGraphviz(dot) {
                Viz.instance().then(viz => {
                  document.getElementById("graphviz").innerHTML = ""
                  document.getElementById("graphviz").appendChild(viz.renderSVGElement(dot));
                });
            }
    """ + f"""
            let dot = atob("{encoded_graphviz}");
            renderGraphviz(dot);
    """ + """
        </script>
        <style>
            #graphviz svg {
                width: 90vw;
                overflow: visible;
            }
            #graphviz svg .node polygon {
              fill: white;
              filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.5));
            }
        </style>
    """

def start_server():
    app.run(debug=True)

def run_one_off():
    token_tree_builder = TokenTreeBuilder()
    tree = token_tree_builder.run("Once upon a time there was a kitten named...", model="gpt-3.5-turbo", n=20, max_tokens=10, top_logprobs=10)
    print(tree.to_graphviz())

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Token Tree Generator")
    parser.add_argument('-s', '--server', action='store_true', help='Start the server')

    args = parser.parse_args()

    if args.server:
        start_server()
    else:
        run_one_off()

if __name__ == "__main__":
    main()
