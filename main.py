import asyncio
import os
import colorsys
from dotenv import load_dotenv
from tapo import ApiClient

COLOUR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
}

async def setup_light():
    load_dotenv()

    client = ApiClient(
        os.getenv("TAPO_USERNAME"),
        os.getenv("TAPO_PASSWORD")
    )

    device = await client.l530("192.168.1.234")
    return device

global power
global brightness
global colour

async def handle_command(device, cmd: str):
    power = 0
    brightness = 0
    colour = COLOUR_MAP["white"]

    parts = cmd.strip().split()

    if len(parts) != 3:
        if len(parts) >= 4 or (len(parts) > 1 and parts[1] not in COLOUR_MAP):
            print("Invalid command")
            return
        else:
            print("Format: <1|0> <colour> <brightness>")
            return
    else:
        power, colour, brightness = parts

    power = int(power)

    # Power control
    if power:
        await device.on()
    else:
        await device.off()
        return

    # Brightness
    brightness = max(1, min(100, int(brightness)))
    await device.set_brightness(brightness)

    # colour
    if colour in COLOUR_MAP:
        r, g, b = COLOUR_MAP[colour]
        h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        await device.set_hue_saturation(int(h * 360), max(1, int(s * 100)))
    else:
        print("Unknown Colour.")

async def main():
    device = await setup_light()

    print("Command format: 1 blue 100")
    print("Type 'exit' to quit")

    while True:
        cmd = input("> ")

        if cmd.lower() == "exit":
            break

        await handle_command(device, cmd)


if __name__ == "__main__":
    asyncio.run(main())