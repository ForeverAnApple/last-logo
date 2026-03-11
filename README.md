# last.dev logo

**Programmatic SVG logo generator -- isometric logo for last.dev.**

## Setup

### Nix + direnv (recommended)

```sh
direnv allow   # sets up Python 3.13 venv + deps automatically
```

### Manual

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
python src/icon.py       # writes output/icon-{light,dark}.svg
python src/wordmark.py   # writes output/wordmark-{light,dark}.svg
python src/logo.py       # writes output/logo-{light,dark}.svg
```

## Project Structure

```
src/           Python generators
  icon.py        standalone cube icon
  wordmark.py    isometric "LAST" text
  logo.py        combined icon + wordmark
output/        generated assets (SVG + PNG)
```

## Dependencies

| Package    | Purpose              |
| ---------- | -------------------- |
| svgwrite   | SVG generation       |
| lxml       | XML processing       |
| cairosvg   | SVG to PNG export    |
| pillow     | Image post-processing|
