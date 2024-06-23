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
        return self.token_bytes.decode("utf-8", "backslashreplace").replace('"', '\\"').replace("\n", "\\\\n")

    def to_graphviz_node(self, show_token_id=True, show_log_prob=True):
        print(f"to_graphviz_node show_token_id = {show_token_id}")
        if self.node_id > 0:
            output = f"n{self.node_id} [label=\"'{self.token_utf8_escaped()}'"
            if show_token_id:
                output += f"\\n[{self.token_id}]"
            if show_log_prob:
                output += f"\\n@ {round(self.log_prob, 2)}"
            output += f"\"]\n"
        else:
            output = f"n{self.node_id} [label=\"\"]\n"

        for child in self.children.values():
            output += f"n{self.node_id} -> n{child.node_id}\n"
            output += child.to_graphviz_node(show_token_id=show_token_id, show_log_prob=show_log_prob)
        return output

    def to_graphviz(self, show_token_id=True, show_log_prob=True):
        print(f"to_graphviz show_token_id = {show_token_id}")
        return f"""
              digraph "Token Tree" {{
                rankdir=LR;
                node [shape=rectangle];

                {self.to_graphviz_node(show_token_id=show_token_id, show_log_prob=show_log_prob)}

              }}
            """

