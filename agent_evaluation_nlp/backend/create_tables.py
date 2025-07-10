# create_tables.py
from database.sql import Base, engine

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")

if __name__ == "__main__":
    create_tables()