import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel, QFileDialog
)

from core.io import load_point_cloud
from core.projector import normalize_points, generate_6_views, save_image


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PointCloud Preprocessor")
        self.resize(400, 200)

        self.layout = QVBoxLayout()

        self.label = QLabel("请选择点云文件夹")
        self.layout.addWidget(self.label)

        self.btn_select = QPushButton("选择文件夹")
        self.btn_select.clicked.connect(self.select_folder)
        self.layout.addWidget(self.btn_select)

        self.btn_run = QPushButton("开始处理")
        self.btn_run.clicked.connect(self.run)
        self.layout.addWidget(self.btn_run)

        self.setLayout(self.layout)

        self.folder_path = None

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择点云文件夹")
        if folder:
            self.folder_path = folder
            self.label.setText(f"已选择: {folder}")

    def run(self):
        if not self.folder_path:
            self.label.setText("请先选择文件夹")
            return

        output_dir = os.path.join(self.folder_path, "output")
        os.makedirs(output_dir, exist_ok=True)

        files = [f for f in os.listdir(self.folder_path)
                 if f.endswith(".ply")]

        for f in files:
            path = os.path.join(self.folder_path, f)
            pcd = load_point_cloud(path)

            points = normalize_points(
                __import__("numpy").asarray(pcd.points)
            )

            views = generate_6_views(points)

            obj_dir = os.path.join(output_dir, f.split(".")[0])
            os.makedirs(obj_dir, exist_ok=True)

            for name, img in views.items():
                save_image(img, os.path.join(obj_dir, f"{name}.png"))

        self.label.setText("处理完成！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())