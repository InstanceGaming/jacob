from abc import ABC, abstractmethod
from typing import List, Literal, Optional


class TreeNode:
    
    @property
    def is_child(self):
        return self._parent is not None
    
    @property
    def is_parent(self):
        return len(self._children)
    
    @property
    def node_id(self):
        return self._node_id
    
    @property
    def depth(self):
        return self._depth
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def children(self):
        return self._children
    
    def __init__(self,
                 node_id,
                 depth: Optional[int] = None,
                 parent: Optional['TreeNode'] = None,
                 children: List['TreeNode'] = None):
        self._node_id = node_id
        self._depth = depth
        self._parent = parent
        self._children = children or []
        
        self.next_node: Optional['TreeNode'] = None
        self.previous_node: Optional['TreeNode'] = None
    
    def insert_child(self, index: int, node: 'TreeNode'):
        self._children.insert(index, node)
    
    def insert_child_adjacent(self, existing_node: 'TreeNode', direction: Literal[-1, 1], node: 'TreeNode') -> int:
        for i, n in enumerate(self._children):
            if n == existing_node:
                insertion_index = i + direction
                self.insert_child(insertion_index, node)
                return insertion_index
        return -1
    
    def append_child(self, child: 'TreeNode'):
        self._children.append(child)
    
    def remove_child(self, child: 'TreeNode'):
        self._children.remove(child)
    
    def change_parent(self, new_parent: 'TreeNode'):
        self._parent = new_parent
    
    def change_depth(self, new_depth: int):
        self._depth = new_depth
    
    def __contains__(self, item):
        assert isinstance(item, TreeNode)
        return item in self._children
    
    def __iter__(self):
        return iter(self._children)
    
    def __lt__(self, other):
        assert isinstance(other, TreeNode)
        return self._node_id <= other.node_id
    
    def __eq__(self, other):
        assert isinstance(other, TreeNode)
        return self._node_id == other.node_id
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __repr__(self):
        return f'<TreeNode {str(self.node_id)} {len(self._children)} children>'


def link_nodes(nodes: List[TreeNode]) -> None:
    """
    Link list of tree nodes, assuming list is in sequential order in-place.
    :param nodes: sequential list of tree nodes
    """
    for i, node in enumerate(nodes):
        try:
            previous_index = i - 1
            node.previous_node = nodes[previous_index]
        except IndexError:
            pass

        try:
            next_index = i + 1
            node.next_node = nodes[next_index]
        except IndexError:
            pass


def populate_hierarchy(nodes: List[TreeNode]) -> None:
    """
    Associate tree node children to parents and vice-versa in-place.
    :param nodes: unassociated tree nodes
    """
    parent_stack = []
    for i, node in enumerate(nodes):
        if node.depth == 0:
            parent_stack = [node]
            continue
        
        # -1 <= rewrite parent stack, 0 = same depth, 1 = child
        depth_delta = node.depth - node.previous_node.depth if node.previous_node is not None else 1
        if depth_delta < 0:
            # must traverse back up the parent stack to find item parent
            del parent_stack[-1: (-1 + depth_delta): -1]
            parent = parent_stack[-1]
        elif depth_delta == 0:
            # parent is just the latest item on the parent stack
            parent = parent_stack[-1]
        elif depth_delta == 1:
            parent = node.previous_node
            
            # prevent duplicate root nodes
            if parent.depth:
                parent_stack.append(parent)
        else:
            raise ValueError(f'invalid depth delta {depth_delta}')
        
        node.change_parent(parent)
        parent.append_child(node)


class TreeTraverser(ABC):
    
    def __init__(self, max_depth: int = -1):
        self.max_depth = max_depth
    
    def iter_nodes(self, nodes: List[TreeNode], start=0):
        for i, node in enumerate(nodes, start=start):
            yield i, node
    
    def process_branch(self,
                       nodes: List[TreeNode],
                       whitelist: Optional[List[TreeNode]] = None,
                       blacklist: Optional[List[TreeNode]] = None,
                       start: int = 0):
        for i, node in self.iter_nodes(nodes, start=start):
            if self.max_depth != -1 and i > self.max_depth:
                break
            
            if whitelist is not None and node not in whitelist:
                continue
            
            if blacklist is not None and node in blacklist:
                continue
            
            if node.is_parent:
                self.process_branch(node.children,
                                    whitelist=whitelist,
                                    blacklist=blacklist,
                                    start=i)
            else:
                if self.process_leaf(i, node):
                    break

    @abstractmethod
    def process_leaf(self, i: int, node: TreeNode) -> bool:
        pass
