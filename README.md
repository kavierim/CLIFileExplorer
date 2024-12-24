# CLIFileExplorer

CLIFileExplorer is a curses-based file explorer that displays directories and files in a tree structure. It allows navigation and expansion/collapse of directories.

## Features

- Display directories and files in a tree structure.
- Navigate through directories and files using arrow keys.
- Expand and collapse directories.

## Installation

To run CLIFileExplorer, you need to have Python installed on your system. You can install the required dependencies using pip:

```sh
pip install -r requirements.txt
```

## Usage

To start the file explorer, run the following command:

```sh
python ws.py
```

You can also specify a starting directory:

```sh
python ws.py /path/to/start/directory
```

## Building a Binary

To build a standalone binary of CLIFileExplorer using PyInstaller, follow these steps:

1. Install PyInstaller if you haven't already:

    ```sh
    pip install pyinstaller
    ```

2. Run PyInstaller with the following command:

    ```sh
    pyinstaller --onefile ws.py
    ```

3. The binary will be created in the `dist` directory.

## Keybindings

- `UP` : Move up
- `DOWN` : Move down
- `RIGHT` : Expand directory
- `LEFT` : Collapse directory
- `ENTER`: Enter directory or go up to parent directory
- `q` or `ESC`: Quit the file explorer

## License

This project is licensed under the MIT License.