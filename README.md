# LatexCalc
A calculator app written in Python that accepts LaTeX mathematical expressions, renders them in real-time, and calculates the results.

## Features
- Real-time LaTeX rendering using matplotlib
- Support for complex mathematical expressions
- Dark mode interface
- Instant calculation results in both numerical and boolean form

## Installation
The app is available for both Windows and Linux and is portable, meaning you don't need to install python or any other dependencies.
Just download the binary for your operating system and run it.

## Usage
1. Enter your LaTeX expression in the input field
2. The expression will be rendered in real-time in the preview field
3. Click "Calculate" to see the result

## Example Expressions
- Basic arithmetic: `2 + 2`
- Fractions: `\frac{1}{2} + \frac{3}{4}`
- Powers: `2^3 + 4^2`
- Complex expressions: `\frac{1-(1+0.1)^{-15}}{0.1}+60\frac{\frac{1-(1+0.1)^{-15}}{0.1}-15(1+0.1)^{-15}}{0.1}-13330.02`

## Python dependencies
- [PyQt6](https://pypi.org/project/PyQt6)
- [latex2sympy2_extended](https://github.com/huggingface/latex2sympy2_extended)
- [sympy](https://www.sympy.org/en/index.html)
- [matplotlib](https://matplotlib.org)