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

Excel 导入导出是下一阶段的功能。按照题目要求，工作表每行放一个联系人，每类信息使用单独的列，同类多条联系方式需要能够完整导出并重新导入。
