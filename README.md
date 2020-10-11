# Cmyk Splitter

#### Requirements:
```
Python3
Tkinter
Numpy
Pillow
```

### Creating executable files with PyInstaller:
To create an executable file independent of Python and modules the following codes using PyInstaller should be used according to the platform.

**Linux:**

```pyinstaller --onefile --hidden-import='PIL._tkinter_finder' --add-data="img/daka_bg.png:img" --add-data="img/daka_logo.png:img" main.py```

**Windows:**

```pyinstaller --onefile --hidden-import='PIL._tkinter_finder' --add-data="img/daka_bg.png;img" --add-data="img/daka_logo.png;img" --icon="img/logo_128x128.ico" --windowed main.py```

**MacOS:**

```pyinstaller --onefile --hidden-import='PIL._tkinter_finder' --add-data="img/daka_bg.png:img" --add-data="img/daka_logo.png:img" --icon="img/logo_128x128.icns" --windowed main.py```


