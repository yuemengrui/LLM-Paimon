# *_*coding:utf-8 *_*
# @Author : YueMengRui
import sshtunnel
from urllib import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


ssh_host = ""  # 服务器ip
ssh_user = ""  # ssh连接用户名
ssh_password = ""  # ssh密码
ssh_port = 0

forwarding_server = sshtunnel.SSHTunnelForwarder(
    (ssh_host, ssh_port),
    ssh_username=ssh_user,
    ssh_password=ssh_password,
    set_keepalive=5.0,
    remote_bind_address=('localhost', 3306)
)
forwarding_server.start()
local_port = forwarding_server.local_bind_port

# 数据库连接配置
SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://{}:{}@{}:{}/{}".format('root', parse.quote_plus("666666"), '127.0.0.1', local_port, 'llm_paimon')
)

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URI)
# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 声明基类
Base = declarative_base()
