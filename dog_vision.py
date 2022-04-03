# -*- coding: utf-8 -*-
"""dog-vision.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WqoAMTbWqi1uyOefPZoYfn60p4bH9adX
"""

#!unzip "/content/drive/MyDrive/dog-vision/dog-breed-identification.zip" -d "drive/MyDrive/dog-vision/"

"""**Dog-Vision** is deep learning model made using tensorflow to predict the brees of the dog using its image .

**Evaluation** we will evaluate our model on its prediction probability .

It is multi-class classification model with 120 different classes .

"""

import tensorflow as tf 
import tensorflow_hub as hub
import pandas as  pd
import numpy as np
import matplotlib.pyplot as plt
print(" TensorFlow v : ",tf.__version__)
print(" TensorFlow v : ",hub.__version__)

# Check for GPU availibity
print(" GPU : "," available ! " if tf.config.list_physical_devices("GPU") else " not available ! ")

labels = pd.read_csv("/content/drive/MyDrive/dog-vision/labels.csv")
labels.head()

labels.shape

ax,fig = plt.subplots(figsize=(20,7))
ax = labels.breed.value_counts().plot(kind='bar',label='No. of images');
ax.axhline(np.mean(labels.breed.value_counts()),color='salmon',label="Mean");
ax.set(title="Number of IMAGES of each Dog")
ax.legend();

from IPython.display import Image
Image("/content/drive/MyDrive/dog-vision/train/001513dfcb2ffafc82cccf4d8bbaba97.jpg")

# Creating a new column for the path of each image 
labels["path"] = "/content/drive/MyDrive/dog-vision/train/"+labels.id+".jpg"

unique_breeds = labels.breed.unique()
unique_breeds

numeric_labels = np.array(pd.get_dummies(labels.breed))

# Splitting data into Labels and features 
X = np.array(labels.path) #labels
Y = numeric_labels #features

NUM_IMGS = 10000 #@param { type:"slider", min:1000, max:10000, step:1000 }

from sklearn.model_selection import train_test_split
x_train,x_val,y_train,y_val = train_test_split(X[:NUM_IMGS],Y[:NUM_IMGS],test_size=0.2,random_state=42)
x_train.shape,y_train.shape

# Reading an image using matplotlib 
from matplotlib.pyplot import imread
image = imread(labels.path[42])
image.shape

# Function to convert an image into tensor
IMG_SIZE = 224
def process_image(path,img_size=IMG_SIZE):
  '''
  converts an oimage into tensor 
  '''
  image = tf.io.read_file(path)
  image = tf.image.decode_jpeg(image,channels=3)
  image = tf.image.convert_image_dtype(image, tf.float32)
  image = tf.image.resize(image, size=[img_size,img_size])
  return image

image = process_image(labels.path[42])
image

# Function to create a tuple of tensors
def get_tuple(path, label):
  tup = (process_image(path),label)
  return tup

t = get_tuple(X[42],tf.constant(Y[42]))
t

# Turning data train and valid into batches
BATCH_SIZE = 32
def batch(x,y=None,batch_size=BATCH_SIZE,valid_data=False,test_data=False):
  # Validation set
  if valid_data:
    print(" Creating validation data batches.....")
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x),
                                                tf.constant(y)))
    data_batch = data.map(get_tuple).batch(batch_size)
    return data_batch
  # Testing set
  elif test_data:
    print(" Creating testing data batches.....")
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x)))
    data_batch = data.map(process_image).batch(batch_size)
    return data_batch
  # Training set
  else :
    print(" Creating training data batches.....")
    data = tf.data.Dataset.from_tensor_slices((tf.constant(x),
                                               tf.constant(y)))
    data = data.shuffle(buffer_size=len(x))
    data_batch = data.map(get_tuple).batch(batch_size)
    return data_batch

train_data = batch(x_train,y_train)
val_data = batch(x_val,y_val,valid_data=True)

train_data.element_spec,val_data.element_spec

"""Visualizing our batches"""

# Creating a visualizing function to see 25 images from our data set
def show_images(images,labels):
  plt.figure(figsize=(10,10))
  for i in range(25):
    ax = plt.subplot(5,5,i+1)
    plt.imshow(images[i])
    plt.title(unique_breeds[labels[i].argmax()])
    plt.axis("off")

train_img,train_labels = next(train_data.as_numpy_iterator())
show_images(train_img,train_labels)

val_img,val_labels = next(val_data.as_numpy_iterator())
show_images(val_img,val_labels)

# Defining the inout size, output size and the url ofr the model 
INPUT_SIZE = [None,IMG_SIZE,IMG_SIZE,3]
OUTPUT_SIZE = len(unique_breeds)
URL = "https://tfhub.dev/google/imagenet/mobilenet_v3_large_100_224/classification/5"

def build_model(input_size=INPUT_SIZE,output_size=OUTPUT_SIZE,url=URL):
   print(" Building the model from : ",url)
   model = tf.keras.Sequential([
                                hub.KerasLayer(URL), # Layer 1 
                                tf.keras.layers.Dense(activation="softmax",units=OUTPUT_SIZE) # Layer 2
   ])
   model.compile(
   loss = tf.keras.losses.CategoricalCrossentropy(),
   optimizer = tf.keras.optimizers.Adam(),   
   metrics=['accuracy'] 
   )
   model.build(INPUT_SIZE)
   return model

model = build_model()
 model.summary()

# Creating a callback function
import datetime
import os
def create_tensorboard_callback():
  logdir = os.path.join("/content/drive/MyDrive/dog-vision/logs",
                        datetime.datetime.now().strftime("%d%m%Y-%H%M%S"))
  return tf.keras.callbacks.TensorBoard(logdir)

early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy',
                                                  patience=3)

EPOCHS = 100 #@param {type:'slider',min:10,max:100,step:10}

# Check for GPU availibity
print(" GPU : "," available ! " if tf.config.list_physical_devices("GPU") else " not available ! ")

def train_model():
  model = build_model()
  tensorboard = create_tensorboard_callback()
  model.fit(x=train_data,
            epochs=EPOCHS,
            validation_data=val_data,
            validation_freq=1,
            callbacks=[tensorboard,early_stopping])
  return model

model = train_model()

# Commented out IPython magic to ensure Python compatibility.
# %load_ext tensorboard
# %tensorboard --logdir /content/drive/MyDrive/dog-vision/logs

import pickle 
pickle.dump(model,open("/content/drive/MyDrive/dog-vision/dog-vision.pkl",'wb'))
model = pickle.load(open("/content/drive/MyDrive/dog-vision/dog-vision.pkl",'rb'))

# Function to show the predictions 
predictions = model.predict(val_data,verbose=1)

show_results(15)

def unbatchify(data):
  labels_ = []
  images_ = []
  for image,label in data.unbatch().as_numpy_iterator():
    images_.append(image)
    labels_.append(label)
  return labels_,images_

# Function to show predictions and actual labels 
labels,images = unbatchify(val_data)
def show_results(n,true_data=val_data):
  print(" For index ",n)
  print(" Probability prediction : ",np.max(predictions[n])*100)
  print(" Predicted Breed :",unique_breeds[np.argmax(predictions[n])])
  print(" Actual Breed :",unique_breeds[np.argmax(labels[n])])

def plot_top5(n):
  top5_index = predictions[n].argsort()[-5:][::-1]
  top5_breeds,top5_probs,true_label = unique_breeds[top5_index],predictions[n][top5_index],unique_breeds[np.argmax(predictions[n])]
  fig, ax = plt.subplots(figsize=(5,5))
  ax = plt.bar(height=top5_probs,x=top5_breeds,color='salmon')
  if true_label in top5_breeds:
    ax[np.argmax(top5_breeds==true_label)].set_color("lightgreen")
  plt.xticks(top5_breeds,
            rotation='vertical')
  plt.title('Top 5 prediction made by the model');
  plt.ylabel('Probability');

plot_top5(145)

