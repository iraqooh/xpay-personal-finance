from .database import db_session

# Dependency to get a database session
def get_db():
    """
    Dependency function to provide a database session for request handlers. This function creates a new database session, yields it to the request handler, and ensures that the session is properly closed after the request is processed.
    """
    db = db_session()
    try:
        # Yield the database session to the request handler
        yield db
    finally:
        db.close()