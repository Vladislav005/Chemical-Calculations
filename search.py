import reliase

class SearchTreeNode:
    def __init__(self, kind: str, childs: list = None, is_element: bool = False):
        self.kind = kind
        if childs == None:
            childs = []
        self.childs = childs
        self.is_element = is_element

    def add_childs(self, childs: list):
        self.childs = childs
    def add_child(self, child):
        self.childs.append(child)


class SearchTree:
    def __init__(self, treeList: dict = None):
        head = SearchTreeNode('Any')
        if treeList:
            self._make(treeList, head)
        self.head = head

    def _make(self, treeList: dict, node: SearchTreeNode):
        if type(treeList) == list:
            for element in treeList:
                new_node = SearchTreeNode(kind = element, is_element=True)
                node.add_child(new_node)
        else:
            for branch in treeList.items():
                new_node = SearchTreeNode(branch[0])
                self._make(branch[1], new_node)
                node.add_child(new_node)

    def make_all_branch(self):
        rows = reliase.getAllElements('elements')
        for row in rows:
            branch = row['branch'].split(';')[:-1] + [[row['name']]]
            self.add_branch(branch)

    def _dfs(self, node: SearchTreeNode, returned_list: list):
        if node.childs == [] and node.is_element:
            returned_list.append(node.kind)
        for child in node.childs:
            self._dfs(child, returned_list)

    def _find_node(self, node: SearchTreeNode, target: str)->SearchTreeNode:
        if node.kind == target:
            return node
        for child in node.childs:
            result = self._find_node(child, target)
            if result:
                return result
        return None

    def get_elements(self, element_type: str):
        desired_node = self._find_node(self.head, element_type)
        returned_list = []
        if desired_node:
            self._dfs(desired_node, returned_list)
        return returned_list

    def add_branch(self, branch: list):
        current_node = self.head
        elements = None
        if type(branch[len(branch) - 1]) == list:
            elements = branch[len(branch) - 1]
            branch = branch[:len(branch) - 1]
        for i in range(len(branch)):
            branch_node = branch[i]
            goida = None
            for child in current_node.childs:
                if child.kind == branch_node:
                    goida = child
                    break
            if goida:
                current_node = goida
            else:
                new_node = SearchTreeNode(branch_node)
                current_node.add_child(new_node)
                current_node = new_node
        if elements:
            for el in elements:
                new_node = SearchTreeNode(el, is_element=True)
                current_node.add_child(new_node)

    def show_tree(self, node: SearchTreeNode = None):
        if node == None:
            node = self.head
        print(node.kind)
        for child in node.childs:
            self.show_tree(child)

SEARCH_TREE = SearchTree()
SEARCH_TREE.make_all_branch()


if __name__ == '__main__':
    # treeList = {
    #     'carbon': {},
    #     'alcohol': [
    #         '1-Chlorobutane',
    #         'Ethanol',
    #         '1-Hexanol',
    #     ],
    #     'acids': {},
    #     'amin': {}
    # }
    add_node = ['acids', ['Sulfuric acid']]
    tree = SearchTree()
    tree.make_all_branch()
    # tree.add_branch(add_node)
    tree.show_tree()