import sys, subprocess, math
import numpy as np
from PIL import Image
from multiprocessing import Pool
from lib import W, H, FPS, smooth_noise, sstep
import scenes as S

XF = 0.12
_post = {}


def post_assets():
    if not _post:
        _post["fog"] = smooth_noise(1400, 2400, 500, 1)
        _post["fog2"] = smooth_noise(1400, 2400, 260, 2)
        y, x = np.mgrid[0:H, 0:W]
        d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.7)) ** 2)
        _post["vig"] = np.clip(1 - 0.55 * d ** 2.2, 0.25, 1).astype(np.float32)[..., None]
        rng = np.random.default_rng(0)
        _post["grain"] = [rng.normal(0, 6, (H, W, 1)).astype(np.float32) for _ in range(6)]
    return _post


def scene_at(i, t):
    lt = max(0.0, t - S.B[i])
    dur = S.B[i + 1] - S.B[i]
    return S.SCENES[i](lt, dur)


def fog_layer(t, i):
    p = post_assets()
    tint, k = S.FOG[i]
    ox = int(150 + 120 * math.sin(t * 0.07) + t * 9) % 300
    oy = int(200 + t * 6) % 400
    f1 = p["fog"][oy:oy + H, ox:ox + W]
    ox2 = int(300 - t * 14) % 300
    f2 = p["fog2"][oy // 2:oy // 2 + H, ox2:ox2 + W]
    return ((0.6 * f1 + 0.4 * f2) ** 1.5 * k)[..., None], np.array(tint, np.float32)


def frame(fi):
    t = fi / FPS
    n = len(S.SCENES)
    i = 0
    while i < n - 1 and t >= S.B[i + 1]:
        i += 1
    fi_idx = i
    j = None
    if i < n - 1 and t > S.B[i + 1] - XF:
        j = i
    elif i > 0 and t < S.B[i] + XF:
        j = i - 1
    if j is None:
        img = scene_at(i, t)
    else:
        u = sstep(S.B[j + 1] - XF, S.B[j + 1] + XF, t)
        img = Image.blend(scene_at(j, t), scene_at(j + 1, t), u)
    p = post_assets()
    a = np.asarray(img, dtype=np.float32)
    fa, tint = fog_layer(t, fi_idx)
    a = a * (1 - fa) + tint * fa
    # colour grade: teal shadows, slight desaturation
    lum = a.mean(axis=2, keepdims=True)
    a = a * 0.88 + lum * 0.12
    a[..., 2:3] += (1 - lum / 255) * 6
    a[..., 0:1] -= (1 - lum / 255) * 3
    a = a * p["vig"] + p["grain"][fi % 6]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if t >= S.TITLE_T - 0.05:
        S.title_card(out, sstep(S.TITLE_T - 0.05, S.TITLE_T + 0.35, t))
    return out


def render_chunk(args):
    k, f0, f1, path = args
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        pr.stdin.write(frame(fi).tobytes())
    pr.stdin.close()
    pr.wait()
    return path


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = [frame(int(t * FPS)).resize((270, 480)) for t in ts]
        cols = 6
        rows = math.ceil(len(ims) / cols)
        sheet = Image.new("RGB", (cols * 270, rows * 480))
        for j, im in enumerate(ims):
            sheet.paste(im, ((j % cols) * 270, (j // cols) * 480))
        sheet.save(sys.argv[3])
    else:
        total = int(round(S.END * FPS))
        nw = 4
        chunks = []
        per = math.ceil(total / (nw * 3))
        for k, f0 in enumerate(range(0, total, per)):
            chunks.append((k, f0, min(total, f0 + per), f"chunk_{k:02d}.mp4"))
        with Pool(nw) as pool:
            res = pool.map(render_chunk, chunks)
        with open("chunks.txt", "w") as f:
            for r in res:
                f.write(f"file '{r}'\n")
        print("frames", total)
