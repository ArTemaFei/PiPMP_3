"""
Поток для выполнения фоновой задачи: конвертация изображения в другой формат.
Вариант 4: Асинхронная конвертация формата.
"""

import os
import time

import cv2
from PyQt6.QtCore import QThread, pyqtSignal


class ConversionThread(QThread):
    """Поток, выполняющий конвертацию файла изображения в другой формат."""

    # Сигналы (Observer pattern: поток — subject, слоты в GUI — observers)
    progress = pyqtSignal(int)        # Прогресс выполнения (0-100)
    result_ready = pyqtSignal(str)    # Путь к готовому файлу
    error_occurred = pyqtSignal(str)  # Текст ошибки

    def __init__(self, input_path: str, output_path: str, to_grayscale: bool = False, parent=None):
        super().__init__(parent)
        self.input_path = input_path
        self.output_path = output_path
        self.to_grayscale = to_grayscale

    def run(self):
        """Выполнение конвертации в фоновом потоке."""
        try:
            # 1. Проверяем, что исходный файл существует
            if not os.path.isfile(self.input_path):
                self.error_occurred.emit(f"Файл не найден: {self.input_path}")
                return

            self.progress.emit(10)
            time.sleep(0.3)  # имитация задержки на чтение/подготовку

            # 2. Загружаем изображение
            image = cv2.imread(self.input_path)
            if image is None:
                self.error_occurred.emit("Не удалось прочитать изображение (неподдерживаемый формат?)")
                return

            self.progress.emit(40)
            time.sleep(0.3)

            # 3. Дополнительное преобразование (по желанию пользователя)
            if self.to_grayscale:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Обратно в 3 канала, чтобы формат записи был универсальным
                image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            self.progress.emit(70)
            time.sleep(0.3)

            # 4. Создаём папку назначения, если нужно, и сохраняем в новом формате
            out_dir = os.path.dirname(self.output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            success = cv2.imwrite(self.output_path, image)
            if not success:
                self.error_occurred.emit("Не удалось сохранить файл в выбранном формате")
                return

            self.progress.emit(100)

            # 5. Сообщаем основному потоку об успешном результате
            self.result_ready.emit(self.output_path)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка конвертации: {e}")
