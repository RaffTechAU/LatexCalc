# LaTeX Calculator

A Python-based calculator that accepts LaTeX mathematical expressions, renders them in real-time, and calculates the results.

## Features

- Real-time LaTeX rendering using MathJax
- Support for complex mathematical expressions
- Dark mode interface
- Instant calculation results

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the calculator:
   ```bash
   python calculator.py
   ```

2. Enter your LaTeX expression in the input field
3. The expression will be rendered in real-time in the preview field
4. Click "Calculate" to see the result

## Example Expressions

- Basic arithmetic: `2 + 2`
- Fractions: `\frac{1}{2} + \frac{3}{4}`
- Powers: `2^3 + 4^2`
- Complex expressions: `\frac{1-(1+0.1)^{-15}}{0.1}+60\frac{\frac{1-(1+0.1)^{-15}}{0.1}-15(1+0.1)^{-15}}{0.1}-13330.02`

## Requirements

- PyQt6
- PyQtWebEngine
- latex2sympy2-extended
- sympy 