# MySQL 数据库

- Olist_21_tables_mysql.sql.gz：完整 21 表数据库；下载并用 7-Zip 等工具解压出 SQL 后，再导入 MySQL。
- Olist_21_tables_schema.sql：仅创建数据库、表及外键，不含数据。
- database_manifest.json：表名、行数和外键清单。

完整文件包含建表语句，因此不要先执行 schema 文件再导入完整文件。使用 MySQL 8.0.16+，在无同名表的空数据库环境导入；数据库名为 olist_delivery_mysql。网站使用已导出的本地数据，不需要启动数据库。网页新增的客服备注保存在浏览器，不会写入此 SQL 文件。
