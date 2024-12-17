import pandas as pd
from skimage.transform import resize
import numpy as np

import connection.database as db

class Image:
    def __init__(self, file_path, original_width=200, target_width=150):
        self.file_path = file_path
        self.original_width = original_width
        self.target_width = target_width
        self.df = None
        self.resized_df = None

    def load_data(self):
        """Load the CSV file into a DataFrame."""
        print("Loading data...")
        self.df = pd.read_csv(self.file_path)
        print("Data loaded successfully!")

    def resize_image_data(self):
        """
        Resize the image pixel data from original_width to target_width.
        """
        if self.df is None:
            raise ValueError(
                "Data not loaded. Use the load_data() method first.")

        print("Resizing image data...")
        # Separate depth and pixel columns
        self.depth = self.df['depth']  # Assuming 'depth' is the column name
        pixels = self.df.drop(columns=['depth']).to_numpy()

        def resize_pixels(row):
            image_row = row.reshape((1, self.original_width))
            resized_row = resize(
                    image_row, (1, self.target_width), anti_aliasing=True)
            return resized_row.flatten()

        # Apply resizing
        resized_pixels = np.array([resize_pixels(row) for row in pixels])

            # Rebuild the DataFrame
        self.resized_df = pd.DataFrame(resized_pixels, columns=[f'pixel_{i}' for i in range(self.target_width)])
        self.resized_df.insert(0, 'depth', self.depth)
        print("Image data resized successfully!")
        


    def save_to_database(self):
        """
        Save the resized DataFrame to a database table.
        
        """
        if self.resized_df is None:
            raise ValueError("Resized data not available. Use the resize_image_data() method first.")
        db.saveTodatabase(self.resized_df)
        

    def image_processing():
        # Initialize the class
        image_data = Image(file_path='data/csv/img.csv', original_width=200, target_width=150)
        # Load data
        image_data.load_data()
        # Resize the image pixel data
        image_data.resize_image_data()
        # Save resized data to a database
        image_data.save_to_database()