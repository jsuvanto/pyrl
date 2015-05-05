from __future__ import absolute_import, division, print_function, unicode_literals

#from enum import Enum


class Key(object):
    LEFT          = "Left"
    RIGHT         = "Right"
    UP            = "Up"
    DOWN          = "Down"
    F1            = "F1"
    F2            = "F2"
    F3            = "F3"
    F4            = "F4"
    F5            = "F5"
    F6            = "F6"
    F7            = "F7"
    F8            = "F8"
    F9            = "F9"
    F10           = "F10"
    F11           = "F11"
    F12           = "F12"
    ESC           = "Esc"
    TAB           = "Tab"
    SHIFT_TAB     = "Shift+Tab"
    BACKSPACE     = "Backspace"
    SPACE         = "Space"
    ENTER         = "Enter"
    INSERT        = "Insert"
    DELETE        = "Delete"
    HOME          = "Home"
    END           = "End"
    PAGE_UP       = "Page up"
    PAGE_DOWN     = "Page down"
    NUMPAD_0      = "Numpad 0"
    NUMPAD_1      = "Numpad 1"
    NUMPAD_2      = "Numpad 2"
    NUMPAD_3      = "Numpad 3"
    NUMPAD_4      = "Numpad 4"
    NUMPAD_5      = "Numpad 5"
    NUMPAD_6      = "Numpad 6"
    NUMPAD_7      = "Numpad 7"
    NUMPAD_8      = "Numpad 8"
    NUMPAD_9      = "Numpad 9"
    WINDOW_RESIZE = "Window resize"
    CLOSE_WINDOW  = "Close window"

    # Use this one to unbind keys
    NONE          = "Unbound"

    # Bindings user don't use this one
    NO_INPUT = "No Input"
