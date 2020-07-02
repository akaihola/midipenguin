from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from os import PathLike
from typing import AnyStr

import evdev
from evdev import InputDevice, ecodes
from rtmidi import API_UNIX_JACK, MidiOut
from rtmidi.midiconstants import PITCH_BEND
from rtmidi.midiutil import open_midioutput


class TouchpadInputDevice(InputDevice):
    def __init__(self, dev: PathLike[AnyStr]) -> None:
        super().__init__(dev)
        caps = self.capabilities()
        if ecodes.EV_ABS not in caps:
            raise InvalidTouchpadDevice()
        abs_x_props = caps[ecodes.EV_ABS][ecodes.ABS_X][1]
        self.x_min = abs_x_props.min
        self.x_max = abs_x_props.max
        self.x_width = self.x_max - self.x_min
        self.x_middle = self.x_min + self.x_width // 2
        self.x_return_skip = self.x_width // 50


@dataclass
class FingerState:
    x: int
    touching: bool


def send_pitch_bend(touchpad: TouchpadInputDevice, x: int, midiout: MidiOut) -> None:
    pbend = min(16383, int(16384 * (x - touchpad.x_min) / touchpad.x_width))
    msg = [PITCH_BEND, pbend & 0x7F, (pbend >> 7) & 0x7F]
    midiout.send_message(msg)
    print(pbend // 260 * " ", msg)


async def print_events(
    touchpad: TouchpadInputDevice, finger: FingerState, midiout: MidiOut
) -> None:
    async for event in touchpad.async_read_loop():
        if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_X:
            finger.x = event.value
            send_pitch_bend(touchpad, finger.x, midiout)
        elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
            finger.touching = not event.value


async def timer(
    touchpad: TouchpadInputDevice, finger: FingerState, midiout: MidiOut
) -> None:
    while True:
        await asyncio.sleep(0.01)
        if finger.touching:
            if finger.x < touchpad.x_middle:
                finger.x = min(finger.x + touchpad.x_return_skip, touchpad.x_middle)
            elif finger.x > touchpad.x_middle:
                finger.x = max(finger.x - touchpad.x_return_skip, touchpad.x_middle)
            else:
                continue
            send_pitch_bend(touchpad, finger.x, midiout)


class InvalidTouchpadDevice(Exception):
    pass


def main() -> None:
    for path in evdev.list_devices():
        try:
            touchpad = TouchpadInputDevice(path)
        except InvalidTouchpadDevice:
            continue
        else:
            break
    else:
        print("Can't find a touchpad")
        sys.exit(1)

    finger = FingerState(x=0, touching=False)

    midiout, port_name = open_midioutput(
        api=API_UNIX_JACK,
        use_virtual=True,
        client_name="touchpadmidi",
        port_name="touchpad",
    )

    asyncio.ensure_future(print_events(touchpad, finger, midiout))
    asyncio.ensure_future(timer(touchpad, finger, midiout))
    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == "__main__":
    main()
