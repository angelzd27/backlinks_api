from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:@localhost/backlinks")

meta = MetaData()

connection = engine.connect()
