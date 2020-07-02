import asyncio

from evdev import InputDevice, ecodes
from rtmidi import API_UNIX_JACK
from rtmidi.midiconstants import PITCH_BEND
from rtmidi.midiutil import open_midioutput

midiout, port_name = open_midioutput(
    api=API_UNIX_JACK,
    use_virtual=True,
    client_name="touchpadmidi",
    port_name="touchpad",
)


touchpad = InputDevice("/dev/input/event4")
abs_x_props = touchpad.capabilities()[ecodes.EV_ABS][ecodes.ABS_X][1]
x_min = abs_x_props.min
x_max = abs_x_props.max
x_width = x_max - x_min
x_middle = x_min + x_width // 2
x_return_skip = x_width // 50

touchpad_x = 0
touchpad_touching = 0


def send_pitch_bend():
    pbend = min(16383, int(16384 * (touchpad_x - x_min) / x_width))
    msg = [PITCH_BEND, pbend & 0x7F, (pbend >> 7) & 0x7F]
    midiout.send_message(msg)
    print(pbend // 260 * " ", msg)


async def print_events(device):
    async for event in device.async_read_loop():
        global touchpad_x, touchpad_touching
        if event.type == ecodes.EV_ABS and event.code == ecodes.ABS_X:
            touchpad_x = event.value
            send_pitch_bend()
        elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
            touchpad_touching = not event.value


async def timer():
    global touchpad_x
    while True:
        await asyncio.sleep(0.01)
        if touchpad_touching:
            if touchpad_x < x_middle:
                touchpad_x = min(touchpad_x + x_return_skip, x_middle)
            elif touchpad_x > x_middle:
                touchpad_x = max(touchpad_x - x_return_skip, x_middle)
            else:
                continue
            send_pitch_bend()


if __name__ == "__main__":
    asyncio.ensure_future(print_events(touchpad))
    asyncio.ensure_future(timer())
    loop = asyncio.get_event_loop()
    loop.run_forever()
