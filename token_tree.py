import textwrap

class TokenTree:
    # Keep track of a global incrementing node id
    next_node_id = 0
    max_gen_count = 1

    def __init__(self, token_id, token_bytes, log_prob):
        self.token_id = token_id
        self.token_bytes = token_bytes
        self.log_prob = log_prob
        self.children = {}
        self.gen_count = 0
        self.last_message = None

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
        return self.token_bytes.decode("utf-8", "backslashreplace").replace('"', '\\"').replace("\n", "\\\\n").replace(" ", '⎵')

    def to_graphviz_node(self, show_token_id=True, show_log_prob=True, show_gen_count=True, show_message=True):
        print(f"to_graphviz_node show_token_id = {show_token_id}")
        display_color_value = self.gen_count / TokenTree.max_gen_count if self.gen_count <= TokenTree.max_gen_count else 1
        display_color = "gray80"
        if self.gen_count > 0:
            display_color = f"0.45 {display_color_value} 0.85"
        if self.node_id > 0:
            label = f"{self.token_utf8_escaped()}"
            if show_gen_count:
                label += f"\\nx{self.gen_count}"
            if show_token_id:
                label += f"\\n[{self.token_id}]"
            if show_log_prob:
                label += f"\\n@ {round(self.log_prob, 2)}"
            other = ""
            if self.gen_count == 0:
                # This one was a non-followed logprob
                other = f"style=filled fillcolor=gray80"
            if self.gen_count > 0:
                other = f"style=filled fillcolor=\"{display_color}\""
            output = f"n{self.node_id} [label=\"{label}\" {other}]\n"
        else:
            output = f"n{self.node_id} [shape=doublecircle label=\"\"]\n"

        for child in self.children.values():
            output += f"n{self.node_id} -> n{child.node_id}\n"
            output += child.to_graphviz_node(show_token_id=show_token_id, show_log_prob=show_log_prob, show_gen_count=show_gen_count, show_message=show_message)

        if self.node_id > 0 and len(self.children) == 0 and show_message and self.last_message is not None:
            print(f"show_message = {show_message}")
            output += f"n{self.node_id} -> message{self.node_id}\n"
            output += f"message{self.node_id} [label=\"{textwrap.fill(self.last_message, 40)}\" style=filled fillcolor=white]\n"

        return output

    def to_graphviz(self, show_token_id=True, show_log_prob=True, show_gen_count=True, show_message=True, top_down_tree=False):
        print(f"to_graphviz show_token_id = {show_token_id}")
        return f"""
              digraph "Token Tree" {{
                rankdir={"TB" if top_down_tree else "LR"};
                bgcolor=transparent;
                node [shape=rectangle ordering=out style=filled fillcolor=white color=white];
                edge [color=white];

                {self.to_graphviz_node(show_token_id=show_token_id, show_log_prob=show_log_prob, show_gen_count=show_gen_count, show_message=show_message)}

              }}
            """

