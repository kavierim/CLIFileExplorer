"""
A curses-based file explorer that displays directories and files in a tree structure.
Allows navigation and expansion/collapse of directories.
"""

import curses
import os

FOLDER_ICON = "📁"
FILE_ICON = "📄"
PLUS_ICON = "+"
NO_ACCESS_ICON = "Θ"

def list_dir(path):
    """
    Return directory listing, including parent dir link.

    Args:
        path (str): The directory path to list.

    Returns:
        list: A list of tuples (name, is_dir) for each item in the directory.
    """
    items = []
    parent = os.path.dirname(path)
    if parent and parent != path:
        items.append(("..", True))
    for entry in os.listdir(path):
        full = os.path.join(path, entry)
        items.append((entry, os.path.isdir(full)))
    return sorted(items, key=lambda x: (not x[1], x[0].lower()))

expanded_dirs = set()

def flatten_tree(path, expanded):
    """
    Return a flat list of (display_name, full_path, is_dir, depth).

    Args:
        path (str): The root directory path.
        expanded (set): A set of expanded directory paths.

    Returns:
        list: A flat list of tuples (display_name, full_path, is_dir, depth).
    """
    items = []
    def recurse(p, depth, prefix):
        if depth == 0:
            parent = os.path.dirname(p)
            if parent != p:
                display_name = prefix + "├─ " + FOLDER_ICON + " .."
                items.append((display_name, parent, True, depth))
        try:
            children = sorted([(e, os.path.isdir(os.path.join(p, e))) for e in os.listdir(p)],
                              key=lambda x: (not x[1], x[0].lower()))
        except PermissionError:
            children = []
        for idx, (entry, is_dir) in enumerate(children):
            is_last = (idx == len(children) - 1)
            connector = "└─" if is_last else "├─"
            full_path = os.path.join(p, entry)
            try:
                if is_dir and full_path not in expanded and os.listdir(full_path):
                    display_name = prefix + connector + PLUS_ICON + FOLDER_ICON + " " + entry
                else:
                    display_name = prefix + connector + " " + (FOLDER_ICON if is_dir else FILE_ICON) + " " + entry
            except PermissionError:
                display_name = prefix + connector + NO_ACCESS_ICON + FOLDER_ICON + " " + entry
            items.append((display_name, full_path, is_dir, depth))
            if is_dir and full_path in expanded:
                new_prefix = prefix + ("   " if is_last else "│  ")
                recurse(full_path, depth + 1, new_prefix)
    recurse(path, 0, "")
    return items

def draw_menu(stdscr, path, flat_items, selected, offset, page_size):
    """
    Draw the menu on the screen.

    Args:
        stdscr: The curses window object.
        path (str): The current directory path.
        flat_items (list): The flat list of directory items.
        selected (int): The index of the selected item.
        offset (int): The offset for scrolling.
        page_size (int): The number of items to display per page.
    """
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = f"{path}"
    stdscr.border(0)
    stdscr.addstr(0, 1, title[:w-2], curses.color_pair(0))
    visible_items = flat_items[offset:offset + page_size]
    for i, (display_name, _, is_dir, _) in enumerate(visible_items):
        idx = offset + i
        default_color = curses.color_pair(0)
        item_color = curses.color_pair(2 if is_dir else 1)
        if idx == selected:
            stdscr.addstr(i+1, 1, display_name, curses.color_pair(3))
        else:
            # Separate line characters from icon and name
            if FOLDER_ICON in display_name:
                pos = display_name.index(FOLDER_ICON)
            elif FILE_ICON in display_name:
                pos = display_name.index(FILE_ICON)
            else:
                pos = len(display_name)
            line_part = display_name[:pos]
            icon_part = display_name[pos:]
            stdscr.addstr(i+1, 1, line_part, default_color)
            stdscr.addstr(i+1, 1 + len(line_part), icon_part, item_color)
    stdscr.refresh()

def main(stdscr, start_path):
    """
    The main function to run the curses-based file explorer.

    Args:
        stdscr: The curses window object.
        start_path (str): The starting directory path.
    """
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # files
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # dirs
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)  # highlight pair
    path = os.path.abspath(start_path)
    global expanded_dirs
    flat_items = flatten_tree(path, expanded_dirs)
    selected = 0
    offset = 0

    while True:
        h, w = stdscr.getmaxyx()
        page_size = h - 2  # Adjust page size to match window height
        max_idx = len(flat_items) - 1
        if selected > max_idx:
            selected = max_idx

        # Adjust offset for scrolling
        if selected < offset:
            offset = selected
        elif selected >= offset + page_size:
            offset = selected - page_size + 1

        draw_menu(stdscr, path, flat_items, selected, offset, page_size)
        key = stdscr.getch()
        if key in [curses.KEY_UP, 259] and selected > 0:
            selected -= 1
        elif key in [curses.KEY_DOWN, 258] and selected < len(flat_items) - 1:
            selected += 1
        elif key in [curses.KEY_RIGHT, 261]:  # Right arrow
            entry_name, full_path, is_dir, _ = flat_items[selected]
            if is_dir:
                if full_path in expanded_dirs:
                    expanded_dirs.remove(full_path)
                else:
                    expanded_dirs.add(full_path)
                flat_items = flatten_tree(path, expanded_dirs)
        elif key in [curses.KEY_LEFT, 260]:  # Left arrow
            entry_name, full_path, is_dir, _ = flat_items[selected]
            if is_dir and full_path in expanded_dirs:
                expanded_dirs.remove(full_path)
                flat_items = flatten_tree(path, expanded_dirs)
        elif key in [curses.KEY_ENTER, 10, 13]:
            entry_name, full_path, is_dir, _ = flat_items[selected]
            if os.path.basename(full_path) == "..":
                path = os.path.dirname(path)
            elif is_dir:
                path = full_path
                expanded_dirs = set()
            flat_items = flatten_tree(path, expanded_dirs)
            selected = 0
            offset = 0
        elif key in [ord('q'), 27]:  # ESC or 'q'
            break

if __name__ == "__main__":
    curses.wrapper(main, os.getcwd())
