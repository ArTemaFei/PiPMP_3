"""
Главное окно приложения.
Вариант 4: Асинхронная конвертация формата изображения.
"""

import os
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QProgressBar, QFileDialog, QComboBox, QCheckBox, QMessageBox
)

from worker_thread import ConversionThread


class MainWindow(QMainWindow):
    """Главное окно приложения для асинхронной конвертации изображений."""

    SUPPORTED_FORMATS = ["jpg", "png", "bmp", "tiff"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Асинхронная конвертация формата")
        self.setGeometry(100, 100, 480, 260)

        self.input_path = None
        self.thread = None

        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""

        # --- Выбор файла ---
        self.choose_button = QPushButton("Выбрать файл")
        self.choose_button.clicked.connect(self.choose_file)

        self.file_label = QLabel("Файл не выбран")

        # --- Выбор целевого формата ---
        self.format_combo = QComboBox()
        self.format_combo.addItems(self.SUPPORTED_FORMATS)

        self.grayscale_checkbox = QCheckBox("Перевести в оттенки серого")

        # --- Кнопка запуска конвертации ---
        self.convert_button = QPushButton("Конвертировать")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.start_conversion)

        # --- Прогресс и статус ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel("Готово к работе")

        # --- Компоновка ---
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Формат:"))
        format_layout.addWidget(self.format_combo)

        layout = QVBoxLayout()
        layout.addWidget(self.choose_button)
        layout.addWidget(self.file_label)
        layout.addLayout(format_layout)
        layout.addWidget(self.grayscale_checkbox)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def choose_file(self):
        """Открывает диалог выбора файла изображения."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if path:
            self.input_path = path
            self.file_label.setText(os.path.basename(path))
            self.convert_button.setEnabled(True)
            self.status_label.setText("Готово к работе")
            self.progress_bar.setValue(0)

    def start_conversion(self):
        """Запуск фоновой задачи конвертации."""
        if not self.input_path:
            return

        # Формируем путь результата: то же имя, новое расширение
        target_format = self.format_combo.currentText()
        base, _ = os.path.splitext(self.input_path)
        output_path = f"{base}_converted.{target_format}"

        # Блокируем кнопки на время выполнения
        self.convert_button.setEnabled(False)
        self.choose_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Конвертация...")

        # Создаём и запускаем поток
        self.thread = ConversionThread(
            input_path=self.input_path,
            output_path=output_path,
            to_grayscale=self.grayscale_checkbox.isChecked(),
        )
        self.thread.progress.connect(self.on_progress)
        self.thread.result_ready.connect(self.on_result)
        self.thread.error_occurred.connect(self.on_error)
        self.thread.start()

    def on_progress(self, value: int):
        """Обработчик прогресса конвертации."""
        self.progress_bar.setValue(value)

    def on_result(self, output_path: str):
        """Обработчик успешного завершения конвертации."""
        self.status_label.setText(f"Готово: {output_path}")
        self.convert_button.setEnabled(True)
        self.choose_button.setEnabled(True)

    def on_error(self, message: str):
        """Обработчик ошибки в фоновом потоке."""
        self.status_label.setText("Ошибка конвертации")
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "Ошибка", message)
        self.convert_button.setEnabled(True)
        self.choose_button.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
