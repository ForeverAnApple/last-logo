# last.dev logo

**Programmatic SVG logo generator -- isometric logo for last.dev.**

Output: `cube.svg` (300x300). See it in the repo after running the script.

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
python cube.py   # writes cube.svg
```

## Dependencies

| Package    | Purpose              |
| ---------- | -------------------- |
| svgwrite   | SVG generation       |
| lxml       | XML processing       |
| cairosvg   | SVG to PNG export    |
| pillow     | Image post-processing|
