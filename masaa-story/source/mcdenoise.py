"""
Motion-compensated temporal denoising (the approach used by professional denoisers
such as Neat Video): every frame is aligned to its neighbours with dense optical flow,
the aligned neighbours are averaged with per-pixel robust weights (pixels that do not
match — occlusions, moving people, flow errors — are rejected), and residual chroma
noise is removed with an edge-preserving filter. Real detail is kept because it is
consistent across frames; noise is not, so it averages out (~1/sqrt(N)).

Works on scene-linear float RGB frames; alignment is computed on a perceptual
(log-encoded) luma so that dark regions align as well as bright ones.
"""
import numpy as np
import cv2

H, W = 1920, 1080


def _percept(lin):
    l = lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722
    p = np.log2(np.maximum(l, 1e-5) * 64 + 1) / np.log2(64 * 6 + 1)  # ~0..1
    return p


class MCDenoiser:
    def __init__(self, radius=2, strength=1.0):
        self.r = radius
        self.k = strength
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self.dis.setFinestScale(1)
        gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.gx, self.gy = gx, gy

    def _flow(self, a8, b8):
        return self.dis.calc(a8, b8, None)

    def denoise(self, frames, c):
        """frames: list of linear frames (window), c: index of the centre frame"""
        ref = frames[c]
        pref = _percept(ref)
        ref8 = (np.clip(pref, 0, 1) * 255).astype(np.uint8)
        # noise level estimate on the perceptual luma (robust MAD of a high-pass)
        hp = pref - cv2.GaussianBlur(pref, (0, 0), 1.5)
        sel = (pref > 0.12) & (pref < 0.7)
        v = hp[sel] if sel.sum() > 5000 else hp.ravel()
        sigma = max(1.4826 * np.median(np.abs(v - np.median(v))), 0.006)
        acc = ref.copy()
        wsum = np.ones((H, W), np.float32)
        for j, f in enumerate(frames):
            if j == c or f is None:
                continue
            pj = _percept(f)
            f8 = (np.clip(pj, 0, 1) * 255).astype(np.uint8)
            flow = self._flow(ref8, f8)
            mx, my = self.gx + flow[..., 0], self.gy + flow[..., 1]
            wf = cv2.remap(f, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            wp = cv2.remap(pj, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            d = cv2.GaussianBlur(np.abs(wp - pref), (0, 0), 1.2)
            dist = abs(j - c)
            w = np.exp(-(d / (2.2 * sigma * self.k)) ** 2) * (0.9 ** (dist - 1))
            acc += wf * w[..., None]
            wsum += w
        out = acc / wsum[..., None]
        return out, sigma


def chroma_clean(lin, strength=1.0):
    """edge-preserving chroma denoise: smooth colour-difference channels guided by luma"""
    l = lin[..., 0] * 0.2126 + lin[..., 1] * 0.7152 + lin[..., 2] * 0.0722
    eps = 1e-4
    cr = (lin[..., 0] + eps) / (l + eps)
    cb = (lin[..., 2] + eps) / (l + eps)
    guide = (np.log2(np.maximum(l, 1e-5) * 64 + 1) / 8.6).astype(np.float32)
    s = int(round(6 * strength)) * 2 + 1
    gf = lambda x: cv2.ximgproc.guidedFilter(guide, x.astype(np.float32), s, 2e-3) if hasattr(cv2, "ximgproc") else cv2.bilateralFilter(x.astype(np.float32), 9, 0.08, 7)
    cr2, cb2 = gf(cr), gf(cb)
    # only in darker areas, where chroma noise lives; bright colour detail is kept
    m = np.clip(1 - (guide - 0.25) / 0.35, 0, 1)
    cr = cr * (1 - m) + cr2 * m
    cb = cb * (1 - m) + cb2 * m
    r = cr * (l + eps) - eps
    b = cb * (l + eps) - eps
    g = (l - 0.2126 * r - 0.0722 * b) / 0.7152
    return np.maximum(np.stack([r, g, b], -1), 0).astype(np.float32)
