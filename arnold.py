import cv2
import numpy as np
from matplotlib import pyplot as plt


def arnold(img, shuffle_times, a, b):
    r, c, d = img.shape
    p = np.zeros(img.shape, np.uint8)
    for s in range(shuffle_times):
        for i in range(r):
            for j in range(c):
                x = (i + b * j) % r
                y = (a * i + (a * b + 1) * j) % c
                p[x, y, :] = img[i, j, :]
        img = np.copy(p)
        img
    return p


def de_arnold(img, shuffle_times, a, b):
    r, c, d = img.shape
    p = np.zeros(img.shape, np.uint8)
    for s in range(shuffle_times):
        for i in range(r):
            for j in range(c):
                x = ((a * b + 1) * i - b * j) % r
                y = (- a * i + j) % c
                p[x, y, :] = img[i, j, :]
        img = np.copy(p)

    return p


Img_path = 'colorPhoto/test.jpg'
Img = cv2.imread(Img_path)
Img = Img[:, :, [2, 1, 0]]

Img_arnold = arnold(Img, 5, 2, 3)
cv2.imwrite("colorPhoto/2.png", Img_arnold)
Img_inverse_arnold = de_arnold(Img_arnold, 5, 2, 3)

plt.subplot(1, 2, 1)
plt.title("arnold", fontsize=12, loc="center")
plt.axis('off')
plt.imshow(Img_arnold)

plt.subplot(1, 2, 2)
plt.title("de_arnold", fontsize=12, loc="center")
plt.axis('off')
plt.imshow(Img_inverse_arnold)
plt.show()
