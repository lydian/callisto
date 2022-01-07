from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class TocNode:
    def __init__(
        self, level: int, text: Optional[str] = None, anchor: Optional[str] = None
    ) -> None:
        self.level: int = level
        self.text: Optional[str] = text
        self.anchor: Optional[str] = anchor
        self.parents: Dict[int, TocNode] = {}
        self.children: List[TocNode] = []

    def _add_child(self, child):
        # type: (TocNode) -> None
        self.children.append(child)
        for level in self.parents:
            child.parents[level] = self.parents[level]
        child.parents[self.level] = self

    def add_child(self, child):
        # type: (TocNode) -> None
        parent = self
        for level in range(self.level + 1, child.level):
            dummy = TocNode(level)
            parent._add_child(dummy)
            parent = dummy
        else:
            parent._add_child(child)

    def __repr__(self) -> str:
        children = ",".join([str(c) for c in self.children])
        return f"L{self.level} Node(children=[{children}])"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "text": self.text,
            "anchor": self.anchor,
            "children": [c.to_dict() for c in self.children],
        }
