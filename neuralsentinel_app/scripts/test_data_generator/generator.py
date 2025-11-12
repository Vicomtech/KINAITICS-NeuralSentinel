import os
import numpy as np
import tensorflow as tf
from sklearn.datasets import make_classification, load_iris
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.utils import to_categorical

# Function to generate a synthetic vector dataset with corresponding MLP model
def make_vector_pair():
    # Generate a synthetic dataset: 500 samples with 100 features, divided into 10 classes
    X, y = make_classification(
        n_samples=500, n_features=100, n_informative=50, n_classes=10, random_state=0
    )
    # Convert the target labels into categorical format (one-hot encoded)
    y = to_categorical(y, num_classes=10)

    # Save the dataset into an NPZ file
    np.savez("synthetic_vectors.npz", x=X, y=y)
    # Save the dataset into a single NPY file
    np.save("synthetic_vectors_data.npy", {"x": X, "y": y})

    # Define a simple Multi-Layer Perceptron (MLP) model for the classification task
    model = Sequential([ 
        Input(shape=(100,)),  # Input layer with 100 features
        Dense(64, activation="relu"),  # Dense hidden layer with 64 units and ReLU activation
        Dense(10, activation="softmax")  # Output layer with 10 units for classification (softmax for probabilities)
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the model on the synthetic data for 2 epochs
    model.fit(X, y, epochs=2, batch_size=32, verbose=0)

    # Save the trained model to a file
    model.save("vector_model.h5")
    print("Generated: synthetic_vectors.npz + synthetic_vectors_data.npy + vector_model.h5")

# Function to generate a grayscale image dataset with a corresponding CNN model
def make_gray_image_pair():
    # Generate a dataset: 500 grayscale images of size 28x28 with 1 channel, 10 classes
    X = np.random.rand(500, 28, 28, 1).astype(np.float32)
    y = np.random.randint(0, 10, size=(500,))  # Random labels between 0 and 9
    y = to_categorical(y, num_classes=10)  # Convert labels to categorical format

    # Save the grayscale image dataset into an NPZ file
    np.savez("gray_images.npz", x=X, y=y)
    # Save the grayscale image dataset into a single NPY file
    np.save("gray_images_data.npy", {"x": X, "y": y})

    # Define a small Convolutional Neural Network (CNN) model for image classification
    model = Sequential([
        Input(shape=(28,28,1)),  # Input layer for grayscale images of size 28x28x1
        Conv2D(16, 3, activation="relu"),  # Convolutional layer with 16 filters
        MaxPooling2D(),  # MaxPooling layer to reduce dimensionality
        Flatten(),  # Flatten the output of the previous layer to feed into a dense layer
        Dense(10, activation="softmax")  # Output layer for 10 classes
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the CNN model on the generated data
    model.fit(X, y, epochs=2, batch_size=32, verbose=0)

    # Save the trained model to a file
    model.save("gray_cnn.h5")
    print("Generated: gray_images.npz + gray_images_data.npy + gray_cnn.h5")

# Function to generate a color image dataset with a corresponding CNN model
def make_color_image_pair():
    # Generate a dataset: 500 color images of size 32x32 with 3 channels, 5 classes
    X = np.random.rand(500, 32, 32, 3).astype(np.float32)
    y = np.random.randint(0, 5, size=(500,))  # Random labels between 0 and 4
    y = to_categorical(y, num_classes=5)  # Convert labels to categorical format

    # Save the color image dataset into an NPZ file
    np.savez("color_images.npz", x=X, y=y)
    # Save the color image dataset into a single NPY file
    np.save("color_images_data.npy", {"x": X, "y": y})

    # Define a deeper CNN model for color image classification
    model = Sequential([
        Input(shape=(32,32,3)),  # Input layer for color images of size 32x32x3
        Conv2D(16, 3, activation="relu"),  # Convolutional layer with 16 filters
        MaxPooling2D(),  # MaxPooling layer to reduce dimensionality
        Conv2D(32, 3, activation="relu"),  # Second convolutional layer with 32 filters
        MaxPooling2D(),  # MaxPooling layer
        Flatten(),  # Flatten the output to feed into the dense layer
        Dense(5, activation="softmax")  # Output layer for 5 classes
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the CNN model on the generated color image data
    model.fit(X, y, epochs=2, batch_size=32, verbose=0)

    # Save the trained model to a file
    model.save("color_cnn.h5")
    print("Generated: color_images.npz + color_images_data.npy + color_cnn.h5")

# Function to generate the Iris dataset with a corresponding MLP model
def make_iris_pair():
    # Load the Iris dataset (150 samples, 4 features, 3 classes)
    iris = load_iris()
    X, y = iris.data, iris.target
    y = to_categorical(y, num_classes=3)  # Convert labels to categorical format

    # Save the Iris dataset into an NPZ file
    np.savez("iris.npz", x=X, y=y)
    # Save the Iris dataset into a single NPY file
    np.save("iris_data.npy", {"x": X, "y": y})

    # Define a small MLP model for Iris classification
    model = Sequential([
        Input(shape=(4,)),  # Input layer for the 4 features of the Iris dataset
        Dense(8, activation="relu"),  # Dense hidden layer with 8 units and ReLU activation
        Dense(3, activation="softmax")  # Output layer for 3 classes (Iris species)
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

    # Train the MLP model on the Iris dataset
    model.fit(X, y, epochs=5, batch_size=16, verbose=0)

    # Save the trained model to a file
    model.save("iris_model.h5")
    print("Generated: iris.npz + iris_data.npy + iris_model.h5")

# Main execution block to generate all datasets and models
if __name__ == "__main__":
    # Ensure we are in the correct folder before generating the datasets and models
    os.makedirs(".", exist_ok=True)

    # Generate each dataset-model pair
    make_vector_pair()
    make_gray_image_pair()
    make_color_image_pair()
    make_iris_pair()