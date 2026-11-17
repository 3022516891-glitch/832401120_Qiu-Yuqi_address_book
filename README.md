# EE308 通讯录

Python + Flask + SQLite 课程作业框架。可新增联系人，为同一联系人录入多条联系方式，收藏或取消收藏，并在「我的收藏」中查看已收藏联系人。

## 本地运行（Windows PowerShell）

在本目录执行以下命令，再打开浏览器访问 `http://127.0.0.1:5000`。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run
```

应用首次启动会创建 `instance/contacts.sqlite3`。

| 路径 | 用途 |
| --- | --- |
| `app.py` | 应用入口，联系人录入、列表和收藏路由 |
| `storage.py` / `schema.sql` | 数据库连接、联系人与联系方式的一对多关系 |
| `templates/` / `static/` | 页面模板和样式 |

## Excel import and export

Use **Export All to Excel** to download every contact, including favorites. Each contact
occupies one row. Repeated methods use additional columns such as `Phone 2` and
`Phone 3`. Phone numbers are exported as text.

Use **Import Excel** to download a blank template or upload an exported or compatible
`.xlsx` file. `Name` is required. `Favorite` accepts Yes, No, or a blank cell.
Import adds new contacts, including when a name already exists. If a row fails
validation, the workbook is rejected before any contact is added.

## 功能演示

1. 在首页点击 **Add Contact**，填写示例姓名 Alex Chen。用 **Add another method** 增加一条电话和一条邮箱，保存后核对联系人卡片。
2. 点击 **Add to favorites**，再切换到 **Favorites**，确认该联系人出现在收藏列表。
3. 点击 **Export All to Excel**，打开下载的 `contacts.xlsx`，确认同一联系人的两个号码分别位于 `Phone` 和 `Phone 2` 列。
4. 打开 **Import Excel** 下载空白模板。另填一位示例联系人并上传，确认成功提示，并在 **All Contacts** 核对新增记录。

开发约定见 [Coding Standards](CODING_STANDARDS.md)。
