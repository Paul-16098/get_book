import glob
import json
from typing import Any, TypedDict, NotRequired
from webbrowser import open as open_url
from urllib.parse import quote
from pylib.paul_tools import logger
from pylib.paul_tools.Tools import clipboard


class JSONType(TypedDict):
    name: str
    web: str
    cofg: NotRequired[dict[str, Any]]


class WebData:
    def __init__(self, name: str, web: str, cofg: dict[str, Any] | None = None) -> None:
        self._name = name
        self._web = web
        self._cofg = cofg or {}
        self._rt = quote if self._cofg.get("quote", False) else lambda x: x

    @staticmethod
    def from_file_load(path: str) -> "WebData":
        """Load book names and URLs from a JSON file.

        :param path: Path to the JSON file
        :return: A WebData instance
        """
        with open(path, "r", encoding="utf-8") as f:
            j: JSONType = json.load(f)
        return WebData(j.get('name', ''), j.get('web', ''), j.get('cofg', {}))

    @property
    def name(self) -> str:
        return self._name

    @property
    def web(self) -> str:
        return self._web

    @property
    def cofg(self) -> dict[str, Any]:
        return self._cofg

    def get(self, *args: str | list[str] | dict[str, str] | None) -> dict[str, str]:
        """Format the web URL with given arguments.

        :param args: Variable length argument list of strings, lists, or dictionaries for URL formatting
        :return: A dictionary with formatted URL
        """
        values, kwargs = [], {}
        for arg in args:
            if arg is None:
                continue
            elif isinstance(arg, str):
                values.append(self._rt(arg))
            elif isinstance(arg, list):
                values.extend(map(self._rt, arg))
            elif isinstance(arg, dict):
                kwargs.update({k: self._rt(v) for k, v in arg.items()})

        try:
            return {"name": self._name, "web": self._web.format(*values, **kwargs)}
        except KeyError:
            return {"name": self._name, "web": self._web}

    def open(self, *args: str | list[str] | dict[str, str] | None) -> bool:
        """Open the formatted URL in the default browser.

        :param args: Arguments to format the URL
        :return: Result of opening the URL
        """
        return open_url(self.get(*args)['web'])


class WebDataList(list[WebData]):
    def get(self, index: int, *args: str | list[str] | dict[str, str] | None) -> dict[str, str]:
        """Get formatted URL for a specific WebData in the list.

        :param index: Index of the WebData instance
        :param args: Formatting arguments
        :return: Formatted URL dictionary
        """
        return self[index].get(*args)

    def get_all(self, *args: str | list[str] | dict[str, str] | None) -> list[dict[str, str]]:
        """Get formatted URLs for all WebData in the list.

        :param args: Formatting arguments
        :return: list of formatted URL dictionaries
        """
        return [data.get(*args) for data in self]

    def open(self, index: int, *args: str | list[str] | dict[str, str] | None) -> bool:
        """Open URL for a specific WebData in the list.

        :param index: Index of the WebData instance
        :param args: Formatting arguments
        :return: Result of opening the URL
        """
        return self[index].open(*args)

    def open_all(self, *args: str | list[str] | dict[str, str] | None) -> list[bool]:
        """Open URLs for all WebData in the list.

        :param args: Formatting arguments
        :return: list of results from opening each URL
        """
        return [data.open(*args) for data in self]


# Predefined WebData instances
web_data_list = WebDataList((
    # WebData("小說狂人", "https://czbooks.net/s/{q}?q={q}"),
    # WebData("85度c小說網", "https://www.85novel.com/search?k={q}"),
    # WebData("69書吧", "https://69shuba.cx/modules/article/search.php")
))

book_list: list[str] = []


def text_to_data(text: str) -> list[str]:
    """將文字轉換為書名清單。"""
    return [line.split(' ')[1].strip() for line in text.strip().split('\n') if line.strip()]


def is_data_text(data_text: str) -> bool:
    """檢查文字中是否包含與資料相關的關鍵字。"""
    return any(keyword in data_text for keyword in ["有更新", "尚未閱讀", "無更新"])


def main() -> None:
    try:
        for book_json in glob.glob("./book-data/*.json"):
            web_data_list.append(WebData.from_file_load(book_json))
            logger.debug(f"load book data: {book_json}")
        while True:
            user_input = input("Book name: ")
            if not user_input:
                break
            if is_data_text(user_input):
                book_list.extend(text_to_data(user_input))
            else:
                book_list.append(user_input)

        for i in range((book_list_len := len(book_list))):
            book = book_list[i]
            input(f"{((i+1)/book_list_len) * 100:.2f}%({i +
                  1}/{book_list_len})=>{book}: Press Enter to continue...")
            clipboard.copy_to_clipboard(book)
            web_data_list.open_all({"q": book})

    except (EOFError, KeyboardInterrupt):
        logger.info("\nOperation canceled.")


if __name__ == "__main__":
    main()
