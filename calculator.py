import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QTextEdit, QPushButton, QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon
from latex2sympy2_extended import latex2sympy
import sympy
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'
matplotlib.rcParams['mathtext.default'] = 'regular'
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Get the directory containing the script
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle (PyInstaller)
    application_path = sys._MEIPASS
else:
    # If the application is run from a Python interpreter
    application_path = os.path.dirname(os.path.abspath(__file__))

class DarkFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
            }
        """)

class LatexCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX Calculator")
        self.setMinimumSize(400, 400)
        self.resize(400, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #888888;
                border: none;
                font-family: monospace;
                font-size: 14px;
                padding: 5px;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                padding: 5px 16px;
                border-radius: 10px;
                font-size: 20px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QScrollBar:vertical {
                border: none;
                background: #2b2b2b;
                height: 8px;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                min-width: 20px;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("LaTeX Calculator")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # GitHub
        github_label = QLabel('<a href="https://github.com/RaffTechAU/LatexCalc">https://github.com/RaffTechAU/LatexCalc</a>')
        github_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(github_label)

        # Create a container for input and preview
        input_preview_container = QWidget()
        input_preview_layout = QVBoxLayout(input_preview_container)
        input_preview_layout.setSpacing(15)
        input_preview_layout.setContentsMargins(0, 0, 0, 0)

        # Input section
        input_frame = DarkFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        input_label = QLabel("Input:")
        input_layout.addWidget(input_label)
        
        input_content = QFrame()
        input_content.setStyleSheet("background-color: #2b2b2b;")
        input_content_layout = QVBoxLayout(input_content)
        input_content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Enter LaTeX expression (e.g., \\frac{1}{2} + \\sqrt{4} = 2.5)")
        self.input_field.textChanged.connect(self.update_preview)
        input_content_layout.addWidget(self.input_field)
        
        input_layout.addWidget(input_content, 1)
        input_preview_layout.addWidget(input_frame, 1)

        # Preview section
        preview_frame = DarkFrame()
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.setSpacing(0)
        
        preview_label = QLabel("Preview:")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        preview_label.setFixedHeight(preview_label.sizeHint().height())
        preview_layout.addWidget(preview_label)
        
        preview_content = QFrame()
        preview_content.setStyleSheet("background-color: #2b2b2b;")
        preview_content_layout = QVBoxLayout(preview_content)
        preview_content_layout.setContentsMargins(2, 10, 2, 5)
        
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)  # Prevent content from affecting size
        preview_content_layout.addWidget(self.preview)
        
        preview_layout.addWidget(preview_content, 1)
        input_preview_layout.addWidget(preview_frame, 1)

        # Add the container to the main layout with stretch
        layout.addWidget(input_preview_container, 1)

        # Button and result section
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        self.calc_button = QPushButton("Calculate")
        self.calc_button.setFixedSize(120, 35)
        bottom_layout.addWidget(self.calc_button)
        self.calc_button.clicked.connect(self.calculate)
        
        result_frame = DarkFrame()
        result_layout = QVBoxLayout(result_frame)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(0)
        
        result_inner = QFrame()
        result_inner.setStyleSheet("background-color: #2b2b2b;")
        result_inner_layout = QVBoxLayout(result_inner)
        result_inner_layout.setContentsMargins(10, 0, 10, 0)
        result_inner_layout.setSpacing(0)
        
        self.result = QLabel()
        self.result.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.result.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                padding-right: 5px;
                font-weight: normal;
            }
            QLabel[error="true"] {
                color: #ff4444;
            }
        """)
        result_inner_layout.addWidget(self.result)
        result_layout.addWidget(result_inner)
        bottom_layout.addWidget(result_frame, stretch=1)
        
        layout.addLayout(bottom_layout)

    def render_latex(self, latex_str, dpi=600, color='white'):
        if not latex_str.strip():
            return None
            
        try:
            # Clean up the LaTeX string for mathtext
            latex_str = latex_str.strip()
            latex_str = latex_str.replace('$', '')
            
            # First render with a temporary figure to get the text size
            temp_fig = Figure(figsize=(1, 1), dpi=dpi)
            temp_ax = temp_fig.add_subplot(111)
            temp_text = temp_ax.text(0.5, 0.5, f'${latex_str}$',
                                   color=color,
                                   horizontalalignment='center',
                                   verticalalignment='center')
            temp_fig.canvas.draw()
            bbox = temp_text.get_window_extent()
            temp_fig.clear()
            
            # Calculate the required figure size based on the text size
            width_inches = bbox.width / dpi * 1.05
            height_inches = bbox.height / dpi * 1.1
            
            # Create the actual figure with the correct size
            fig = Figure(figsize=(width_inches, height_inches), dpi=dpi)
            fig.patch.set_alpha(0)
            
            # Create a subplot with no margins and transparent background
            ax = fig.add_subplot(111)
            ax.patch.set_alpha(0)
            
            # Remove all axes and margins
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Render the text
            ax.text(0.5, 0.5, f'${latex_str}$',
                   color=color,
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes)
            
            # Convert to QPixmap
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            
            # Get the RGBA buffer
            buf = canvas.buffer_rgba()
            w, h = canvas.get_width_height()
            
            # Convert to QImage and then QPixmap
            qimage = QImage(buf, w, h, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            
            # Clean up
            fig.clear()
            return pixmap
            
        except Exception as e:
            return None

    # Update the preview with the current input
    def update_preview(self):
        text = self.input_field.toPlainText()
        if not text.strip():
            self.preview.clear()
            return
            
        try:
            pixmap = self.render_latex(text)
            if pixmap:
                # Scale the pixmap to fit the preview box while maintaining aspect ratio
                preview_size = self.preview.size()
                # Scale to full width
                target_width = preview_size.width()
                scaled_pixmap = pixmap.scaled(target_width, 
                                            preview_size.height(),
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                self.preview.setPixmap(scaled_pixmap)
            else:
                self.preview.setText(" ")
        except Exception as e:
            print(f"Preview error: {e}")
            self.preview.setText(" ")

    # Calculate the result of the expression
    def calculate(self):
        try:
            text = self.input_field.toPlainText()
            if not text:
                return

            # Parse the LaTeX expression
            expr = latex2sympy(text)
            
            # Check if it's an equality expression (has Eq in it)
            if isinstance(expr, sympy.Equality):
                try:
                    # Evaluate both sides numerically first
                    left_side = float(sympy.N(expr.lhs, 10))
                    right_side = float(sympy.N(expr.rhs, 10))
                    # Compare with a small tolerance for floating point arithmetic
                    result = abs(left_side - right_side) < 1e-10
                    self.result.setProperty("error", False)
                    self.result.setText(str(result))
                    self.result.style().unpolish(self.result)
                    self.result.style().polish(self.result)
                except (TypeError, ValueError):
                    self.result.setProperty("error", True)
                    self.result.setText("Invalid Expression")
                    self.result.style().unpolish(self.result)
                    self.result.style().polish(self.result)
            else:
                # Try to evaluate numerically
                try:
                    # Evaluate with high precision (10 decimal places)
                    numeric_result = float(sympy.N(expr, 10))
                    # Format the result to remove trailing zeros
                    result_str = f"{numeric_result:.10f}".rstrip('0').rstrip('.')
                    self.result.setProperty("error", False)
                    self.result.setText(result_str)
                    self.result.style().unpolish(self.result)
                    self.result.style().polish(self.result)
                except (TypeError, ValueError):
                    self.result.setProperty("error", True)
                    self.result.setText("Invalid Expression")
                    self.result.style().unpolish(self.result)
                    self.result.style().polish(self.result)
                
        except Exception as e:
            self.result.setProperty("error", True)
            self.result.setText("Invalid Expression")
            self.result.style().unpolish(self.result)
            self.result.style().polish(self.result)

    # Handle window resize events
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide icon and metadata
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        application_path = sys._MEIPASS
    else:
        # If the application is run from a Python interpreter
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Set application metadata
    app.setApplicationName("LatexCalc")
    app.setApplicationDisplayName("LaTeX Calculator")
    app.setDesktopFileName("latexcalc")
    
    # Set window class name for proper icon mapping
    if sys.platform.startswith('linux'):
        # On Linux, we need to set the WM_CLASS property
        app.setProperty('RESOURCE_NAME', 'latexcalc')
        os.environ['RESOURCE_NAME'] = 'latexcalc'
    
    # Set the icon
    icon_path = os.path.join(application_path, 'cropped-logo.ico')
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    calculator = LatexCalculator()
    calculator.show()
    sys.exit(app.exec())