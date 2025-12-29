import sys
import math
import os
import re
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QRect, QEasingCurve, 
    QPoint, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QShortcut, QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, 
    QPushButton, QLabel, QSizePolicy, QGraphicsDropShadowEffect
)

os.environ['QT_QPA_PLATFORM'] = 'wayland'

class AnimatedButton(QPushButton):
    def __init__(self, text, btn_type="btn-number", parent=None):
        super().__init__(text, parent)
        self.setProperty("class", btn_type)
        self.setText(text)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

class ModernCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("98kalculator")
        self.setMinimumSize(480, 680)
        self.resize(500, 750)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_display()
        self.setup_buttons()
        self.setStyleSheet(self.get_stylesheet())
        
        self.current_input = "0"
        self.reset_next = False

    def setup_display(self):
        self.display_container = QWidget()
        self.display_container.setObjectName("DisplayContainer")
        self.display_layout = QVBoxLayout(self.display_container)
        self.display_layout.setContentsMargins(25, 40, 25, 15)
        self.display_layout.setSpacing(5)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(187, 134, 252))
        shadow.setOffset(0, 0)
        
        self.lbl_history = QLabel("")
        self.lbl_history.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.lbl_history.setObjectName("HistoryLabel")
        self.display_layout.addWidget(self.lbl_history)

        self.lbl_result = QLabel("0")
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.lbl_result.setObjectName("ResultLabel")
        self.lbl_result.setGraphicsEffect(shadow)
        self.display_layout.addWidget(self.lbl_result)

        self.main_layout.addWidget(self.display_container, stretch=3)

    def setup_buttons(self):
        self.buttons_container = QWidget()
        self.buttons_layout = QGridLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(15, 15, 15, 15)
        self.buttons_layout.setSpacing(12)

        buttons = [
            ("C", 0, 0, "btn-action"), ("(", 0, 1, "btn-science"), (")", 0, 2, "btn-science"), ("mod", 0, 3, "btn-science"), ("÷", 0, 4, "btn-operator"),
            ("sin", 1, 0, "btn-science"), ("cos", 1, 1, "btn-science"), ("tan", 1, 2, "btn-science"), ("x²", 1, 3, "btn-science"), ("×", 1, 4, "btn-operator"),
            ("ln", 2, 0, "btn-science"), ("7", 2, 1, "btn-number"), ("8", 2, 2, "btn-number"), ("9", 2, 3, "btn-number"), ("-", 2, 4, "btn-operator"),
            ("log", 3, 0, "btn-science"), ("4", 3, 1, "btn-number"), ("5", 3, 2, "btn-number"), ("6", 3, 3, "btn-number"), ("+", 3, 4, "btn-operator"),
            ("1/x", 4, 0, "btn-science"), ("1", 4, 1, "btn-number"), ("2", 4, 2, "btn-number"), ("3", 4, 3, "btn-number"), ("^", 4, 4, "btn-operator"),
            ("x!", 5, 0, "btn-science"), ("e", 5, 1, "btn-science"), ("0", 5, 2, "btn-number"), (".", 5, 3, "btn-number"), ("=", 5, 4, "btn-equals"),
        ]

        for text, r, c, cls in buttons:
            btn = AnimatedButton(text, cls)
            self.buttons_layout.addWidget(btn, r, c)
            btn.clicked.connect(lambda checked, t=text: self.on_button_click(t))

        self.main_layout.addWidget(self.buttons_container, stretch=6)
        self.setup_shortcuts()

    def setup_shortcuts(self):
        key_map = {
            Qt.Key.Key_0: "0", Qt.Key.Key_1: "1", Qt.Key.Key_2: "2",
            Qt.Key.Key_3: "3", Qt.Key.Key_4: "4", Qt.Key.Key_5: "5",
            Qt.Key.Key_6: "6", Qt.Key.Key_7: "7", Qt.Key.Key_8: "8",
            Qt.Key.Key_9: "9",
            Qt.Key.Key_Plus: "+", Qt.Key.Key_Minus: "-",
            Qt.Key.Key_Asterisk: "×", Qt.Key.Key_Slash: "÷",
            Qt.Key.Key_Period: ".", Qt.Key.Key_Return: "=", 
            Qt.Key.Key_Enter: "=", Qt.Key.Key_Escape: "C",
            Qt.Key.Key_Backspace: "DEL",
            Qt.Key.Key_Exclam: "x!", Qt.Key.Key_Percent: "mod",
            Qt.Key.Key_AsciiCircum: "^"
        }
        
        for key, text in key_map.items():
            if text == "DEL":
                QShortcut(QKeySequence(key), self).activated.connect(self.backspace)
            else:
                QShortcut(QKeySequence(key), self).activated.connect(lambda t=text: self.on_button_click(t))

    def on_button_click(self, text):
        if text in "0123456789.":
            self.handle_number(text)
        elif text in "+-×÷^mod":
            self.handle_operator(text)
        elif text == "=":
            self.calculate()
        elif text == "C":
            self.clear_all()
        elif text in ["sin", "cos", "tan", "ln", "log"]:
            self.handle_func(text)
        elif text == "x²":
            self.handle_pow2()
        elif text == "1/x":
            self.handle_inv()
        elif text == "x!":
            self.handle_fact()
        elif text == "e":
            self.handle_const("e")
        elif text in ["(", ")"]:
            self.add_explicit(text)

    def handle_number(self, num):
        if self.reset_next:
            self.current_input = "0"
            self.reset_next = False
        
        # Input Limit Check
        if len(self.current_input) >= 15 and not self.reset_next:
            return

        if self.current_input == "0" and num != ".":
            self.current_input = num
        else:
            self.current_input += num
        self.update_display()

    def handle_operator(self, op):
        self.reset_next = False
        if op == "mod": op = "%"
        self.current_input += op
        self.update_display()

    def handle_func(self, func):
        if self.reset_next: self.current_input = ""; self.reset_next = False
        if self.current_input == "0": self.current_input = func + "("
        else: self.current_input += func + "("
        self.update_display()

    def handle_pow2(self):
        self.current_input += "^2"
        self.update_display()

    def handle_inv(self):
        if self.reset_next: self.reset_next = False
        self.current_input = "1/(" + self.current_input + ")"
        self.update_display()
        
    def handle_fact(self):
        if self.reset_next: self.reset_next = False
        self.current_input += "!"
        self.update_display()
        
    def handle_const(self, c):
        if self.reset_next: self.current_input = c; self.reset_next = False
        elif self.current_input == "0": self.current_input = c
        else: self.current_input += c
        self.update_display()
        
    def add_explicit(self, t):
        if self.reset_next: self.current_input = ""; self.reset_next = False
        if self.current_input == "0": self.current_input = t
        else: self.current_input += t
        self.update_display()

    def calculate(self):
        expression = self.current_input
        
        if "0/0" in expression or "0÷0" in expression:
             self.lbl_result.setText("98k is coming for you")
             self.current_input = "0"
             self.reset_next = True
             return
             
        expression = expression.replace("×", "*").replace("÷", "/")
        expression = expression.replace("^", "**")
        expression = expression.replace("mod", "%")
        
        expression = expression.replace("sin", "math.sin")
        expression = expression.replace("cos", "math.cos")
        expression = expression.replace("tan", "math.tan")
        expression = expression.replace("ln", "math.log")
        expression = expression.replace("log", "math.log10")
        
        expression = re.sub(r'(\d+)!', r'math.factorial(\1)', expression)
        
        try:
            res = eval(expression, {"__builtins__": None, "math": math})
            
            if isinstance(res, float) and math.isnan(res):
                 self.lbl_result.setText("98k is coming for you")
                 self.reset_next = True
                 return

            if isinstance(res, float):
                if res.is_integer():
                   result_str = str(int(res))
                else:
                   result_str = f"{res:.8f}".rstrip('0').rstrip('.')
            else:
                result_str = str(res)

            # Scientific Notation Check
            if len(result_str) > 12:
                try:
                    # Convert back to float to format
                    val = float(res)
                    result_str = f"{val:.5e}"
                except:
                    pass # Keep original if conversion fails

            self.current_input = result_str
            self.lbl_history.setText(expression.replace("math.", "") + " =")
            self.update_display()
            self.reset_next = True
            
        except ZeroDivisionError:
            self.lbl_result.setText("98k is coming for you")
            self.reset_next = True
        except Exception:
            self.lbl_result.setText("Error")
            self.reset_next = True

    def backspace(self):
        if self.reset_next:
            self.current_input = "0"
            self.reset_next = False
        elif len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"
        self.update_display()

    def clear_all(self):
        self.current_input = "0"
        self.lbl_history.setText("")
        self.reset_next = False
        self.update_display()

    def update_display(self):
        self.lbl_result.setText(self.current_input)

    def get_stylesheet(self):
        return """
        QMainWindow {
            background-color: #050505;
        }
        
        QWidget#DisplayContainer {
            background-color: #000000;
            border-bottom: 2px solid #3d0075;
        }
        
        QLabel#HistoryLabel {
            color: #bb86fc;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 18px;
            opacity: 0.7;
        }
        
        QLabel#ResultLabel {
            color: #ffffff;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 64px;
            font-weight: 300;
        }
        
        QPushButton {
            border: none;
            border-radius: 16px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 20px;
            font-weight: 600;
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        
        QPushButton:hover {
            background-color: #2a2a2a;
            border: 1px solid #3d0075;
        }
        
        QPushButton:pressed {
            background-color: #3d0075;
            color: #ffffff;
        }

        QPushButton[class="btn-operator"] {
            background-color: #311b92;
            color: #ffffff;
            font-size: 24px;
        }
        QPushButton[class="btn-operator"]:hover {
            background-color: #4527a0;
            border: 1px solid #7c4dff;
        }

        QPushButton[class="btn-science"] {
            background-color: #121212;
            color: #bb86fc;
            font-size: 18px;
            font-style: italic;
        }
        QPushButton[class="btn-science"]:hover {
            background-color: #2c2c2e;
            color: #d0bcff;
        }

        QPushButton[class="btn-action"] {
            background-color: #2b1111;
            color: #ff5252;
        }
        QPushButton[class="btn-action"]:hover {
            background-color: #441b1b;
        }

        QPushButton[class="btn-equals"] {
            background-color: #6200ea;
            color: #ffffff;
            font-size: 32px;
            border-radius: 16px;
        }
        QPushButton[class="btn-equals"]:hover {
            background-color: #7c4dff;
            border: 2px solid #ffffff;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernCalculator()
    window.show()
    sys.exit(app.exec())
