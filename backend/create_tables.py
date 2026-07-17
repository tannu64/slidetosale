from database import engine, Base
import models  # importing this registers all seven table classes on Base

# Reads every class that inherits from Base and creates its table if missing.
Base.metadata.create_all(bind=engine)
print("All tables created.")
