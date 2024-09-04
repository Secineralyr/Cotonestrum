from typing import Callable
import keyboard

class KeyboardBehaviorData:
    _ctrl = False
    _alt = False
    _shift = False

    @property
    def ctrl(self):
        """Ctrlが押されているか"""
        return self._ctrl

    @property
    def alt(self):
        """Altが押されているか"""
        return self._alt

    @property
    def shift(self):
        """Shiftが押されているか"""
        return self._shift

    def _set_ctrl(self, value: bool):
        self._ctrl = value

    def _set_alt(self, value: bool):
        self._alt = value

    def _set_shift(self, value: bool):
        self._shift = value

    _press_ctrl: Callable[[], None] | None = None
    _press_alt: Callable[[], None] | None = None
    _press_shift: Callable[[], None] | None = None
    _release_ctrl: Callable[[], None] | None = None
    _release_alt: Callable[[], None] | None = None
    _release_shift: Callable[[], None] | None = None

    def start_keyboard_event(self):
        if (
            self._press_ctrl is not None or
            self._press_alt is not None or
            self._press_shift is not None or
            self._release_ctrl is not None or
            self._release_alt is not None or
            self._release_shift is not None
        ):
            return
        self._press_ctrl = keyboard.on_press_key('ctrl', lambda _: self._set_ctrl(True))
        self._release_ctrl = keyboard.on_release_key('ctrl', lambda _: self._set_ctrl(False))
        self._press_alt = keyboard.on_press_key('alt', lambda _: self._set_alt(True))
        self._release_alt = keyboard.on_release_key('alt', lambda _: self._set_alt(False))
        self._press_shift = keyboard.on_press_key('shift', lambda _: self._set_shift(True))
        self._release_shift = keyboard.on_release_key('shift', lambda _: self._set_shift(False))
