import os
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
from sklearn.datasets import make_classification

# Unsplash Access Key
ACCESS_KEY = "your_key_here"  # Reemplaza con tu clave de acceso

def save_pair(name, X, y):
    # X: float32 normalizado en [0,1] o tabular, y: one-hot float32
    np.savez(f"{name}.npz", x=X, y=y)
    np.save(f"{name}_data.npy", {"x": X, "y": y}, allow_pickle=True)
    print(f"Generated: {name}.npz + {name}_data.npy")

def fetch_unsplash_float(query, n=5, size=(256,256)):
    """
    Descarga n imágenes RGB de Unsplash (raw), las redimensiona a `size`
    con filtro LANCZOS, convierte a float32 en [0,1] y devuelve array (n,H,W,3).
    """
    url = "https://api.unsplash.com/search/photos"
    params = {"query": query, "page": 1, "per_page": n, "client_id": ACCESS_KEY}
    r = requests.get(url, params=params); r.raise_for_status()
    data = r.json()["results"]
    imgs = []
    for item in data:
        img_url = item["urls"]["raw"] + f"&w={size[0]*2}&h={size[1]*2}&fit=crop"
        resp = requests.get(img_url); resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        img = img.resize(size, resample=Image.LANCZOS)
        arr = np.array(img).astype(np.float32) / 255.0
        imgs.append(arr)
    return np.stack(imgs)

def make_image_classification_pair(name, query, num_classes=5):
    X = fetch_unsplash_float(query, n=num_classes, size=(256,256))
    y_int = np.arange(num_classes, dtype=np.int32)
    y = to_categorical(y_int, num_classes)
    save_pair(name, X, y)

    model = models.Sequential([
        layers.Input(shape=X.shape[1:]),
        layers.Conv2D(16, 3, activation="relu"), layers.MaxPooling2D(),
        layers.Conv2D(32, 3, activation="relu"), layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dense(num_classes, activation="softmax"),
    ])
    model.compile("adam","categorical_crossentropy",["accuracy"])
    model.fit(X, y, epochs=5, batch_size=8, verbose=1)
    model.save(f"{name}_model.h5")
    print(f"Generated: {name}_model.h5\n")

def make_mnist_pair():
    (Xtr, ytr), (Xte, yte) = mnist.load_data()
    Xtr = Xtr[...,None].astype(np.float32)/255.0
    Xte = Xte[...,None].astype(np.float32)/255.0
    ytr_cat = to_categorical(ytr, 10)
    yte_cat = to_categorical(yte, 10)
    save_pair("mnist_train", Xtr, ytr_cat)
    save_pair("mnist_test",  Xte, yte_cat)

    model = models.Sequential([
        layers.Input(shape=Xtr.shape[1:]),
        layers.Conv2D(32, 3, activation="relu"), layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(64, activation="relu"),
        layers.Dense(10, activation="softmax"),
    ])
    model.compile("adam","categorical_crossentropy",["accuracy"])
    model.fit(Xtr, ytr_cat, epochs=5, batch_size=32,
              validation_data=(Xte, yte_cat), verbose=1)
    model.save("mnist_model.h5")
    print("Generated: mnist_model.h5\n")

def make_synthetic_tabular_pair():
    # Genera 500 muestras, 10 features, 3 clases
    X, y = make_classification(
        n_samples=500, n_features=10, n_informative=5,
        n_redundant=2, n_classes=3, random_state=0
    )
    X = X.astype(np.float32)
    y_cat = to_categorical(y, 3)
    save_pair("synthetic_tabular", X, y_cat)

    # MLP sencillo
    model = models.Sequential([
        layers.Input(shape=(10,)),
        layers.Dense(32, activation="relu"),
        layers.Dense(16, activation="relu"),
        layers.Dense(3, activation="softmax"),
    ])
    model.compile("adam","categorical_crossentropy",["accuracy"])
    model.fit(X, y_cat, epochs=5, batch_size=16, verbose=1)
    model.save("synthetic_tabular_model.h5")
    print("Generated: synthetic_tabular_model.h5\n")

if __name__ == "__main__":
    # Imágenes:
    make_image_classification_pair("cars",  "car",   num_classes=5)
    make_image_classification_pair("dogs",  "dog",   num_classes=5)
    make_image_classification_pair("faces", "face",  num_classes=5)
    # MNIST:
    make_mnist_pair()
    # Tabular sintético:
    make_synthetic_tabular_pair()