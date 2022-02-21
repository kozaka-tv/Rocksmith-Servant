class TreeNode(dict):
    def __init__(self, name, children=None):
        super().__init__()
        self.__dict__ = self
        self.name = name
        self.children = list(children) if children is not None else []

    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = TreeNode(dict_['name'], dict_['children'])
        #        node.children = [TreeNode.from_dict(child) for child in node.children]
        node.children = list(map(TreeNode.from_dict, node.children))
        return node


if __name__ == '__main__':
    import json

    tree = TreeNode('Parent')
    tree.children.append(TreeNode('Child 1'))
    child2 = TreeNode('Child 2')
    tree.children.append(child2)
    child2.children.append(TreeNode('Grand Kid'))
    child2.children[0].children.append(TreeNode('Great Grand Kid'))

    json_str = json.dumps(tree, indent=2)
    print(json_str)
    print()

    pyobj = TreeNode.from_dict(json.loads(json_str))  # reconstitute

    print('pyobj class: {}'.format(pyobj.__class__.__name__))  # -> TreeNode
    print(json.dumps(pyobj, indent=2))
