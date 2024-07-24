from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:12345678@localhost/backlinks")

meta = MetaData()

connection = engine.connect()
