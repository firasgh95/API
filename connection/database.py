from sqlalchemy import create_engine
#  DATABASE CONNECTION
database_name = 'data/database/image_data.db'  # SQLite database file
table_name = 'resized_images'
# Create a database connection using SQLAlchemy
engine = create_engine(f'sqlite:///{database_name}', echo=False)

def saveTodatabase(data):
     
    print("Saving resized data to the database...")
    data.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Data successfully saved to database '{database_name}' in table '{table_name}'.")