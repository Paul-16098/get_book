# Get Book Script

## 功能

此腳本用於管理書籍資料，並根據書名生成對應的網址，方便用戶快速訪問相關內容。

## 使用方式

1. 將書籍資料以 JSON 格式放置於 `./book-data/` 資料夾中。
2. 執行腳本：

   ```bash
   python get_book.py
   ```

3. 輸入書名，或直接按下 Enter 結束輸入。
4. 按提示處理書籍資料。

## 注意事項

- 確保 `book-name.json` 文件存在，否則腳本會自動創建。
- 若腳本正在執行，重複啟動會顯示警告並退出。

## 預設目錄結構

```tree
get_book/
├── book-data/
│   └── example.json
├── get_book.py
├── README.md
└── book-name.json
```
