from flask import Flask
from blueprints.image_api import image_api  # Import the Blueprint
from models.image import Image

#get the csv file and perform Preprocessing then store in sqlite database
Image.image_processing()


# Initialize Flask App
app = Flask(__name__)
# Register the Blueprint
app.register_blueprint(image_api, url_prefix='/api')



if __name__ == '__main__':
    print("Starting the Flask API server...")
    app.run(debug=True)

