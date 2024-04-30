#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math


# 本文件只允许依赖math库


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(int(y0), int(y1) + 1):
                result.append([x0, y])
            return result

        m = abs((y0 - y1) / (x0 - x1))
        if m < 1:
            if x0 > x1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            delta_y = m
            if y0 < y1:
                result.append([x0, y0])
                y_k = y0
                for x in range(int(x0) + 1, int(x1) + 1):
                    y_k += delta_y
                    result.append([x, round(y_k)])
            else:
                result.append([x1, y1])
                y_k = y1
                for x in range(int(x1) - 1, int(x0) - 1, -1):
                    y_k += delta_y
                    result.append([x, round(y_k)])
        else:
            if y0 > y1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            delta_x = 1 / m
            if x0 < x1:
                result.append([x0, y0])
                x_k = x0
                for y in range(int(y0) + 1, int(y1) + 1):
                    x_k += delta_x
                    result.append([round(x_k), y])
            else:
                result.append([x1, y1])
                x_k = x1
                for y in range(int(y1) - 1, int(y0) - 1, -1):
                    x_k += delta_x
                    result.append([round(x_k), y])
    elif algorithm == 'Bresenham':
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(int(y0), int(y1) + 1):
                result.append([x0, y])
            return result

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        if dy / dx < 1:
            if x0 > x1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            flag = 0
            if y0 > y1:
                flag = 1
            result.append([x0, y0])
            p_k = 2 * dy - dx
            y_k = y0
            for x in range(int(x0) + 1, int(x1) + 1):
                if p_k >= 0:
                    p_k += 2 * dy - 2 * dx
                    y_k += (1 if flag == 0 else -1)
                else:
                    p_k += 2 * dy
                result.append([x, y_k])
        else:
            dy, dx = dx, dy
            if y0 > y1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            flag = 0
            if x0 > x1:
                flag = 1
            result.append([x0, y0])
            p_k = 2 * dy - dx
            x_k = x0
            for y in range(int(y0) + 1, int(y1) + 1):
                if p_k >= 0:
                    p_k += 2 * dy - 2 * dx
                    x_k += (1 if flag == 0 else -1)
                else:
                    p_k += 2 * dy
                result.append([x_k, y])
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    core_x = int((x0 + x1) / 2)
    core_y = int((y0 + y1) / 2)
    a = int(abs(x0 - x1) / 2)
    b = int(abs(y0 - y1) / 2)
    a_2 = a ** 2
    b_2 = b ** 2
    x_k = 0
    y_k = b
    result.append([core_x, core_y + b])
    result.append([core_x, core_y - b])
    result.append([core_x + a, core_y])
    result.append([core_x - a, core_y])

    p_k = b_2 - a_2 * b + a_2 / 4
    while b_2 * x_k < a_2 * y_k:
        if p_k < 0:
            p_k += 2 * b_2 * x_k + 3 * b_2
        else:
            p_k += 2 * b_2 * x_k + 3 * b_2 - 2 * a_2 * y_k + 2 * a_2
            y_k -= 1
        x_k += 1
        result.append((core_x + x_k, core_y + y_k))
        result.append((core_x - x_k, core_y + y_k))
        result.append((core_x + x_k, core_y - y_k))
        result.append((core_x - x_k, core_y - y_k))

    p_k = b_2 * (x_k + 1 / 2) ** 2 + a_2 * (y_k - 1) ** 2 - a_2 * b_2
    while y_k > 0:
        if p_k > 0:
            p_k += -2 * a_2 * y_k + 3 * a_2
        else:
            p_k += 2 * b_2 * x_k + 3 * a_2 - 2 * a_2 * y_k + 2 * b_2
            x_k += 1
        y_k -= 1
        result.append((core_x + x_k, core_y + y_k))
        result.append((core_x - x_k, core_y + y_k))
        result.append((core_x + x_k, core_y - y_k))
        result.append((core_x - x_k, core_y - y_k))

    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    if algorithm == 'Bezier':
        result = bezier_curve(p_list)
    elif algorithm == 'B-spline':
        result = bspline_curve(p_list)
    return result


def bezier_curve(p_list):
    result = []
    n = len(p_list) - 1
    result.append(p_list[0])
    u = 0.001
    while u < 1:
        res = p_list.copy()
        for i in range(n):
            temp = []
            for j in range(len(res) - 1):
                x1, y1 = res[j]
                x2, y2 = res[j + 1]
                temp.append([(1 - u) * x1 + u * x2, (1 - u) * y1 + u * y2])
            res = temp.copy()
        x, y = round(res[0][0]), round(res[0][1])
        result.append([x, y])
        u += 0.001
    result.append(p_list[-1])
    return result


def bspline_curve(p_list):
    result = []
    n = len(p_list)
    if n < 4:
        return result
    k = 4
    u = 3
    du = 1 / 1000
    while u < n:
        x1, y1 = 0, 0
        for i in range(n):
            x0, y0 = p_list[i]
            res = de_boor_cox(i, k, u)
            x1 += x0 * res
            y1 += y0 * res
        result.append([round(x1), round(y1)])
        u += du
    return result


def de_boor_cox(i, k, u):
    if k == 1:
        return 1 if i <= u < i + 1 else 0
    return (u - i) / (k - 1) * de_boor_cox(i, k - 1, u) + (i + k - u) / (k - 1) * de_boor_cox(i + 1, k - 1, u)


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for p in p_list:
        result.append([p[0] + dx, p[1] + dy])
    return result


def rotate(p_list, x, y, r, unit=True):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :param unit: (bool) 角度单位
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    if unit:
        for p in p_list:
            x0, y0 = p[0] - x, p[1] - y
            x_new = x0 * math.cos(r / 180 * math.pi) - y0 * math.sin(r / 180 * math.pi)
            y_new = x0 * math.sin(r / 180 * math.pi) + y0 * math.cos(r / 180 * math.pi)
            result.append([round(x_new) + x, round(y_new) + y])
    else:
        for p in p_list:
            x0, y0 = p[0] - x, p[1] - y
            x_new = x0 * math.cos(r) - y0 * math.sin(r)
            y_new = x0 * math.sin(r) + y0 * math.cos(r)
            result.append([round(x_new) + x, round(y_new) + y])
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return [[round((res[0] - x) * s) + x, round((res[1] - y) * s) + y] for res in p_list]


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
