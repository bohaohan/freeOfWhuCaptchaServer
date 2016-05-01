__author__ = 'bohaohan'
from keras.layers import Convolution2D, BatchNormalization, Activation, MaxPooling2D, Flatten, Dense
from keras.models import Sequential
from keras.optimizers import SGD
import numpy as np

class CaptchaNew(object):
    cha = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a',
       'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
       'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
       'x', 'y', 'z']
    model = self.get_model()
    def __init__(self):
        pass

    def get_model(self):
        classes = 36
        # data = np.empty((57218, 1, 24, 24), dtype="float32")
        model = Sequential()
        model.add(Convolution2D(4, 5, 5, border_mode='valid', input_shape=(1, 24, 24)))
        model.add(BatchNormalization())
        model.add(Activation('relu'))

        model.add(Convolution2D(8, 3, 3, border_mode='valid'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Convolution2D(16, 3, 3, border_mode='valid'))
        model.add(BatchNormalization())
        model.add(Activation('relu'))
        # model.add(Dropout(0.5))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(128, init='normal'))
        model.add(BatchNormalization())
        model.add(Activation('tanh'))
        model.add(Dense(classes, init='normal'))
        model.add(Activation('softmax'))
        sgd = SGD(l2=0.0, lr=0.05, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, class_mode="categorical")
        model.load_weights("tmp/weights.11-0.05.h5")
        return model

    def get_res(self, img):
        # # img.show()
        img = np.array(img)
        from skimage import color
        img_hsv = color.rgb2hsv(img)
        h = img_hsv[:, :, 0]
        s = img_hsv[:, :, 1]
        v = img_hsv[:, :, 2]
        img = 255 - h / 100 - s / 1 + v / 8 - 255
        img *= 255

        img = np.array(img)

        origin = img
        from skimage.filters import threshold_otsu
        # print img
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i][j] > -100:
                    img[i][j] = 255
                else:
                    # print img[i][j]
                    img[i][j] = 0


        new_img = img[:, 28:108]

        res = []
        for i in range(0, 5):
            crop_img = new_img[6:, i * 13: i * 13 + 24]
            res.append(crop_img)
        return res


    def predict(self, img):
        result = ""

        try:
            res = self.get_res(img)
            for i in res:
                result += str(self.cha[self.model.predict_classes(i.reshape(1, 1, 24, 24))])
            return result
        except:
            pass

if __name__ == "__main__":
    from PIL import Image
    img = Image.open("testdata/GenImg1.jpeg")
    c = CaptchaNew()
    print c.predict(img)