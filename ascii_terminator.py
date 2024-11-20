# Study and based by "https://github.com/tpoff/Python-Gif-Ascii-Animator/tree/master"
# Thanks.
from PIL import Image, ImageFont
import os
import time
import argparse
import platform

custom_chars = {
    "`": " ",
    ".": " ",
}

def extract_gif_frames(gif, fillEmpty=False):
    frames=[]
    try:
        while True:
            gif.seek(gif.tell()+1)
            new_frame = Image.new('RGBA',gif.size)
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            
            #check if we are painting over a canvas
            if fillEmpty:
                canvas=Image.new('RGBA', new_frame.size, (255,255,255,0))
                canvas.paste(new_frame, mask=new_frame)
                new_frame=canvas
            
            
            frames.append(new_frame)
    except EOFError:
        pass # end of sequence
    return frames


def convert_image_to_ascii(image: Image.Image, intensity: int):
    font = ImageFont.load_default()
    (chrx, chry) = font.getsize(chr(32))

    weights = []
    for i in range(32, 127):
        chrImage = font.getmask(chr(i))
        ctr = 0
        for y in range(chry):
            for x in range(chrx):
                if chrImage.getpixel((x, y)) > 0:
                    ctr += 1
        weights.append(float(ctr) / (chrx * chry))
    
    output = ""
    (imgx, imgy) = image.size
    imgx = int(imgx / chrx)
    imgy = int(imgy / chry)

    # NEAREST/BILINEAR/BICUBIC/ANTIALIAS
    image = image.resize((imgx, imgy), Image.ANTIALIAS)
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    image_gray = image.copy().convert("L")

    pixels = image.load()
    pixels_gray = image_gray.load()
    for y in range(imgy):
        for x in range(imgx):
            r, g, b, a = pixels[x, y]
            if a == 0:
                output += " "
                continue

            w = float(pixels_gray[x, y]) / 255 / intensity
            # find closest weight match
            wf = -1.0; k = -1
            for i in range(len(weights)):
                if abs(weights[i] - w) <= abs(wf - w):
                    wf = weights[i]; k = i

            char = chr(k + 32)
            if char in custom_chars:
                char = custom_chars[char]
            color = f"\033[38;2;{r};{g};{b}m"
            output += f"{color}{char}"

        output += "\n"
    return output


def convert_frames_to_ascii(frames, intensity: int):
    ascii_frames = []
    for frame in frames:
        new_frame = convert_image_to_ascii(frame, intensity)
        ascii_frames.append(new_frame)
    return ascii_frames


def animate_ascii(ascii_frames, frame_pause=.02, num_iterations=15, system_name="Windows", clear_prev_frame=True):
    for i in range(num_iterations):
        for frame in ascii_frames:
            print(frame)
            time.sleep(frame_pause)
            if clear_prev_frame:      
                if system_name == "Windows":
                    os.system('cls')
                else:
                    os.system('clear')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Gif")
    parser.add_argument("-i", "--intensity", type=int, default=6)
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Erreur : The file '{args.file}' don't exist.")
        exit(1)

    im = Image.open(args.file)
    frames = extract_gif_frames(im, fillEmpty=True)
    ascii_frames = convert_frames_to_ascii(frames, args.intensity)

    animate_ascii(ascii_frames, num_iterations=200, system_name=platform.system())
