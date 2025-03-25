import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import numpy as np
from collections import defaultdict
import json
import csv

class MosaicGenerator:
    def __init__(self, image_path, available_colors, mosaic_size, canvas_size):
        self.image_path = image_path
        self.available_colors = available_colors
        self.mosaic_size = mosaic_size
        self.canvas_size = canvas_size
        self.image = Image.open(image_path).convert("RGB")
        self.image = self.image.resize(self.mosaic_size)
        self.pixels = np.array(self.image)
        self.mosaic = None

    def _find_closest_color(self, color):
        target = np.array(color)
        best_score = float('inf')
        best_color = None

        for candidate in self.available_colors:
            arr = np.array(candidate)

            # 1. Максимальное отклонение по каналу (главный критерий)
            max_diff = np.max(np.abs(arr - target))

            # 2. Среднее отклонение (вторичный критерий)
            mean_diff = np.mean(np.abs(arr - target))

            # 3. Штраф за серые тона (R=G=B)
            gray_penalty = 20 if (arr[0] == arr[1] == arr[2]) else 0

            # Комбинированный score
            score = max_diff * 1000 + mean_diff + gray_penalty

            if score < best_score:
                best_score = score
                best_color = candidate

        return best_color

    def generate_mosaic(self):
        """Генерирует мозаику."""
        self.mosaic = np.zeros((self.mosaic_size[1], self.mosaic_size[0], 3), dtype=np.uint8)
        for y in range(self.mosaic_size[1]):
            for x in range(self.mosaic_size[0]):
                original_color = self.pixels[y, x]
                closest_color = self._find_closest_color(original_color)
                self.mosaic[y, x] = closest_color

    def show_preview(self):
        """Показывает превью мозаики."""
        if self.mosaic is None:
            self.generate_mosaic()
        preview = Image.fromarray(self.mosaic, 'RGB')
        preview = preview.resize(self.canvas_size, Image.NEAREST)
        return ImageTk.PhotoImage(preview)

    def generate_instructions(self):
        """Генерирует инструкции для сборки мозаики."""
        if self.mosaic is None:
            self.generate_mosaic()
        instructions = defaultdict(list)
        for y in range(self.mosaic_size[1]):
            for x in range(self.mosaic_size[0]):
                color = tuple(int(c) for c in self.mosaic[y, x])  # Преобразуем в целые числа
                instructions[color].append((x, y))
        return instructions

    def save_instructions(self, filename, format='txt'):
        instructions = self.generate_instructions()

        if format == 'txt':
            with open(filename, 'w') as f:
                for color, coordinates in instructions.items():
                    f.write(f"Color: {color}\n")
                    f.write(f"Count: {len(coordinates)}\n")
                    for coord in coordinates:
                        f.write(f"{coord}\n")
                    f.write("\n")

        elif format == 'json':
            data = {
                str(color): {
                    'count': len(coordinates),
                    'coordinates': coordinates
                } for color, coordinates in instructions.items()
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

        elif format == 'csv':
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Color", "Count", "Coordinates"])
                for color, coordinates in instructions.items():
                    writer.writerow([color, len(coordinates), str(coordinates)])

        else:
            raise ValueError("Unsupported format. Use 'txt', 'json', or 'csv'.")

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mosaic Generator")
        self.root.geometry("1500x1200")  # Установка размера окна
        self.available_colors = [
            (255, 0, 0),  # Красный
            (255, 255, 0),  # Желтый
            (0, 255, 0),  # Зеленый
            (255, 255, 255),  # Белый
            (0, 0, 0),  # Черный
            (75, 0, 130),  # Фиолетовый
            (0, 0, 255),  # Синий
            (0, 128, 0),  # Темно-зеленый
            (255, 192, 203),  # Розовый
            (0, 191, 255),  # Голубой
        ]
        self.mosaic_size = (100, 100)  # Размер мозаики в квадратиках
        self.canvas_size = (800, 800)  # Размер полотна для превью

        self.image_path = tk.StringVar()
        self.image_path.set("images/cvetok.png")

        self.format = tk.StringVar()
        self.format.set('txt')

        self.mosaic_size_var = tk.StringVar()
        self.mosaic_size_var.set("100,100")  # Размер мозаики

        self.create_widgets()

    def create_widgets(self):
        # Менюбар
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть изображение", command=self.browse_image)
        file_menu.add_command(label="Сохранить инструкции", command=self.save_instructions)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        # Основные виджеты
        tk.Label(self.root, text="Изображение:", font=('Arial', 14)).grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.image_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Обзор", command=self.browse_image, font=('Arial', 12)).grid(row=0, column=2, padx=10, pady=10)

        tk.Label(self.root, text="Размер мозаики (x,y):", font=('Arial', 14)).grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.mosaic_size_var, width=20).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Формат инструкций:", font=('Arial', 14)).grid(row=2, column=0, padx=10, pady=10)
        tk.OptionMenu(self.root, self.format, 'txt', 'json', 'csv').grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self.root, text="Показать превью", command=self.show_preview, font=('Arial', 12)).grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Поле для превью
        self.preview_label = tk.Label(self.root)
        self.preview_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    def browse_image(self):
        path = filedialog.askopenfilename()
        self.image_path.set(path)

    def show_preview(self):
        if not self.image_path.get():
            self.error_message("Ошибка: Путь к изображению не указан.")
            return

        try:
            mosaic_size = tuple(map(int, self.mosaic_size_var.get().split(',')))
            generator = MosaicGenerator(self.image_path.get(), self.available_colors, mosaic_size, self.canvas_size)
            preview = generator.show_preview()
            self.preview_label.config(image=preview)
            self.preview_label.image = preview  # Чтобы изображение не было удалено
        except Exception as e:
            self.error_message(f"Ошибка при генерации превью: {str(e)}")

    def save_instructions(self):
        if not self.image_path.get():
            self.error_message("Ошибка: Путь к изображению не указан.")
            return

        try:
            mosaic_size = tuple(map(int, self.mosaic_size_var.get().split(',')))
            generator = MosaicGenerator(self.image_path.get(), self.available_colors, mosaic_size, self.canvas_size)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt" if self.format.get() == 'txt' else ".json" if self.format.get() == 'json' else ".csv")
            if not filename:
                self.error_message("Ошибка: Файл для сохранения не выбран.")
                return
            generator.save_instructions(filename, format=self.format.get())
            self.success_message("Инструкции успешно сохранены.")
        except Exception as e:
            self.error_message(f"Ошибка при сохранении инструкций: {str(e)}")

    def error_message(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Ошибка")
        tk.Label(error_window, text=message, fg="red").pack(padx=10, pady=10)
        tk.Button(error_window, text="ОК", command=error_window.destroy).pack(pady=10)

    def success_message(self, message):
        success_window = tk.Toplevel(self.root)
        success_window.title("Успех")
        tk.Label(success_window, text=message, fg="green").pack(padx=10, pady=10)
        tk.Button(success_window, text="ОК", command=success_window.destroy).pack(pady=10)

    def about(self):
        # Вывод информации о программе
        print("Программа для генерации мозаик.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()