from .database import db_session

# Dependency to get a database session
def get_db():
    # Create a new database session for each request
    db = db_session()
    try:
        # Yield the database session to the request handler
        yield db
    finally:
        db.close()