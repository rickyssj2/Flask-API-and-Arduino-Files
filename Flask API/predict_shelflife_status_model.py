import pickle
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from skimage.feature import hog
# load saved model
with open("multiclass_classification.pkl" , "rb") as f:
    model_load = pickle.load(f)




def number_to_string(y_pred):
    match int(y_pred):
        case 0:
            return "0-1.66"
        case 1:
            return "1.66-3.32"
        case 2:
            return "3.32-4.98"
        case 3:
            return ">10"
        case 4:
            return "4.98-6.64"
        case 5:
            return "6.64-8.3"
        case 6:
            return "8.3-9.96"


def transpiration_rate(T, rh):
    k=1.0029
    A=-5.4661
    B=-1.5934
    tr = k*np.exp(A*(1/(T + 273.15) - 0.0033162)/0.000566542)*np.exp(B*((rh/100)-0.34)/0.56)*4.351 + 0.358
    return round(tr,2)


def calculate_remaining_shelflife(current_weightloss_percentage, tr):
    tr = tr/1000
    return round((10 - current_weightloss_percentage)/(100*tr), 0)

def shelf_life_util(upper_limit, lower_limit, tr_ambient, tr_cold):
    shelf_life = {
    "ambient":{
                "upper_limit":calculate_remaining_shelflife(lower_limit, tr_ambient),
                "lower_limit":calculate_remaining_shelflife(upper_limit, tr_ambient)
            },
    "cold":{
            "upper_limit":calculate_remaining_shelflife(lower_limit, tr_cold),
            "lower_limit":calculate_remaining_shelflife(upper_limit, tr_cold)
        },
    }
    return shelf_life

def predict_shelflife_status(image_path):
    # Reading and applying the transform in the image
    img = Image.open(image_path)
    img = img.resize((128,128))
    img = np.array(img)

    # Extracting the feature vectors
    feature_vector, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                        cells_per_block=(2, 2), visualize=True, multichannel=True)

    feature_vector = np.array(feature_vector)
    feature_vector = feature_vector.reshape(1,-1)

    y_pred = model_load.predict(feature_vector)
    CW = number_to_string(y_pred)
    tr_ambient = transpiration_rate(22, 50)
    tr_cold = transpiration_rate(10, 35)
    if CW == "0-1.66":
        shelf_life = shelf_life_util(1.66, 0, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    elif CW == "1.66-3.32":
        shelf_life = shelf_life_util(3.32, 1.66, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    elif CW == "3.32-4.98":
        shelf_life = shelf_life_util(4.98, 3.32, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    elif CW == "4.98-6.64":
        shelf_life = shelf_life_util(6.64, 4.98, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    elif CW == "6.64-8.3":
        shelf_life = shelf_life_util(8.3, 6.64, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    elif CW == "8.3-9.96":
        shelf_life = shelf_life_util(9.96, 8.3, tr_ambient, tr_cold)
        shelf_life["health"] = True
        return shelf_life
    else:
        shelf_life = {
    "ambient":{
                "upper_limit":0,
                "lower_limit":0
            },
    "cold":{
            "upper_limit":0,
            "lower_limit":0
        },
    }
        shelf_life["health"] = False
        return shelf_life