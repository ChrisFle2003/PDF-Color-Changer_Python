# PDF Color Changer

Ein kleines Python-Tool, das schwarze oder sehr dunkle Bereiche in einer PDF-Datei durch ein dunkles, schwarzähnliches Magenta ersetzt.

Ziel ist es, PDFs so umzuwandeln, dass beim Drucken weniger oder keine schwarze Tinte verwendet wird, während der Text weiterhin gut lesbar bleibt.

## Features

- Wandelt dunkle bzw. fast schwarze Pixel in dunkles Magenta um
- Erhält helle und weiße Bereiche
- Schont farbige Inhalte weitgehend
- Gibt das Ergebnis wieder als PDF aus
- Anpassbare DPI, Schwellwerte und Magenta-Farbe
- CLI-basiert und einfach nutzbar

## Installation

```bash
pip install pymupdf pillow
````

## Nutzung

```bash
python3 pdf-color-changer.py input.pdf output.pdf
```

Beispiel:

```bash
python3 pdf-color-changer.py dokument.pdf dokument-magenta.pdf
```

## Optionen

```bash
python3 pdf-color-changer.py input.pdf output.pdf --dpi 200 --threshold 100
```

### Verfügbare Parameter

| Option        | Beschreibung                    | Standard |
| ------------- | ------------------------------- | -------- |
| `--dpi`       | Render-Auflösung der PDF-Seiten | `200`    |
| `--threshold` | Schwellwert für dunkle Pixel    | `100`    |
| `--magenta-r` | Rot-Anteil der Zielfarbe        | `90`     |
| `--magenta-g` | Grün-Anteil der Zielfarbe       | `0`      |
| `--magenta-b` | Blau-Anteil der Zielfarbe       | `55`     |

## Beispiel mit eigener Farbe

```bash
python3 pdf-color-changer.py input.pdf output.pdf \
  --magenta-r 100 \
  --magenta-g 0 \
  --magenta-b 70
```

## Hinweise

* Höhere DPI-Werte erzeugen bessere Qualität, aber auch größere PDF-Dateien.
* Ein niedrigerer `threshold` verändert nur sehr dunkle Bereiche.
* Ein höherer `threshold` kann auch dunkelgraue Bereiche stärker einfärben.
* Das Tool rendert jede PDF-Seite als Bild und baut daraus eine neue PDF.

## Zweck

Dieses Projekt ist vor allem für PDFs gedacht, die gedruckt werden sollen, wenn schwarze Tinte gespart oder durch eine dunkle Farbe ersetzt werden soll.
