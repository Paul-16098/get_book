import glob
import json
import os
from typing import Any, NotRequired, TypedDict
from webbrowser import open as open_url

from paul_tools import logger_init
# from pyperclip import copy as copy_text


def safe_remove(filepath: str) -> None:
    """Safely remove a file if it exists."""
    if os.path.exists(filepath):
        os.remove(filepath)


def initialize_logger() -> None:
    """Initialize the logger and clean up old logs."""
    global logger
    logger = logger_init()
    safe_remove("get_book.log")  # 移除舊的日誌檔案
    logger.add("get_book.log", level="DEBUG")  # 添加新的日誌檔案


class WebDataType(TypedDict):
    """定義 WebData 的型別結構。"""

    name: str
    web: str
    cofg: NotRequired[dict[str, Any]]


class WebData:
    """表示單個網站數據的類別。"""

    def __init__(self, name: str, web: str, cofg: dict[str, Any] | None = None) -> None:
        self._name = name
        self._web = web
        self._cofg = cofg or {}

    @staticmethod
    def from_file_load(path: str) -> "WebData":
        """Load book names and URLs from a JSON file.

        :param path: Path to the JSON file
        :return: A WebData instance
        """
        with open(path, "r", encoding="utf-8") as f:
            j: WebDataType = json.load(f)
        return WebData(j.get("name", ""), j.get("web", ""), j.get("cofg", {}))

    @property
    def name(self) -> str:
        """返回網站名稱。"""
        return self._name

    @property
    def web(self) -> str:
        """返回網站 URL。"""
        return self._web

    @property
    def cofg(self) -> dict[str, Any]:
        """返回網站的配置字典。"""
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
                values.append(arg)
            elif isinstance(arg, list):
                values.extend(arg)
            elif isinstance(arg, dict):
                kwargs.update({k: v for k, v in arg.items()})

        try:
            return {"name": self._name, "web": self._web.format(*values, **kwargs)}
        except KeyError:
            return {"name": self._name, "web": self._web}

    def open(self, *args: str | list[str] | dict[str, str] | None) -> bool:
        """Open the formatted URL in the default browser.

        :param args: Arguments to format the URL
        :return: Result of opening the URL
        """
        return open_url(self.get(*args)["web"])


class WebDataList(list[WebData]):
    """表示多個 WebData 的列表類別。"""

    def get(
        self, index: int, *args: str | list[str] | dict[str, str] | None
    ) -> dict[str, str]:
        """Get formatted URL for a specific WebData in the list.

        :param index: Index of the WebData instance
        :param args: Formatting arguments
        :return: Formatted URL dictionary
        """
        return self[index].get(*args)

    def get_all(
        self, *args: str | list[str] | dict[str, str] | None
    ) -> list[dict[str, str]]:
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

    def load_web_data(self) -> None:
        """從 JSON 檔案中載入網站數據。"""
        web_datas = glob.glob("./web-data/*.json")
        for web_data in web_datas:
            self.append(WebData.from_file_load(web_data))
            logger.debug(f"load web data: {web_data}")
        logger.info(f"Loaded {len(web_datas)} web data files.")


class BookDataList(list[str]):
    """表示書籍數據的列表類別。"""

    def append(self, object: str) -> None:
        """添加書籍數據到列表中。"""
        if self.is_data_text(object):
            logger.debug(f"Appending book data: {object}")
            return super().append(self.text_to_data(object))
        logger.debug(f"Appending regular book data: {object}")
        return super().append(object)

    @staticmethod
    def text_to_data(text: str) -> str:
        """將文字轉換為書名清單。"""
        return [
            line.split(" ")[1].strip()
            for line in text.strip().split("\n")
            if line.strip()
        ][0]

    @staticmethod
    def is_data_text(data_text: str) -> bool:
        """檢查文字中是否包含與資料相關的關鍵字。"""
        return any(keyword in data_text for keyword in ["有更新", "尚未閱讀", "無更新"])

    def write_to_file(self, path: str = "book-name.json") -> None:
        """Write the book data to a file."""
        safe_remove(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self, f, ensure_ascii=False)

    def _process_single_book(self, book: str, index: int, total: int) -> None:
        """Process a single book."""
        progress = ((index + 1) / total) * 100
        logger.debug(f"Processing: {book} ({index + 1}/{total})")
        input(f"{progress:.2f}%({index + 1}/{total})=>{book}")
        web_data_list.open_all({"q": book})

    def process_books(self) -> None:
        """Process all books in the book data list."""
        total_books = len(self)
        for i, book in enumerate(
            self[:]
        ):  # Use slicing to avoid modifying the list during iteration
            self._process_single_book(book, i, total_books)
            self.pop(0)
            self.write_to_file()


# Predefined WebData instances
web_data_list = WebDataList()  # 預定義的網站數據列表

book_data: BookDataList = BookDataList()  # 預定義的書籍數據列表


def handle_user_input() -> None:
    """處理使用者輸入的書籍名稱。"""
    try:
        with open("book-name.json", encoding="utf-8") as f:
            o_l = len(book_data)
            try:
                book_data.extend(json.load(f))
            except json.decoder.JSONDecodeError as e:
                logger.error(f"Error decoding JSON file:{e.doc}({e.msg})")
            finally:
                logger.info(f"Loaded {len(book_data) - o_l} book data from file.")
    except FileNotFoundError:
        with open("book-name.json", "xt", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

    while True:
        user_input = input("Book name: ")
        if not user_input:
            break
        if BookDataList.is_data_text(user_input):
            book_data.append(BookDataList.text_to_data(user_input))
        else:
            book_data.append(user_input)
        book_data.write_to_file()


def main() -> None:
    """主函數，負責執行整個流程。"""
    try:
        initialize_logger()
        web_data_list.load_web_data()
        handle_user_input()
        book_data.process_books()
    except (EOFError, KeyboardInterrupt):
        logger.info("\nOperation canceled.")


if __name__ == "__main__":
    main()  # 執行主函數
