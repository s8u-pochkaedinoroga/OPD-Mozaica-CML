from PIL import Image, ImageDraw
import numpy as np
from collections import defaultdict

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
        """Находит ближайший доступный цвет.""" 
        available_colors_array = np.array(self.available_colors, dtype=np.float64)
        color_array = np.array(color, dtype=np.float64)
        distances = np.linalg.norm(available_colors_array - color_array, axis=1)
        closest_color_index = np.argmin(distances)
        return self.available_colors[closest_color_index]

    
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
        preview.show()

    def generate_instructions(self):
        """Генерирует инструкции для сборки мозаики."""
        if self.mosaic is None:
            self.generate_mosaic()
        instructions = defaultdict(list)
        for y in range(self.mosaic_size[1]):
            for x in range(self.mosaic_size[0]):
                color = tuple(self.mosaic[y, x])
                instructions[color].append((x, y))
        return instructions

    def save_instructions(self, filename):
        """Сохраняет инструкции в файл."""
        instructions = self.generate_instructions()
        with open(filename, 'w') as f:
            for color, coordinates in instructions.items():
                f.write(f"Color: {color}\n")
                for coord in coordinates:
                    f.write(f"{coord}\n")
                f.write("\n")





available_colors = [
          (255, 0, 0),       # Красны
          (255, 255, 0),     # Желтый
          (0, 255, 0),       # Зелены
          (255, 255, 255),   # Белый
          (0, 0, 0)          # Черный
]

mosaic_size = (50, 50)  # Размер мозаики в квадратиках
canvas_size = (1000, 1000)  # Размер полотна для превью

generator = MosaicGenerator("images/image.jpg", available_colors, mosaic_size, canvas_size)
generator.show_preview()
generator.save_instructions("instructions.txt")