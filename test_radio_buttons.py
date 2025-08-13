#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы radio button'ов в food tracker.
"""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class TestRadioButtons(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Radio Buttons")
        self.setGeometry(100, 100, 400, 300)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Создаем layout
        layout = QVBoxLayout(central_widget)

        # Создаем radio button'ы
        self.radio_weight = QRadioButton("Use Weight Mode")
        self.radio_calories = QRadioButton("Use Portion Mode")

        # Создаем spin box'ы
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(0, 10000)
        self.weight_spin.setValue(100)
        self.weight_spin.setSuffix(" g")

        self.calories_spin = QDoubleSpinBox()
        self.calories_spin.setRange(0, 10000)
        self.calories_spin.setValue(50)
        self.calories_spin.setSuffix(" kcal")

        # Создаем кнопку для тестирования
        self.test_button = QPushButton("Test Calculation")
        self.test_button.clicked.connect(self.test_calculation)

        # Создаем label для результата
        self.result_label = QLabel("Result will appear here")

        # Добавляем виджеты в layout
        layout.addWidget(QLabel("Radio Buttons:"))
        layout.addWidget(self.radio_weight)
        layout.addWidget(self.radio_calories)

        layout.addWidget(QLabel("Weight:"))
        layout.addWidget(self.weight_spin)

        layout.addWidget(QLabel("Calories:"))
        layout.addWidget(self.calories_spin)

        layout.addWidget(self.test_button)
        layout.addWidget(self.result_label)

        # Устанавливаем начальное состояние
        self.radio_weight.setChecked(True)

        # Подключаем сигналы
        self.radio_weight.clicked.connect(self.on_radio_changed)
        self.radio_calories.clicked.connect(self.on_radio_changed)
        self.weight_spin.valueChanged.connect(self.on_values_changed)
        self.calories_spin.valueChanged.connect(self.on_values_changed)

        # Обновляем расчет
        self.update_calculation()

    def on_radio_changed(self):
        """Обработчик изменения radio button'ов"""
        print(
            f"🔧 Radio button changed: weight={self.radio_weight.isChecked()}, calories={self.radio_calories.isChecked()}"
        )
        self.update_calculation()

    def on_values_changed(self):
        """Обработчик изменения значений"""
        print(f"🔧 Values changed: weight={self.weight_spin.value()}, calories={self.calories_spin.value()}")
        self.update_calculation()

    def test_calculation(self):
        """Тестирует расчет при нажатии кнопки"""
        print(f"🔧 Test button clicked!")
        print(
            f"🔧 Current state: weight={self.weight_spin.value()}, calories={self.calories_spin.value()}, use_weight={self.radio_weight.isChecked()}"
        )
        self.update_calculation()

    def update_calculation(self):
        """Обновляет расчет калорий"""
        weight = self.weight_spin.value()
        calories = self.calories_spin.value()
        use_weight = self.radio_weight.isChecked()

        print(f"🔧 update_calculation: weight={weight}, calories={calories}, use_weight={use_weight}")

        if use_weight:
            # Weight mode: calories per 100g
            if weight > 0 and calories > 0:
                calculated_calories = (weight * calories) / 100
                self.result_label.setText(f"Weight Mode: {calculated_calories:.1f} kcal total")
                print(f"🔧 Weight mode: calculated_calories={calculated_calories}")
            else:
                self.result_label.setText("Weight Mode: Need weight > 0 and calories > 0")
                print(f"🔧 Weight mode: insufficient data for calculation")
        else:
            # Portion mode: direct calories
            if calories > 0:
                self.result_label.setText(f"Portion Mode: {calories:.1f} kcal total")
                print(f"🔧 Portion mode: direct calories={calories}")
            else:
                self.result_label.setText("Portion Mode: Need calories > 0")
                print(f"🔧 Portion mode: no calories specified")


def main():
    app = QApplication(sys.argv)
    window = TestRadioButtons()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
