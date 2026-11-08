"""Nhạc nền tổng hợp 96 BPM và trộn với giọng, chữ chốt rơi đúng phách. Tự sinh, không vướng bản quyền."""
import wave
import numpy as np

SR = 44100
BPM = 96
BEAT = 60 / BPM
LECH = 0.41            # đẩy giọng trễ để "mông mèo" 5,84 s rơi vào phách 10 = 6,25 s
T_CHOT = 6.25
DUR = 8.125            # 13 phách

def _dan(buf, t, tin, g=1.0):
    s = int(t * SR); e = min(len(buf), s + len(tin))
    if 0 <= s < len(buf):
        buf[s:e] += g * tin[:e - s]

def _kick():
    x = np.arange(int(.22 * SR)) / SR
    return np.sin(2 * np.pi * (48 * x + 18 * (1 - np.exp(-x * 30)))) * np.exp(-x * 11)

def _hat():
    x = np.arange(int(.05 * SR)) / SR
    n = np.random.default_rng(3).standard_normal(len(x))
    return np.diff(n, prepend=0) * np.exp(-x * 90) * .4

def _bass(f, d):
    x = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x)) * np.minimum(x * 200, 1) * np.exp(-x * 3.5)

def _pluck(f):
    x = np.arange(int(.3 * SR)) / SR
    return np.sign(np.sin(2 * np.pi * f * x)) * .25 * np.exp(-x * 14)

def nhac():
    """Trống và bass đi đều; 1 phách trước chữ chốt im hẳn, vào lại đúng chữ chốt."""
    b = np.zeros(int(DUR * SR))
    bass = [55.0, 55.0, 65.41, 49.0]
    kk, hh = _kick(), _hat()
    for i in range(13):
        t = i * BEAT
        if 9 <= t / BEAT < 10:
            continue
        if i % 2 == 0:
            _dan(b, t, kk, .85)
            _dan(b, t, _bass(bass[(i // 2) % 4], BEAT * 1.8), .4)
        _dan(b, t + BEAT / 2, hh, .5)
        if i >= 4 and i % 4 == 3:
            _dan(b, t + BEAT / 2, _pluck(330), .3)
    _dan(b, T_CHOT, _kick(), 1.0)
    _dan(b, T_CHOT, _pluck(220), .6)
    return b

def giong(p):
    w = wave.open(p); ch, sw, r0 = w.getnchannels(), w.getsampwidth(), w.getframerate()
    v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    v = v.reshape(-1, ch).mean(axis=1)
    return np.interp(np.arange(0, len(v), r0 / SR), np.arange(len(v)), v)

def tron(p_giong, ra, hieu_ung=()):
    n = int(DUR * SR)
    gi = np.zeros(n); _dan(gi, LECH, giong(p_giong))
    env = np.convolve(np.abs(gi), np.ones(SR // 10) / (SR // 10), "same")
    duck = 1 - .65 * np.clip(env / (env.max() * .25), 0, 1)     # nhạc nhường giọng
    tron = nhac() * .55 * duck + gi
    for t, tin, g in hieu_ung:
        _dan(tron, t, tin, g)
    tron = np.clip(tron / max(1, np.abs(tron).max() / .95), -1, 1)
    o = wave.open(ra, "w"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((tron * 32000).astype(np.int16).tobytes()); o.close()
