import os

if os.getenv("USE_SQLITE", "0") != "1":
    import pymysql

    pymysql.version_info = (1, 4, 3, "final", 0)
    pymysql.install_as_MySQLdb()
