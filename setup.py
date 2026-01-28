from setuptools import setup, find_packages

setup(
    name="pyside-native-glass",
    version="0.3.0",
    description="Librería de efectos nativos (Mica, Acrylic, Vibrancy) para PySide6",
    author="Tu Nombre",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6",
        "pyobjc-framework-Cocoa; sys_platform == 'darwin'"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
)
