# utils.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from typing import List

from gi.repository import Gtk, Gdk

TOOLTIP_SECONDARY_TEXT_MARKUP = """<span weight="600" size="smaller" alpha="75%">%s</span>"""


def find_child(widget: Gtk.Widget, child_name):
    """Find child widget by its name.
    Goes recursive if needed.

    :param widget: parent widget
    :param child_name: name of the widget
    :return:
    """
    if widget.get_name() == child_name:
        return widget

    if hasattr(widget, 'get_children'):
        for child in widget.get_children():
            _widget = find_child(child, child_name)
            if _widget:
                return _widget


def markup_accel_tooltip(accels: [str], description: str = None) -> str:
    """Markup accelerator tooltip.
    """

    parts = []
    if description:
        parts.append(description)

    if accels:
        unique_accels = []

        for accel in accels:
            accel_string = accel_to_string(accel)
            if accel_string not in unique_accels:
                unique_accels.append(accel)

        if unique_accels:
            # TRANSLATORS: This is a delimiter that separates two keyboard shortcut labels like `⌘ + →, Control + A`
            accel_label = ', '.join(unique_accels)
            accel_markup = TOOLTIP_SECONDARY_TEXT_MARKUP.format(accel_label)
            parts.append(accel_markup)

    return "\n".join(parts)


def accel_to_string(accel: str) -> str:
    """Converts a Gtk.accelerator_parse-style accelerator string to a human-readable string.

    Args:
        accel: An accelerator label like "<Control>a" or "<Super>Right".

    Returns:
        A human-readable string like "Ctrl + A" or "⌘ + →".
    """

    if not accel:
        return ""

    # Placeholder for translation functionality
    # (Replace with a suitable translation method for your application)
    def _(text):
        return text

    parsed, accel_key, accel_mods = Gtk.accelerator_parse(accel)

    arr = []
    if accel_mods & Gdk.ModifierType.SUPER_MASK:
        arr.append("⌘")
    if accel_mods & Gdk.ModifierType.SHIFT_MASK:
        arr.append(_("Shift"))
    if accel_mods & Gdk.ModifierType.CONTROL_MASK:
        arr.append(_("Ctrl"))
    if accel_mods & Gdk.ModifierType.ALT_MASK:
        arr.append(_("Alt"))

    switch = {
        Gdk.KEY_Up: "↑",
        Gdk.KEY_Down: "↓",
        Gdk.KEY_Left: "←",
        Gdk.KEY_Right: "→",
        Gdk.KEY_Alt_L: _("Left Alt"),
        Gdk.KEY_Alt_R: _("Right Alt"),
        Gdk.KEY_backslash: "\\",
        Gdk.KEY_Control_R: _("Right Ctrl"),
        Gdk.KEY_Control_L: _("Left Ctrl"),
        Gdk.KEY_minus: _("Minus"),
        Gdk.KEY_KP_Subtract: _("Minus"),
        Gdk.KEY_KP_Add: _("Plus"),
        Gdk.KEY_plus: _("Plus"),
        Gdk.KEY_KP_Equal: _("Equals"),
        Gdk.KEY_equal: _("Equals"),
        Gdk.KEY_Return: _("Enter"),
        Gdk.KEY_Shift_L: _("Left Shift"),
        Gdk.KEY_Shift_R: _("Right Shift"),
    }

    arr.append(switch.get(accel_key, Gtk.accelerator_get_label(accel_key, 0)))

    return " + ".join(arr) if accel_mods else arr[0]
