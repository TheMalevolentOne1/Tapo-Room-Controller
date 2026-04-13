import asyncio
import os
import colorsys
from dotenv import load_dotenv
from tapo import ApiClient
import argparse

COLOUR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (0, 0, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
}

async def setup_light():
    load_dotenv()

    try:
        client = ApiClient(os.getenv("TAPO_USERNAME"), os.getenv("TAPO_PASSWORD"))
    except TypeError:
        print("Verify existence of .env with Tapo Creds")
        return

    device = await client.l530("192.168.1.234")
    return device

global power
global brightness
global colour

async def toggle_power(device, power):
    # Power control
    if power:
        await device.on()
    else:
        await device.off()
    return

async def change_brightness(device, brightness):
    # Brightness
    brightness = max(1, min(100, int(brightness)))
    await device.set_brightness(brightness)
    return

async def change_colour(device, colour):
    # colour
    if colour in COLOUR_MAP:
        r, g, b = COLOUR_MAP[colour]
        h, s, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        await device.set_hue_saturation(int(h * 360), max(1, int(s * 100)))
    else:
        print("Unknown Colour.")

async def main():
    device = await setup_light()
    if not device:
        return

    if args.mode == "normal":
        await toggle_power(device, args.power)
        await change_colour(device, args.colour)
        await change_brightness(device, args.brightness)

    elif args.mode == "custom":
        await toggle_power(device, args.power)

        # Convert RGB → HSV (same logic you used)
        h, s, _ = colorsys.rgb_to_hsv(args.r / 255, args.g / 255, args.b / 255)
        await device.set_hue_saturation(int(h * 360), max(1, int(s * 100)))

        await change_brightness(device, args.brightness)

parser = argparse.ArgumentParser(description="Tapo Room Controller")

subparsers = parser.add_subparsers(dest="mode", required=True)

# Normal mode
normal = subparsers.add_parser("normal")
normal.add_argument("power", type=int)
normal.add_argument("colour", type=str)
normal.add_argument("--brightness", type=int, default=100)

# Custom mode
custom = subparsers.add_parser("custom")
custom.add_argument("power", type=int)
custom.add_argument("r", type=int)
custom.add_argument("g", type=int)
custom.add_argument("b", type=int)
custom.add_argument("--brightness", type=int, default=100)

args = parser.parse_args()
asyncio.run(main())