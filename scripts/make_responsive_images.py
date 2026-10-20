#!/usr/bin/env python3
"""Gera versões de 800 px (-800w.webp) das imagens usadas nas páginas 2026.

O builder (build_pages_2026.py) só usa srcset quando a versão existe.
Uso: python3 scripts/make_responsive_images.py
"""
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = list((ROOT / "content" / "pages").rglob("*.html")) + [ROOT / "index.html"]


def referenced_images() -> set[Path]:
    found = set()
    for page in SOURCES:
        text = page.read_text(encoding="utf-8")
        for src in re.findall(r'(/assets/[^"\s,]+\.(?:jpe?g|png|webp))', text):
            webp = ROOT / re.sub(r"\.(jpe?g|png)$", ".webp", src).lstrip("/")
            if webp.exists() and not webp.stem.endswith("-800w"):
                found.add(webp)
    return found


def main() -> None:
    made = 0
    for webp in sorted(referenced_images()):
        target = webp.with_name(webp.stem + "-800w.webp")
        with Image.open(webp) as im:
            if im.width <= 900:
                continue
            if target.exists():
                continue
            height = round(im.height * 800 / im.width)
            im.convert("RGB").resize((800, height), Image.LANCZOS).save(target, "WEBP", quality=78, method=6)
            made += 1
            print(f"{target.relative_to(ROOT)}: {webp.stat().st_size // 1024} KB -> {target.stat().st_size // 1024} KB")
    print(f"{made} versões criadas")


if __name__ == "__main__":
    main()
