from ..config.database import engine, meta

meta_object = meta

meta_object.reflect(bind=engine)

users = meta.tables['users']
contacts = meta.tables['contacts']
websites = meta.tables['website']

if len(meta.sorted_tables) > 0:
    print('Connection to database active.')