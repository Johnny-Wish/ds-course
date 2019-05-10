import numpy as np
import keras.backend as K
from keras.datasets.fashion_mnist import load_data
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Activation, Flatten
from keras.optimizers import Adam
from sklearn.preprocessing import OneHotEncoder


def get_fashion_mnist(preprocess=True, normalise=True):
    training_set, testing_set = load_data()
    train_features, train_labels = training_set
    test_features, test_labels = testing_set

    if normalise:  # normalise values in [0, 1] to avoid non-convergence
        train_features = train_features / 255.0
        test_features = test_features / 255.0

    if preprocess:
        encoder = OneHotEncoder()
        train_features = np.reshape(train_features, train_features.shape + (1,))
        train_labels = encoder.fit_transform(train_labels.reshape(-1, 1))
        test_features = np.reshape(test_features, test_features.shape + (1,))
        test_labels = encoder.fit_transform(test_labels.reshape(-1, 1))

    return train_features, train_labels, test_features, test_labels


def get_model(channels, height, width, labels, activation="relu"):
    model = Sequential()
    if K.image_data_format() == "channels_first":
        input_shape = (channels, height, width)
    else:
        input_shape = (height, width, channels)

    model.add(Conv2D(20, 5, padding="same", input_shape=input_shape))
    model.add(Activation(activation))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2,)))

    model.add(Conv2D(50, 5, padding="same"))
    model.add(Activation(activation))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

    model.add(Flatten())
    model.add(Dense(500))
    model.add(Activation(activation))

    model.add(Dense(labels))
    model.add(Activation("softmax"))

    return model


if __name__ == '__main__':
    train_features, train_labels, test_features, test_labels = get_fashion_mnist()
    print("features for training, shape =", train_features.shape)
    print("labels  for training, shape =", train_labels.shape)
    print("features for testing, shape =", test_features.shape)
    print("labels for testing sbape =", test_labels.shape)

    model = get_model(channels=1, height=28, width=28, labels=10, activation="relu")
    optimizer = Adam()
    print("using optimizer {}".format(optimizer))
    model.compile(optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

    # train and validate the model
    model.fit(x=train_features, y=train_labels, batch_size=64, epochs=3, validation_split=0.3, shuffle=False)

    # test the model
    scores = model.evaluate(x=test_features, y=test_labels)
    print("TESTING: cross-entropy = {}, top-1-accuracy={}".format(*scores))
