# Alembic 初始化配置
file_template = %%(rev)s_%%(slug)s

sqlalchemy.url = driver://user:password@localhost/dbname

version_path_separator = :

version_locations = %(here)s/versions

# encoding
encoding = utf-8

# 提交信息模板
message_template = ""

# 脚本模板
script_location = %(here)s

# 是否自动生成迁移脚本
autogenerate = true
