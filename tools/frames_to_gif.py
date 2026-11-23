"""Turns a folder of timed screenshots (NNNN_<ms>.jpg) into a looping GIF for the README.

    python tools/frames_to_gif.py <frames dir> <out.gif> [--width 960] [--speed 1.0] [--hold 2500]

One palette is shared by every frame so colours don't flicker, frames that look the same are
merged, and the last frame is held so the result can be read before the loop starts again.
"""

import argparse
import re
from pathlib import Path

from PIL import Image, ImageChops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--hold", type=int, default=2500)
    ap.add_argument("--min-ms", type=int, default=70)
    ap.add_argument("--colors", type=int, default=128)
    a = ap.parse_args()

    files = sorted(Path(a.frames).glob("*.jpg"))
    stamps = [int(re.search(r"_(\d+)\.jpg$", f.name).group(1)) for f in files]

    frames, times = [], []
    for f, t in zip(files, stamps):
        im = Image.open(f).convert("RGB")
        h = round(im.height * a.width / im.width)
        frames.append(im.resize((a.width, h), Image.LANCZOS))
        times.append(t / a.speed)

    # A shared palette from a spread of frames.
    sample = frames[:: max(1, len(frames) // 12)]
    sheet = Image.new("RGB", (a.width, sum(s.height for s in sample)))
    y = 0
    for s in sample:
        sheet.paste(s, (0, y))
        y += s.height
    palette = sheet.quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT)

    out, durations = [], []
    last = None
    for i, im in enumerate(frames):
        q = im.quantize(palette=palette, dither=Image.Dither.NONE)
        next_t = times[i + 1] if i + 1 < len(times) else times[i] + a.hold
        d = next_t - times[i]
        same = last is not None and ImageChops.difference(q.convert("RGB"), last.convert("RGB")).getbbox() is None
        if out and (same or durations[-1] < a.min_ms):
            if same:
                durations[-1] += d
                continue
        out.append(q)
        durations.append(d)
        last = q
    durations[-1] = max(durations[-1], a.hold)
    durations = [max(20, round(d / 10) * 10) for d in durations]

    out[0].save(a.out, save_all=True, append_images=out[1:], duration=durations, loop=0,
                optimize=False, disposal=1)
    size = Path(a.out).stat().st_size / 1e6
    print(f"{a.out}: {len(out)} frames, {sum(durations) / 1000:.1f}s, {size:.1f} MB")


if __name__ == "__main__":
    main()
