
from backend.database.db import Base, engine
from backend.models import db_models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Freaknssential database tables initialized!")


if __name__ == "__main__":
    initialize_database()
