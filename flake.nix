{
  description = "last.dev logo - SVG generation with Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        python = pkgs.python313;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.uv

            # System deps for cairosvg / pillow
            pkgs.cairo
            pkgs.pkg-config
            pkgs.gobject-introspection
            pkgs.libffi
          ];

          shellHook = ''
            if [ ! -d .venv ]; then
              echo "Creating venv..."
              uv venv .venv
            fi
            source .venv/bin/activate

            if [ ! -f .venv/.installed ]; then
              echo "Installing Python deps..."
              uv pip install -r requirements.txt
              touch .venv/.installed
            fi

            echo "last.dev logo environment"
            echo "========================="
            echo "Python: $(python --version)"
          '';
        };
      }
    );
}
