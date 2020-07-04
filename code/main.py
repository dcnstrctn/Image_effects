# -*- coding: utf-8 -*-
import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import base64
from icon import img

root = Tk()
tmp = open("tmp.ico", "wb+")
tmp.write(base64.b64decode(img))
tmp.close()
root.title("图像浮雕/油画")
root.iconbitmap("tmp.ico")
os.remove("tmp.ico")

# root = Tk()
# root.iconbitmap(".\\PS.ico")

v = IntVar()
v.set(1)  # 默认选第一个

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

frmTop = Frame(root)
frmTop.pack(side='top')
frmBottom = Frame(root)
frmBottom.pack(side='bottom')
frmLeftTop = Frame(frmTop)
frmLeftTop.pack(side='left')
frmRightTop = Frame(frmTop)
frmRightTop.pack(side='right')

canvas1 = Canvas(frmLeftTop, width=300, height=300, bg="white")
canvas1.pack()
canvas2 = Canvas(frmRightTop, width=300, height=300, bg="white")
canvas2.pack()

r1 = Radiobutton(frmBottom, text="浮雕效果", value=1, variable=v)
r1.pack(side="top")
r2 = Radiobutton(frmBottom, text="油画效果", value=2, variable=v)
r2.pack(side="bottom")

contentPath = ""
image = ""


def contentClk():
    global canvas1
    global contentPath
    contentPath = filedialog.askopenfilename(parent=root, title='选择图片...')
    im = Image.open(contentPath)
    im = im.resize((300, 300), Image.ANTIALIAS)
    filename = ImageTk.PhotoImage(im)
    canvas1.image = filename  # <--- keep reference of your image
    canvas1.create_image(0, 0, anchor='nw', image=filename)


def emboss(path):
    # 读取原始图像
    img = cv2.imread(path)
    # 获取图像的高度和宽度
    height, width = img.shape[:2]
    # 图像灰度处理
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 创建目标图像
    dst = np.zeros((height, width, 1), np.uint8)
    # 浮雕特效算法：newPixel = grayCurrentPixel - grayNextPixel + 150
    for i in range(0, height):
        for j in range(0, width - 1):
            grayCurrentPixel = int(gray[i, j])
            grayNextPixel = int(gray[i, j + 1])
            newPixel = grayCurrentPixel - grayNextPixel + 150
            if newPixel > 255:
                newPixel = 255
            if newPixel < 0:
                newPixel = 0
            dst[i, j] = newPixel

    dst = Image.fromarray(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))
    return dst


def oilPaint(path):
    img = cv2.imread(path)
    imgInfo = img.shape
    height = imgInfo[0]
    width = imgInfo[1]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst = np.zeros((height, width, 3), np.uint8)
    pixel_class = 4
    section = int(256 / pixel_class)
    # 用两层for循环来遍历图片的每个数据
    for i in range(3, height - 3):
        for j in range(3, width - 3):
            # 当前程序中定义的灰度等级是4个
            # 定义一个数组来装载这4个等级内的像素个数
            array1 = np.zeros(pixel_class, np.uint8)
            # 当前程序中定义的小方块是6x6的
            for m in range(-3, 3):
                for n in range(-3, 3):
                    # p1是对该像素点等级段的划分，用下标表示0-3
                    p1 = int(gray[i + m, j + n] / section)
                    # 接下来对像素等级进行计数，array1的下标代表像素等级，
                    # 值则代表处在该像素等级小方框内像素的个数
                    array1[p1] = array1[p1] + 1
            # 接下来判断在这个小方框内哪一个像素段的像素最多
            currentMax = array1[0]
            p = 0  # 这里设置一个p用来记录像素段计数最多的数组下标
            for k in range(0, pixel_class):
                if currentMax < array1[k]:
                    currentMax = array1[k]
                    p = k
            # 均值处理
            u = v = w = 0
            for m in range(-3, 3):
                for n in range(-3, 3):
                    if (p * section) <= gray[i + m, j + n] <= ((p + 1) * section):
                        (b, g, r) = img[i + m, j + n]
                        u += b
                        v += g
                        w += r
            u = int(u / array1[p])
            v = int(v / array1[p])
            w = int(w / array1[p])
            dst[i, j] = [u, v, w]

    dst = Image.fromarray(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))
    return dst


def transferClk():
    global contentPath
    if v.get() is 1:
        img = emboss(contentPath)
    else:
        img = oilPaint(contentPath)

    global image
    image = img
    # display image
    img = img.resize((300, 300), Image.ANTIALIAS)
    filename = ImageTk.PhotoImage(img)
    global canvas2
    canvas2.image = filename  # <--- keep reference of your image
    canvas2.create_image(0, 0, anchor='nw', image=filename)
    pass


def saveClk():
    filename = filedialog.asksaveasfilename(parent=root, title='另存图片为...', defaultextension=".*",
                                            filetypes=[("PNG", ".png"), ("JPEG", ".jpg"), ("BMP", ".bmp")])
    global image
    image.save(filename)


Button(frmLeftTop, text='选择原图', command=lambda: contentClk()).pack()
Button(frmRightTop, text='转换', command=lambda: transferClk()).pack(side="left")
Button(frmRightTop, text='另存为', command=lambda: saveClk()).pack()

root.mainloop()
