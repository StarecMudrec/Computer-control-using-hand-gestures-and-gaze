import sys
import random
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QDesktopWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer


class CameraWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Window")
        self.setGeometry(100, 100, 640, 480)  # Устанавливаем начальные размеры окна (размеры видеопотока)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)  # Устанавливаем центральный виджет для QMainWindow

        self.camera_label = QLabel(central_widget)
        self.camera_label.setGeometry(0, 0, 640, 480)  # Устанавливаем размер и положение метки камеры (размеры видеопотока)

        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)
        self.timer.start(30)

        self.setCursor(Qt.OpenHandCursor)  # Устанавливаем курсор для перемещения окна

        # Устанавливаем флаг Qt.WindowStaysOnTopHint
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def display_frame(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytesPerLine = ch * w
            qImg = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.camera_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.camera.release()  # Освобождаем ресурсы камеры при закрытии окна



class GraphicsView(QGraphicsView):
    def __init__(self, rows, cols, selected_cell):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing, True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.rows = rows
        self.cols = cols
        self.selected_cell = (selected_cell[0] - 1, selected_cell[1] - 1)

        self.setFixedSize(QDesktopWidget().availableGeometry().size())  # Установка размера на весь экран

        self.setSceneRect(0, 0, self.width(), self.height())  # Установка размеров сцены

        cell_width = self.width() / self.cols
        cell_height = self.height() / self.rows

        for row in range(self.rows):
            for col in range(self.cols):
                rect = self.scene.addRect(col * cell_width, row * cell_height, cell_width, cell_height)
                if (row, col) == self.selected_cell:
                    rect.setBrush(Qt.green)
                else:
                    rect.setBrush(Qt.white)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            x = event.pos().x()
            y = event.pos().y()
            print(f"Mouse position: ({x}, {y})")
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            while color == Qt.green:  # Проверяем, чтобы цвет не был зеленым
                color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pen = QPen(color, 5, Qt.SolidLine)
            self.scene.addEllipse(event.pos().x(), event.pos().y(), 5, 5, pen)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Accuracy Testing")

        self.rows = int(input("Enter the number of rows: "))
        self.cols = int(input("Enter the number of columns: "))
        self.selected_cell = tuple(map(int, input("Enter the selected cell (row col): ").split()))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.graphics_view = GraphicsView(self.rows, self.cols, self.selected_cell)
        self.layout.addWidget(self.graphics_view)

        self.camera_window = CameraWindow()
        self.camera_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())