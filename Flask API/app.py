from email.mime import image
from flask import Flask, jsonify, render_template, request, url_for
import numpy as np
from load_model2 import predict_shelflife_status
import werkzeug
import os
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
from skimage.feature import hog
import pickle

app = Flask(__name__)

# def generator_for_data():
#     for i in range(0,5):
#         yield round(1.1 * np.random.randn() + 5, 2)

# @app.before_request
# def before():
#     print("This is executed BEFORE each request.")

temp_list = []
image_list = []

@app.route("/api", methods=["GET"])
def api():
    if(request.method == 'GET'):

        global temp_list
        response = jsonify(temp_list)

        return response

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
        
@app.route('/add', methods =['POST'])
def add_data_point():
    if(request.method == 'POST'):

        global temp_list
        temp_list.append({"T": str(round(1.1 * np.random.randn() + 5, 2))})
        return ''
        
@app.route('/reset', methods =['POST'])
def reset_data():
    if(request.method == 'POST'):
        global temp_list
        temp_list = []
        return ''

@app.route('/test', methods = ['POST','GET'])
def test():
    if(request.method == 'POST'):        
        json = request.get_json()
        imageURL = json['imageURL']
        print(imageURL)
        urllib.request.urlretrieve(imageURL,"test.png")  
        img = Image.open("test.png")

        #Predict weight loss status
        weight_loss_status = predict_weightloss_status_img(img)
        #Predict sprout status
        sprout_status = predict_sprout_status_img(img)
         #Predict disease status
        disease_status = predict_disease_status_img(img)
        return jsonify({
            "weight loss status" : str(weight_loss_status),
            "sprout status" : str(sprout_status),
            "disease status" : str(disease_status),
        })
    else:
        return """
            <h1>make a post request with imageURL<h1>
        """

@app.route('/upload', methods =['POST'])
def upload_image():
    if(request.method == 'POST'):
        global image_list
        imageFile = request.files['image']
        filename = werkzeug.utils.secure_filename(imageFile.filename)
        imageFile.save(os.path.join("static","images", filename))

        #Predict weight loss status
        weight_loss_status = predict_weightloss_status(os.path.join("static","images", filename))
        #Predict sprout status
        sprout_status = predict_sprout_status(os.path.join("static","images", filename))
         #Predict disease status
        disease_status = predict_disease_status(os.path.join("static","images", filename))
        image_list.append(filename)
        for filename in image_list:
            os.remove(os.path.join("static","images", filename))
        image_list = []
        return jsonify({
            "message": "Image uploaded successfully",
            "weight loss status" : str(weight_loss_status),
            "sprout status" : str(sprout_status),
            "disease status" : str(disease_status),
        })

@app.route('/manage-your-stock', methods =['POST'])
def manage_your_stock():
    if(request.method == 'POST'):
        global image_list
        imageFile = request.files['image']
        filename = werkzeug.utils.secure_filename(imageFile.filename)
        imageFile.save(os.path.join("static","images", filename))

        #Manag your stock result
        result = predict_shelflife_status(os.path.join("static","images", filename))

        image_list.append(filename)
        for filename in image_list:
            os.remove(os.path.join("static","images", filename))
        image_list = []
        return jsonify({
            "message": "Image uploaded successfully",
            "result": result
        })

        
@app.route('/delete-all-images', methods =['POST'])
def delete_all_images():
    global image_list
    if(request.method == 'POST'):
        for filename in image_list:
            os.remove(os.path.join("static","images", filename))
        image_list = []
        return jsonify({"message": "Successfully deteled all images"})
        

@app.route("/")
def hello_world():    
    files = os.listdir("/app/static/images") # for heroku
    #files = os.listdir("static/images") #works on local computer
    print(os.getcwd())
    return render_template('index.html', files = files)



def predict_weightloss_status(image_path):
    # Transformer to change the heigt and width of the image
    img = Image.open(image_path)
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred

def predict_weightloss_status_img(img):
    # Transformer to change the heigt and width of the image
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred

def predict_sprout_status(image_path):
    # Transformer to change the heigt and width of the image
    img = Image.open(image_path)
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model_sprout_prediction.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred

def predict_sprout_status_img(img):
    # Transformer to change the heigt and width of the image
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model_sprout_prediction.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred
    
def predict_disease_status(image_path):
    # Transformer to change the heigt and width of the image
    img = Image.open(image_path)
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model_diseased_prediction.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred

def predict_disease_status_img(img):
    # Transformer to change the heigt and width of the image
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)
    import pickle
    # load saved model
    with open('model_diseased_prediction.pkl' , 'rb') as f:
        model_load = pickle.load(f)
    y_pred = model_load.predict(feature_vector)
    return y_pred

if __name__ == '__main__':
    app.run(debug=True)

