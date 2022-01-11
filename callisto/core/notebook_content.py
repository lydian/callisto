import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import nbformat
from bs4 import BeautifulSoup
from cssutils import parseStyle
from nbconvert.exporters import HTMLExporter

from callisto.core.toc import TocNode


class NotebookContent:

    _last_modified: Optional[str] = None
    _content: Optional[str] = None
    _dict_content: Optional[Dict[str, Any]] = None
    _html_content: Optional[str] = None
    path: str
    loader: Any

    def __init__(self, loader: Any, path: str) -> None:
        self.path = path
        self.loader = loader

    @property
    def content(self) -> Optional[str]:
        def fetch() -> None:
            content = self.loader.get(self.path, type="file")
            self._content = content["content"]
            self._last_modified = content["last_modified"]
            self._dict_content = None
            self._html_content = None

        if self._content is None:
            fetch()

        new_info = self.loader.info(self.path)
        if new_info["last_modified"] != self._last_modified:
            fetch()

        return self._content

    @property
    def dict_content(self) -> Dict[str, Any]:
        if self._dict_content is None:
            self._dict_content = json.loads(str(self.content))
        return self._dict_content

    @property
    def html_content(self) -> str:
        if self._html_content is None:
            html_exporter = HTMLExporter()
            html_exporter.template_name = "classic"
            notebook_node = nbformat.reads(
                self.content, as_version=self.dict_content["nbformat"]
            )
            html, _ = html_exporter.from_notebook_node(notebook_node)
            soup = BeautifulSoup(html, "html.parser")
            for elem in soup.find_all(class_="CodeMirror"):
                style = parseStyle(elem.get("style", ""))
                style["overflow-x"] = "auto"
                elem["style"] = style.cssText
            self._html_content = str(soup)
        return self._html_content

    def toc(self) -> List[Any]:
        soup = BeautifulSoup(self.html_content, "html.parser")
        headings: List[TocNode] = [
            TocNode(
                int(item.name.replace("h", "")),
                item.contents[0].text,
                item["id"],
            )
            for item in soup.find_all(["h1", "h2", "h3", "h4", "h5"])
        ]

        tree = []
        prev = None
        for h in headings:
            if h.level == 1:
                tree.append(h)
            elif prev is None:
                dummy = TocNode(1)
                dummy.add_child(h)
                tree.append(dummy)
            elif h.level == prev.level:
                prev.parents[h.level - 1].add_child(h)
            elif h.level < prev.level:
                prev.parents[h.level - 1].add_child(h)
            else:
                prev.add_child(h)
            prev = h

        return [n.to_dict() for n in tree]
