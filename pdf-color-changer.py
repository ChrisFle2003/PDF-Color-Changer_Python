import argparse
import io
import sys
from typing import Tuple

import fitz  # PyMuPDF
from PIL import Image


def map_dark_to_magenta(
    image: Image.Image,
    threshold: int = 100,
    preserve_colored: bool = True,
    magenta_rgb: Tuple[int, int, int] = (90, 0, 55),
) -> Image.Image:
    """
    Ersetzt dunkle Pixel durch dunkles Magenta.

    threshold:
        Alle Pixel, deren R,G,B <= threshold sind, gelten als "nahe Schwarz".
    preserve_colored:
        Wenn True, bleiben bunte Elemente weitgehend unangetastet; nur wirklich dunkle
        Pixel werden ersetzt.
    magenta_rgb:
        Zielton. Standard ist absichtlich dunkel, damit es schwarzähnlich wirkt.
    """
    img = image.convert("RGB")
    px = img.load()
    width, height = img.size

    mr, mg, mb = magenta_rgb

    for y in range(height):
        for x in range(width):
            r, g, b = px[x, y]

            # Nahe Weiß unverändert lassen
            if r > 245 and g > 245 and b > 245:
                continue

            # Pixel-Helligkeit (0..255), niedriger = dunkler
            luminance = int(0.299 * r + 0.587 * g + 0.114 * b)

            # Strikte Erkennung "schwarz / sehr dunkel"
            is_dark = (r <= threshold and g <= threshold and b <= threshold)

            # Zusätzlich toleranter Bereich für fast-schwarz mit wenig Farbstich
            near_neutral_dark = (
                luminance <= threshold
                and abs(r - g) <= 20
                and abs(r - b) <= 20
                and abs(g - b) <= 20
            )

            if preserve_colored:
                if not (is_dark or near_neutral_dark):
                    continue
            else:
                if luminance > threshold:
                    continue

            # Stärke beibehalten: dunkle Stellen bleiben dunkler
            # scale = 1 für schwarz, kleiner für hellere Grautöne
            scale = max(0.18, 1.0 - (luminance / max(1, threshold + 40)))

            nr = int(mr * scale)
            ng = int(mg * scale)
            nb = int(mb * scale)

            # Etwas Mindestdichte, damit es nicht zu blass wird
            nr = max(nr, 25)
            nb = max(nb, 12)

            px[x, y] = (nr, ng, nb)

    return img


def convert_pdf(
    input_pdf: str,
    output_pdf: str,
    dpi: int = 200,
    threshold: int = 100,
    magenta_rgb: Tuple[int, int, int] = (90, 0, 55),
):
    src = fitz.open(input_pdf)
    out = fitz.open()

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(src):
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        converted = map_dark_to_magenta(
            img,
            threshold=threshold,
            preserve_colored=True,
            magenta_rgb=magenta_rgb,
        )

        buf = io.BytesIO()
        # PNG bewahrt Kanten besser; PDF wird größer, aber sauberer
        converted.save(buf, format="PNG")
        img_bytes = buf.getvalue()

        rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        new_page = out.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=img_bytes)

        print(f"Seite {i+1}/{len(src)} verarbeitet", file=sys.stderr)

    # Deflate komprimiert Streams im PDF
    out.save(output_pdf, deflate=True, garbage=4)
    out.close()
    src.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="PDF: Schwarz/dunkel -> dunkles Magenta, Ausgabe wieder als PDF"
    )
    parser.add_argument("input_pdf", help="Pfad zur Eingabe-PDF")
    parser.add_argument("output_pdf", help="Pfad zur Ausgabe-PDF")
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Render-Auflösung pro Seite (Standard: 200)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Schwellwert für 'nahe Schwarz' (Standard: 100, typischer Bereich 80-130)",
    )
    parser.add_argument(
        "--magenta-r",
        type=int,
        default=90,
        help="Rot-Anteil des Ziel-Magenta (Standard: 90)",
    )
    parser.add_argument(
        "--magenta-g",
        type=int,
        default=0,
        help="Grün-Anteil des Ziel-Magenta (Standard: 0)",
    )
    parser.add_argument(
        "--magenta-b",
        type=int,
        default=55,
        help="Blau-Anteil des Ziel-Magenta (Standard: 55)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not (0 <= args.threshold <= 255):
        raise SystemExit("Fehler: --threshold muss zwischen 0 und 255 liegen.")

    rgb = (args.magenta_r, args.magenta_g, args.magenta_b)
    for value in rgb:
        if not (0 <= value <= 255):
            raise SystemExit("Fehler: RGB-Werte müssen zwischen 0 und 255 liegen.")

    convert_pdf(
        input_pdf=args.input_pdf,
        output_pdf=args.output_pdf,
        dpi=args.dpi,
        threshold=args.threshold,
        magenta_rgb=rgb,
    )
    print(f"Fertig: {args.output_pdf}")


if __name__ == "__main__":
    main()