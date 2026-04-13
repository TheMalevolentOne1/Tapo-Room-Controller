import asyncio
import os
import colorsys
from dotenv import load_dotenv
from tapo import ApiClient
import argparse

COLOUR_MAP = {
    # Primary
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),

    # White / temperature
    "white": (255, 255, 255),
    "warm": (255, 214, 170),
    "cool_white": (240, 250, 255),
    "daylight": (255, 255, 240),

    # Secondary colours
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),

    # Extended warm tones
    "orange": (255, 165, 0),
    "amber": (255, 191, 0),
    "gold": (255, 215, 0),
    "peach": (255, 218, 185),
    "coral": (255, 127, 80),

    # Pinks / reds
    "pink": (255, 192, 203),
    "hot_pink": (255, 105, 180),
    "rose": (255, 0, 127),
    "crimson": (220, 20, 60),
    "maroon": (128, 0, 0),

    # Purples
    "purple": (128, 0, 128),
    "violet": (138, 43, 226),
    "lavender": (230, 230, 250),
    "plum": (142, 69, 133),

    # Blues
    "navy": (0, 0, 128),
    "sky_blue": (135, 206, 235),
    "deep_sky_blue": (0, 191, 255),
    "royal_blue": (65, 105, 225),
    "steel_blue": (70, 130, 180),

    # Greens
    "lime": (0, 255, 0),
    "lime_green": (50, 205, 50),
    "forest_green": (34, 139, 34),
    "sea_green": (46, 139, 87),
    "mint": (189, 252, 201),

    # Earth tones
    "brown": (139, 69, 19),
    "sienna": (160, 82, 45),
    "tan": (210, 180, 140),
    "olive": (128, 128, 0),

    # Grayscale (important for lighting systems)
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
    "dark_gray": (64, 64, 64),
    "light_gray": (211, 211, 211),
    "silver": (192, 192, 192),
}

async def setup_light():
    load_dotenv()

    try:
        client = ApiClient(os.getenv("TAPO_USERNAME"), os.getenv("TAPO_PASSWORD"))
    except TypeError:
        print("Verify existence of .env with Tapo Creds")
        return

    device = await client.l530(os.getenv("LOCAL_IP"))
    return device

async def is_device_on(device):
    info = await device.get_device_info()
    if not info.device_on:
        return False
    else:
        return True

global power
global brightness
global colour

async def change_power(device, power):
    if await is_device_on(device) and power:
        print("Device is already on!")
        return

    # Power control
    if power:
        await device.on()
        print("Light On")
    else:
        await device.off()
        print("Light Off")
    return

async def change_brightness(device, brightness):
    # Brightness
    brightness = max(1, min(100, int(brightness)))
    await device.set_brightness(brightness)
    print("Brightness changed to {}".format(brightness))
    return

async def change_colour(device, colour):
    if colour == "white":
        await device.set_color_temperature(6500)
        return
    elif colour == "warm":
        await device.set_color_temperature(2700)

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
        if args.power is not None:
            await change_power(device, args.power)

        if args.colour is not None:
            await change_colour(device, args.colour)

        if args.brightness is not None:
            await change_brightness(device, args.brightness)

        return
    elif args.mode == "custom":
        # Convert RGB → HSV (same logic you used)
        h, s, _ = colorsys.rgb_to_hsv(args.r / 255, args.g / 255, args.b / 255)
        await device.set_hue_saturation(int(h * 360), max(1, int(s * 100)))
        await change_brightness(device, args.brightness)

        return

parser = argparse.ArgumentParser(description="Tapo Room Controller")

subparsers = parser.add_subparsers(dest="mode", required=True)

# Normal mode
normal = subparsers.add_parser("normal")
normal.add_argument("--power", type=int, default=1)
COLOUR_HELP = "\nAvailable colours:\n" + "\n".join(f"  - {c}" for c in COLOUR_MAP.keys())

normal.add_argument("--colour",
    type=str,
    default=None,
    help="Set light colour." + COLOUR_HELP)
normal.add_argument("--brightness", type=int, default=None)

# Custom mode
custom = subparsers.add_parser("custom")
custom.add_argument("r", type=int)
custom.add_argument("g", type=int)
custom.add_argument("b", type=int)
custom.add_argument("brightness", type=int, nargs="?")

args = parser.parse_args()
asyncio.run(main())