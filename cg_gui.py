#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import sys
from typing import Optional

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem, QColorDialog, QDialog, QInputDialog, QMessageBox, QFileDialog)

import cg_algorithms as alg


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_color = QColor(0, 0, 0)

        self.isPolygonFinish = False
        self.curvePointNum = -1

        self.origin_pos = None
        self.origin_p_list = None
        self.trans_center = None

    def init(self):
        self.scene().clear()
        self.item_dict = {}

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_color = QColor(0, 0, 0)

        self.isPolygonFinish = False
        self.curvePointNum = -1

        self.origin_pos = None
        self.origin_p_list = None
        self.trans_center = None

    def start_draw_line(self, algorithm):
        self.status = 'line'
        self.temp_algorithm = algorithm

    def start_draw_polygon(self, algorithm):
        self.status = 'polygon'
        self.temp_algorithm = algorithm

    def start_draw_ellipse(self):
        self.status = 'ellipse'

    def start_draw_curve(self, algorithm, curvePointNum):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.curvePointNum = curvePointNum

    def start_translate(self):
        self.status = 'translate'

    def start_rotate(self):
        self.status = 'rotate'

    def start_scale(self):
        self.status = 'scale'

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm

    def finish_draw(self):
        self.temp_item = None

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if selected != '':
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            if self.selected_id != '':
                self.item_dict[self.selected_id].selected = False
                self.item_dict[self.selected_id].update()
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.status = ''
            self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_id = self.main_window.get_id()
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.temp_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if self.temp_item is None:
                self.temp_id = self.main_window.get_id()
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        self.temp_color)
                self.scene().addItem(self.temp_item)
            else:
                x0, y0 = self.temp_item.p_list[0]
                if (abs(x0 - x) + abs(y0 - y) < 10) and len(self.temp_item.p_list) > 2:
                    self.isPolygonFinish = True
                else:
                    self.temp_item.p_list.append([x, y])
        elif self.status == 'ellipse':
            self.temp_id = self.main_window.get_id()
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.temp_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item is None:
                self.temp_id = self.main_window.get_id()
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        self.temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'translate':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                self.origin_pos = pos
        elif self.status == 'rotate':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                if self.trans_center is None:
                    self.trans_center = pos
                else:
                    self.origin_pos = pos
        elif self.status == 'scale':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                if self.trans_center is None:
                    self.trans_center = pos
                else:
                    self.origin_pos = pos
        elif self.status == 'clip':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                self.origin_pos = pos
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'polygon':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'curve':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            if self.selected_id != '':
                dx = x - int(self.origin_pos.x())
                dy = y - int(self.origin_pos.y())
                self.temp_item.p_list = alg.translate(self.origin_p_list, dx, dy)
        elif self.status == 'rotate':
            if self.selected_id != '' and self.trans_center is not None and self.origin_pos is not None:
                x_origin, y_origin = int(self.origin_pos.x() - self.trans_center.x()), int(
                    self.origin_pos.y() - self.trans_center.y())
                len_origin = math.sqrt(x_origin ** 2 + y_origin ** 2)
                x_now, y_now = x - int(self.trans_center.x()), y - int(self.trans_center.y())
                len_now = math.sqrt(x_now ** 2 + y_now ** 2)
                if len_origin != 0 and len_now != 0:
                    sin_origin = y_origin / len_origin
                    cos_origin = x_origin / len_origin
                    sin_now = y_now / len_now
                    cos_now = x_now / len_now
                    delta_sin = sin_now * cos_origin - cos_now * sin_origin
                    delta_cos = cos_now * cos_origin + sin_now * sin_origin
                    if delta_cos >= 0:
                        r = math.asin(delta_sin)
                    else:
                        r = math.pi - math.asin(delta_sin)
                    self.temp_item.p_list = alg.rotate(self.origin_p_list, int(self.trans_center.x()),
                                                       int(self.trans_center.y()), r, False)
        elif self.status == 'scale':
            if self.selected_id != '' and self.trans_center is not None and self.origin_pos is not None:
                x_last, y_last = int(self.origin_pos.x() - self.trans_center.x()), int(
                    self.origin_pos.y() - self.trans_center.y())
                len_last = math.sqrt(x_last ** 2 + y_last ** 2)
                if len_last != 0:
                    x_now, y_now = x - int(self.trans_center.x()), y - int(self.trans_center.y())
                    len_now = math.sqrt(x_now ** 2 + y_now ** 2)
                    self.temp_item.p_list = alg.scale(self.origin_p_list, int(self.trans_center.x()),
                                                      int(self.trans_center.y()), len_now / len_last)
        elif self.status == 'clip':
            if self.selected_id != '':
                self.temp_item.p_list = alg.clip(self.origin_p_list, self.origin_pos.x(), self.origin_pos.y(), x, y,
                                                 self.temp_algorithm)
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            if self.isPolygonFinish:
                self.isPolygonFinish = False
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
            else:
                pos = self.mapToScene(event.localPos().toPoint())
                x = int(pos.x())
                y = int(pos.y())
                self.temp_item.p_list[-1] = [x, y]
                self.updateScene([self.sceneRect()])
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'curve':
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = int(pos.y())
            self.temp_item.p_list[-1] = [x, y]
            self.updateScene([self.sceneRect()])
            if len(self.temp_item.p_list) == self.curvePointNum:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
        elif self.status == 'translate':
            self.origin_pos = None
            self.origin_p_list = None
        elif self.status == 'rotate':
            if self.origin_pos is not None:
                self.origin_pos = None
                self.origin_p_list = None
                self.trans_center = None
        elif self.status == 'scale':
            if self.origin_pos is not None:
                self.origin_pos = None
                self.origin_p_list = None
                self.trans_center = None
        elif self.status == 'clip':
            self.origin_pos = None
            self.origin_p_list = None
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '',
                 color: QColor = QColor(0, 0, 0), parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.color = color
        self.selected = False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            x, y = self.p_list[0]
            x0, y0 = x, y
            x1, y1 = x, y
            for i in range(1, len(self.p_list)):
                x, y = self.p_list[i]
                x0 = min(x0, x)
                y0 = min(y0, y)
                x1 = max(x1, x)
                y1 = max(y1, y)
            w = x1 - x0
            h = y1 - y0
            return QRectF(x0 - 1, y0 - 1, w + 2, h + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)

        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)

        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)

        ellipse_act.triggered.connect(self.ellipse_action)

        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)

        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        temp_color = QColorDialog.getColor()
        if temp_color.isValid():
            self.canvas_widget.temp_color = temp_color

    def reset_canvas_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.list_widget.clear()
        self.canvas_widget.init()
        self.item_cnt = 0

        dialog = QDialog()
        dialog.setWindowTitle('重置画布')
        dialog.resize(400, 250)

        while True:
            height_dialog = QInputDialog(self)
            height, height_pressed = height_dialog.getInt(self, '重置画布', 'Please input height(range:100-1000):',
                                                          int(self.scene.height()))
            if not height_pressed:
                break

            width_dialog = QInputDialog(self)
            width, width_pressed = width_dialog.getInt(self, '重置画布', 'Please input height(range:100-1000):',
                                                       int(self.scene.width()))
            if not width_pressed:
                break

            if height < 100 or width < 100 or height > 1000 or width > 1000:
                QMessageBox.critical(self, 'Error', 'out of range')
            else:
                self.scene.setSceneRect(0, 0, height, width)
                break

        self.statusBar().showMessage('空闲')

    def save_canvas_action(self):
        self.statusBar().showMessage('保存画布')
        canvas = self.canvas_widget

        dialog = QFileDialog()
        filename = dialog.getSaveFileName(filter="Image Files(*.jpg *.png *.bmp)")
        if filename[0]:
            pix = QPixmap(self.width(), self.height())
            pix.fill(QColor(255, 255, 255))
            painter = QPainter()
            painter.begin(pix)
            for item in canvas.item_dict:
                canvas.item_dict[item].paint(painter, QStyleOptionGraphicsItem)
            painter.end()
            pix.save(filename[0])

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive')
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA')
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA')
        self.statusBar().showMessage('DDA算法绘制polygon')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham')
        self.statusBar().showMessage('Bresenham算法绘制polygon')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse()
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', 3)
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', 4)
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland裁剪')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky裁剪')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
