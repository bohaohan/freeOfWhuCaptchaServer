# -*- coding: utf-8 -*-

import logging
import json
from StringIO import StringIO

import requests
from fann2 import libfann
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile

from eduLogin.captcha.exceptions import CaptchaException, CaptchaDownloadError, CaptchaParamError
from eduLogin.captcha.utils import (
    COLOR_RGB_BLACK, COLOR_RGB_WHITE, COLOR_RGBA_BLACK, COLOR_RGBA_WHITE,
    BORDER_LEFT, BORDER_TOP, BORDER_RIGHT, BORDER_BOTTOM,
)

logger = logging.getLogger(__name__)


class Captcha(object):
    """
    验证码类
    """
    def __init__(self, image, manual=False, system_type='education'):
        """
        初始化
        :param image: 验证码图片文件 Image Object
        :param manual: 是否人工验证, 默认为False, 采用机器验证
        :param system_type: 验证码系统类型('education': 教务系统, 'sport': 体育系统)
        """
        self._manual = manual
        self._system_type = system_type
        if manual:
            if isinstance(image, StringIO):
                self._image = image
            else:
                raise CaptchaParamError('captcha image file is unavailable')
        else:
            if isinstance(image, file) or isinstance(image, str) or isinstance(image, unicode):
                self._image = Image.open(image)
            elif isinstance(image, JpegImageFile):
                self._image = image
            else:
                raise CaptchaParamError('captcha image file is unavailable')

    def result(self):
        """
        获取验证码识别结果
        :return: str
        """
        if self._manual:
            return self._human_recognization()

        neural = libfann.neural_net()
        libfann.neural_net.create_from_file(neural, '/Users/bohaohan/development/eduLogin/eduLogin/captcha/data/training.data')

        self._binaryzation()
        self._clear_noise()
        image_list = self._cut_images()
        captcha = ''
        for image in image_list:
            image = self._rotate_image(image)
            image = self._resize_to_norm(image)
            string = self._captcha_to_string(image)
            arr = []
            for x in string:
                arr.append(int(x))
            neural_result = libfann.neural_net.run(neural, arr)
            max_element = 0
            max_pos = 0
            for index, item in enumerate(neural_result):
                if item > max_element:
                    max_element = item
                    max_pos = index

            if max_pos in range(0, 10):
                captcha += str(max_pos)
            else:
                captcha += chr(max_pos - 10 + 97)
        return captcha

    def _get_black_border(self, image):
        """
        获取指定图像的内容边界坐标
        :param image: 图像 Image Object
        :return: 图像内容边界坐标tuple (left, top, right, bottom)
        """
        width, height = image.size
        max_x = max_y = 0
        min_x = width - 1
        min_y = height - 1
        for y in range(height):
            for x in range(width):
                if image.getpixel((x, y)) == COLOR_RGBA_BLACK:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        return min_x, min_y, max_x, max_y

    def _binaryzation(self):
        """
        将图片进行二值化
        """
        width, height = self._image.size
        for y in range(height):
            for x in range(width):
                r, g, b = self._image.getpixel((x, y))
                if g <= 100 and b <= 100:
                    self._image.putpixel((x, y), COLOR_RGB_BLACK)
                else:
                    self._image.putpixel((x, y), COLOR_RGB_WHITE)

    def _clear_noise_fill_color(self, x, y, now, count, used, color):
        """
        清除噪点染色过程
        :param x: 坐标X
        :param y: 坐标Y
        :param now: 当前颜色
        :param count: 颜色计数列表
        :param used: 是否染色过的标记列表
        :param color: 颜色列表
        """
        width, height = self._image.size
        used[x][y] = True
        color[x][y] = now
        count[now] += 1
        if x > 0 and not used[x-1][y] and self._image.getpixel((x - 1, y)) == COLOR_RGB_BLACK:
            self._clear_noise_fill_color(x - 1, y, now, count, used, color)
        if y > 0 and not used[x][y-1] and self._image.getpixel((x, y - 1)) == COLOR_RGB_BLACK:
            self._clear_noise_fill_color(x, y - 1, now, count, used, color)
        if x < width - 1 and not used[x+1][y] and self._image.getpixel((x + 1, y)) == COLOR_RGB_BLACK:
            self._clear_noise_fill_color(x + 1, y, now, count, used, color)
        if y < height - 1 and not used[x][y+1] and self._image.getpixel((x, y + 1)) == COLOR_RGB_BLACK:
            self._clear_noise_fill_color(x, y + 1, now, count, used, color)

    def _clear_noise(self):
        """
        清除图片噪点
        """
        width, height = self._image.size
        color = [[0 for y in range(0, height)] for x in range(0, width)]
        count = [0, ]
        used = [[False for y in range(0, height)] for x in range(0, width)]
        now = 0
        final_color = []
        for y in range(height):
            for x in range(width):
                if self._image.getpixel((x, y)) == COLOR_RGB_BLACK and color[x][y] == 0:
                    now += 1
                    count.append(0)
                    self._clear_noise_fill_color(x, y, now, count, used, color)
                    if count[now] >= 5:  # 如果一个区域块大于等于5个像素点，则认为该区块有实际意义
                        final_color.append(now)

        for y in range(height):
            for x in range(width):
                if color[x][y] not in final_color:
                    self._image.putpixel((x, y), COLOR_RGB_WHITE)

    def _cut_images(self):
        """
        切割图像为单个字符块
        :return: list对象, 每个元素为一个单独字符的Image Object
        """
        width, height = self._image.size

        # 获取图片切割线
        origin_crop_list = []
        crop_list = []
        for x in range(width):
            zero_flag = True
            for y in range(height):
                if self._image.getpixel((x, y)) == COLOR_RGB_BLACK:
                    zero_flag = False
                    break
            if zero_flag:
                origin_crop_list.append(x)

        for index, x in enumerate(origin_crop_list):
            if index < len(origin_crop_list) - 1 and x + 1 == origin_crop_list[index+1]:
                continue
            crop_list.append(x)
        for index, x in enumerate(origin_crop_list):
            if index > 0 and x - 1 == origin_crop_list[index-1]:
                continue
            crop_list.append(x)
        crop_list = sorted(crop_list)
        del crop_list[0]
        del crop_list[-1]

        # 切割图片
        croped_image = []
        for index, x in enumerate(crop_list):
            if index % 2 == 1:
                continue

            begin_row = 0
            end_row = height - 1
            for row in range(height):
                flag = True
                for col in range(x, crop_list[index+1] + 1):
                    if self._image.getpixel((col, row)) == COLOR_RGB_BLACK:
                        flag = False
                        break
                if not flag:
                    begin_row = row
                    break
            for row in reversed(range(height)):
                flag = True
                for col in range(x, crop_list[index+1] + 1):
                    if self._image.getpixel((col, row)) == COLOR_RGB_BLACK:
                        flag = False
                        break
                if not flag:
                    end_row = row
                    break

            croped_image.append(self._image.crop((x, begin_row, crop_list[index+1], end_row + 1)))

        return croped_image

    def _rotate_image(self, image):
        """
        将单个字符图片旋转到合适角度 (投影至X轴长度最小)
        :return: 旋转后的图像 (RGB)
        """
        image = image.convert('RGBA')
        optimisim_image = image
        for angle in range(-30, 31):
            image_copy = image.rotate(angle, expand=True)
            fff = Image.new('RGBA', image_copy.size, (255, )*4)
            out = Image.composite(image_copy, fff, image_copy)

            border_out = self._get_black_border(out)
            border_optimisim = self._get_black_border(optimisim_image)
            if border_out[BORDER_RIGHT] - border_out[BORDER_LEFT] + 1 < border_optimisim[BORDER_RIGHT] - border_optimisim[BORDER_LEFT] + 1:
                optimisim_image = out

        border = self._get_black_border(optimisim_image)
        optimisim_image = optimisim_image.crop((
            border[BORDER_LEFT],
            border[BORDER_TOP],
            border[BORDER_RIGHT],
            border[BORDER_BOTTOM]
        ))
        optimisim_image = optimisim_image.convert('RGB')
        return optimisim_image

    def _resize_to_norm(self, image):
        """
        将单个图像缩放至32x32像素标准图像
        :param image: 图像 (RGB)
        :return: 缩放后的Image Object
        """
        if image.size[0] > 32 or image.size[1] > 32:
            image = image.resize((32, 32))
        width, height = image.size
        new_image = Image.new('RGB', (32, 32), COLOR_RGB_WHITE)
        offset = ((32 - width) / 2, (32 - height) / 2)
        new_image.paste(image, offset)
        return new_image

    def _captcha_to_string(self, image):
        """
        将验证码转换为数字编码 (2*2为一格，范围0-4)
        :param image: 图像
        :return: 数字编码字符串
        """
        data = []
        for x in range(0, 16):
            data.append([])
            for y in range(0, 16):
                data[-1].append(0)

        for y in range(0, 16):
            for x in range(0, 16):
                count = 0
                if image.getpixel((x * 2, y * 2)) == COLOR_RGB_BLACK:
                    count += 1
                if image.getpixel((x * 2 + 1, y * 2)) == COLOR_RGB_BLACK:
                    count += 1
                if image.getpixel((x * 2, y * 2 + 1)) == COLOR_RGB_BLACK:
                    count += 1
                if image.getpixel((x * 2 + 1, y * 2 + 1)) == COLOR_RGB_BLACK:
                    count += 1
                data[x][y] = count

        string = ''
        for y in range(0, 16):
            for x in range(0, 16):
                string += str(data[x][y])
        return string

    def _human_recognization(self):
        """
        人工识别当前验证码
        :return: 识别结果 str
        """
        return '2333'