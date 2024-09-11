import os
from PIL import Image
import matplotlib.pyplot as plt
from decimal import *
from gmssl import sm3
import json
import binascii
from math import *


#######################这是主程序，运行即可加密


def str_to_hexStr(string: str) -> str:
    """
    这是将16进制字符串变成Decimal类型的函数
    :param string:
    :return: string
    """
    str_bin = string.encode('utf-8')
    return Decimal(binascii.hexlify(str_bin).decode('utf-8'))


# 定义图片文件夹路径
folder_path = 'colorPhoto'

# 获取文件夹中的所有文件
files = os.listdir(folder_path)

# 过滤出所有图片文件（假设是JPG或PNG格式）
image_files = [file for file in files if file.endswith(('jpg', 'jpeg', 'png'))]


# 定义一个函数来显示图片及其RGB范围
def gets(begin: int, k) -> float:
    """
    这个函数的作用是计算8次异或
    :param begin:
    :param k:
    :return: float
    """
    temp = k[begin]
    for i in range(7):
        temp ^= k[i + 1]
    return temp / 256


def generate_logistic(sm3bits: str, img: Image):
    """
    这个函数的作用是根据生成的sm3加密后的字符串生成相应的logistic混沌组序列，数量依据像素值而定
    :param sm3bits:
    :param img:
    :return:
    """
    # print(type(str_to_hexStr(sm3bits)))
    H = sm3bits
    k = list()
    print(H)
    for i in range(64):
        if i % 2 != 0:
            continue
        k.append(int(str_to_hexStr(H[i] + H[i + 1])))
    print(k)

    s1 = gets(0, k)
    s2 = gets(8, k)
    s3 = gets(16, k)
    s4 = gets(24, k)
    s5 = s4 * 256
    x0 = (s1 + s5) / 256
    y0 = (s2 + s5) / 256
    a = (s3 + s5) / 256
    print(x0, y0, a)
    xt = x0
    yt = y0
    for i in range(500):
        xt = (sin(pi * (4 * a * xt * (1 - xt)) + sin(pi * yt))) % 1
        yt = (sin(pi * (4 * a * yt * (1 - yt)) + sin(pi * xt))) % 1
    print(xt, yt)
    xs = list()
    ys = list()

    column = list()
    row = list()
    print(img.size[0])
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            yt = (sin(pi * (4 * a * yt * (1 - yt)) + sin(pi * xt))) % 1
            tem = list()
            tem.append(yt)
            row.append(tem)
        ys.append(row)
        row = list()
    for i in range(img.size[1]):
        for j in range(img.size[0]):
            xt = (sin(pi * (4 * a * xt * (1 - xt)) + sin(pi * yt))) % 1
            tem = list()
            tem.append(xt)
            column.append(tem)
        xs.append(column)
        column = list()

    result = list()
    result.append(xs)
    result.append(ys)
    return result


def make_matrix(res, img: Image):
    """
    这个函数是根据之前生成的混沌序列生成对应的x盒，y盒，方便接下来的对应操作
    :param res:
    :param img:
    :return:
    """
    # x盒子，y盒子
    for i in res[0]:
        j = list()
        j = i.copy()
        j.sort()
        for x in range(img.size[1]):
            for y in range(img.size[1]):
                if i[x] == j[y]:
                    i[x][0] = y + 1
    for i in res[1]:
        j = list()
        j = i.copy()
        j.sort()
        for x in range(img.size[0]):
            for y in range(img.size[0]):
                if i[x] == j[y]:
                    i[x][0] = y + 1
    con = 1
    for i in res[0]:
        for x in i:
            x.append(con)
        con += 1
    con = 1
    for i in res[1]:
        for x in i:
            x.append(con)
        con += 1

    return res


def make_chaos(res, img: Image):
    """
    这个函数是根据x盒子，y盒子生成对应的坐标盒子，将arnold加密处理过的图片进行置乱处理
    :param res:
    :param img:
    :return:
    """
    enImg = Image.new(mode="RGB", size=img.size)
    result = list()
    msg = list()
    con = 0
    for pixel in img.getdata():
        x = con // img.size[0]
        y = con % img.size[0]
        for a in range(img.size[0]):
            for b in range(img.size[1]):
                if res[0][y][x] == res[1][b][a]:
                    enImg.load()[a, b] = img.load()[x, y]

                    msg.append(a)
                    msg.append(b)
                    msg.append(con + 1)
        result.append(msg)
        msg = list()
        con += 1

    enImg.save("colorPhoto/1.png")
    return result


def make_diffusion(T1, res2, img):
    """
    这个函数是打算进行扩散操作的，但仍有问题尚未解决，便到此为止
    :param T1:
    :param res2:
    :param img:
    :return:
    """
    global k
    T = list()
    for i in range(img.size[0]):
        row = list()
        for j in range(img.size[1]):
            for k in T1:
                if k[0] == i and k[1] == j:
                    row.append(k[2])
        T.append(row)
        row = list()

    Td = list()
    for x in range(img.size[1]):
        column = list()
        for i in T:
            column.append(i[x])
        Td.append(column)

    Ts = list()
    for i in res2[0]:
        for j in i:
            for k in j:
                k *= (2 ** 32)

    tem = list()
    for a in range(img.size[0]):
        for b in range(img.size[1]):
            tem.append((T[a][b] + Td[a][b] + res2[0][a][b][0]) % 256)
    print(tem)


def display_image_and_rgb_range(image_path):
    # 打开图片
    img = Image.open(image_path)

    # 显示图片
    plt.imshow(img)
    plt.axis('off')  # 关闭坐标轴
    plt.show()

    # 获取图片数据
    img_data = img.getdata()
    print(img.size)

    # 获取RGB范围
    min_rgb = [255, 255, 255]
    max_rgb = [0, 0, 0]

    Rs = Decimal(0)
    Gs = Decimal(0)
    Bs = Decimal(0)
    con = 0
    for pixel in img_data:
        if con <= 10:
            for i in range(3):
                if i == 0:
                    Rs *= 256
                    Rs += pixel[i]
                elif i == 1:
                    Gs *= 256
                    Gs += pixel[i]
                elif i == 2:
                    Bs *= 256
                    Bs += pixel[i]
            con += 1
    # 只考虑RGB三个通道
    # if pixel[i] < min_rgb[i]:
    #    min_rgb[i] = pixel[i]
    # if pixel[i] > max_rgb[i]:
    #    max_rgb[i] = pixel[i]

    print(f"Image: {os.path.basename(image_path)}")
    print("Rs = ", Rs.to_eng_string())
    print("Gs = ", Gs.to_eng_string())
    print("Bs = ", Bs.to_eng_string())

    body = Rs.to_eng_string()
    body_str = json.dumps(body)
    # sms3
    print(body_str)
    msg_list1 = [i for i in bytes(body_str.encode('UTF-8'))]
    print(msg_list1)
    digest1 = sm3.sm3_hash(msg_list1)

    body2 = Gs.to_eng_string()
    body_str2 = json.dumps(body2)
    # sms3
    print(body_str2)
    msg_list2 = [i for i in bytes(body_str2.encode('UTF-8'))]
    print(msg_list2)
    digest2 = sm3.sm3_hash(msg_list2)

    body3 = Bs.to_eng_string()
    body3_str = json.dumps(body3)
    # sms3
    print(body3_str)
    msg_list3 = [i for i in bytes(body3_str.encode('UTF-8'))]
    print(msg_list3)
    digest3 = sm3.sm3_hash(msg_list3)
    print(type(digest3))
    print("加密后：", digest1)
    print("加密后：", digest2)
    print("加密后：", digest3)
    res1 = generate_logistic(digest1, img)

    res1 = make_matrix(res1, img)

    T1 = make_chaos(res1, img)

    res2 = generate_logistic(digest2, img)

    res2 = make_diffusion(T1, res2, img)


# 遍历所有图片文件并显示图片及其RGB范围
for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    display_image_and_rgb_range(image_path)
