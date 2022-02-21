class RSPLTreeNode(dict):
    def __init__(self, playlist, dlc_set=None):
        super().__init__()
        self.__dict__ = self
        self.playlist = list(playlist) if dlc_set is not None else []
        self.dlc_set = list(dlc_set) if dlc_set is not None else []

    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct RSPLTreeNode-based tree from dictionary. """
        node = RSPLTreeNode(dict_['playlist'], dict_['dlc_set'])
        #        node.dlc_set = [RSPLTreeNode.from_dict(child) for child in node.dlc_set]
        node.dlc_set = list(map(RSPLTreeNode.from_dict, node.dlc_set))
        return node


if __name__ == '__main__':
    import json

    tree = RSPLTreeNode('Parent')
    tree.dlc_set.append(RSPLTreeNode('Child 1'))
    child2 = RSPLTreeNode('Child 2')
    tree.dlc_set.append(child2)
    child2.dlc_set.append(RSPLTreeNode('Grand Kid'))
    child2.dlc_set[0].dlc_set.append(RSPLTreeNode('Great Grand Kid'))

    json_str = json.dumps(tree, indent=2)
    print(json_str)
    print()

    pyobj = RSPLTreeNode.from_dict(json.loads(json_str))  # reconstitute

    print('pyobj class: {}'.format(pyobj.__class__.__name__))  # -> RSPLTreeNode
    print(json.dumps(pyobj, indent=2))
