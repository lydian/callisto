from contextlib import contextmanager
from unittest import mock

import pytest

from callisto.core.notebook_content import NotebookContent
from callisto.core.contents_loader import ContentsLoader


class TestNotebookContent:
    @pytest.fixture
    def loader(self):
        return mock.MagicMock(spec=ContentsLoader)

    @pytest.fixture
    def notebook_content(self, loader):
        return NotebookContent(loader, "/some/path")

    def test_content(self, notebook_content, loader):
        v1_result = {"content": '{"test": 1}', "last_modified": "2021-12-01 00:00:00"}
        v2_result = {"content": '{"test": 2}', "last_modified": "2021-12-01 00:00:01"}

        loader.get.return_value = v1_result
        loader.info.return_value = {"last_modified": v1_result["last_modified"]}

        assert notebook_content.content == v1_result["content"]
        assert notebook_content._last_modified == v1_result["last_modified"]
        notebook_content._dict_content = {"test": 1}
        notebook_content._html_content = "html for test 1"

        # query again
        assert notebook_content.content == v1_result["content"]

        # update content
        loader.get.return_value = v2_result
        loader.info.return_value = {"last_modified": v2_result["last_modified"]}
        assert notebook_content.content == v2_result["content"]
        assert notebook_content._dict_content is None
        assert notebook_content._html_content is None

        loader.get.call_count == 2

    @contextmanager
    def mock_property(self, name, value):
        with mock.patch(
            f"callisto.core.notebook_content.NotebookContent.{name}",
            new_callable=mock.PropertyMock,
        ) as m:
            m.return_value = value
            yield

    def test_dict_content(self, loader):
        with self.mock_property("content", '{"test": 1}'):
            notebook_content = NotebookContent(loader, "/path/file")

            assert notebook_content.content == '{"test": 1}'
            assert notebook_content.dict_content == {"test": 1}

    @pytest.fixture
    def mock_nb_reads(self):
        with mock.patch("nbformat.reads") as m:
            yield m

    @pytest.fixture
    def mock_html_exporter(self):
        with mock.patch(
            "callisto.core.notebook_content.HTMLExporter.from_notebook_node",
            autospec=True,
        ) as m:
            m.return_value = "<html>content</html>", "others"
            yield m

    def test_html_content(self, loader, mock_nb_reads, mock_html_exporter):
        with self.mock_property("content", "some-content"), self.mock_property(
            "dict_content", {"nbformat": 4}
        ):
            notebook_content = NotebookContent(loader, "/some/path.ipynb")
            assert notebook_content.html_content == "<html>content</html>"
            mock_nb_reads.assert_called_once_with("some-content", as_version=4)

    @pytest.fixture
    def mock_soup(self):
        with mock.patch("callisto.core.notebook_content.BeautifulSoup") as m:
            yield m.return_value

    def fake_heading(self, name, id, content):
        class DummyHeading(dict):
            def __init__(self, name: str, contents: str, id: int) -> None:
                self.name = name
                self["id"] = id
                self.contents = [mock.MagicMock(text=content)]

        return DummyHeading(name=name, id=id, contents=[content, "other-content"])

    def test_toc(self, loader, mock_soup):
        with self.mock_property("html_content", "some-content"):
            mock_soup.find_all.return_value = [
                self.fake_heading(name="h2", content="0.1", id="1"),
                self.fake_heading(name="h1", content="1", id="2"),
                self.fake_heading(name="h2", content="1.1", id="3"),
                self.fake_heading(name="h5", content="1.1.0.0.1", id="4"),
                self.fake_heading(name="h5", content="1.1.0.0.2", id="5"),
                self.fake_heading(name="h4", content="1.1.0.1", id="6"),
            ]
            assert NotebookContent(loader, "path").toc() == [
                {
                    "level": 1,
                    "text": None,
                    "anchor": None,
                    "children": [
                        {"level": 2, "text": "0.1", "anchor": "1", "children": []}
                    ],
                },
                {
                    "level": 1,
                    "text": "1",
                    "anchor": "2",
                    "children": [
                        {
                            "level": 2,
                            "text": "1.1",
                            "anchor": "3",
                            "children": [
                                {
                                    "level": 3,
                                    "text": None,
                                    "anchor": None,
                                    "children": [
                                        {
                                            "level": 4,
                                            "text": None,
                                            "anchor": None,
                                            "children": [
                                                {
                                                    "level": 5,
                                                    "text": "1.1.0.0.1",
                                                    "anchor": "4",
                                                    "children": [],
                                                },
                                                {
                                                    "level": 5,
                                                    "text": "1.1.0.0.2",
                                                    "anchor": "5",
                                                    "children": [],
                                                },
                                            ],
                                        },
                                        {
                                            "level": 4,
                                            "text": "1.1.0.1",
                                            "anchor": "6",
                                            "children": [],
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ]
