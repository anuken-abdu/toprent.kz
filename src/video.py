# -*- coding: utf-8 -*-
"""Видео для фона главной: orig/video/pc.* и orig/video/mob.* → assets/video/hero-pc.mp4, hero-mob.mp4 + кадры hero-pc.jpg, hero-mob.jpg.
Нужен ffmpeg. Звук удаляется, метаданные (в т.ч. геолокация) не копируются, moov в начале файла — видео стартует быстрее.
Запуск: python3 src/video.py, затем python3 src/build.py"""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "orig" / "video", ROOT / "assets" / "video"
JOBS = {"pc": ("hero-pc", "1920:1080", 27), "mob": ("hero-mob", "720:1280", 28)}   # имя, кадр, качество (CRF: больше — легче)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (name, size, crf) in JOBS.items():
        src = next((f for f in sorted(SRC.glob(key + ".*")) if f.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")), None) if SRC.exists() else None
        if not src: print(f"нет файла orig/video/{key}.* — пропуск"); continue
        w, h = size.split(":")
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=25"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", "20", "-an", "-map_metadata", "-1", "-vf", vf,
                        "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(OUT / f"{name}.mp4")], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT / f"{name}.mp4"), "-frames:v", "1", "-q:v", "5", str(OUT / f"{name}.jpg")], check=True)
        print(f"{name}.mp4: {(OUT / f'{name}.mp4').stat().st_size // 1024} КБ")

if __name__ == "__main__":
    main()
