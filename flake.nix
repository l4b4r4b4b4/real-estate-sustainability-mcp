{
  description = "real-estate-sustainability-mcp - MCP server for analyzing building sustainability metrics through Excel, PDF, and standardized frameworks (ESG, LEED, BREEAM, DGNB) with IFC integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        fhsEnv = pkgs.buildFHSEnv {
          name = "real-estate-sustainability-mcp-dev-env";

          targetPkgs = pkgs':
            with pkgs'; [
              # Python and uv
              python312
              uv

              # System libraries (required for some dependencies)
              zlib
              stdenv.cc.cc.lib

              # Shells
              zsh
              bash

              # Linting & Formatting
              ruff
              pre-commit

              # Development tools
              git
              git-lfs
              curl
              wget
              jq
              tree
              httpie
            ];

          profile = ''
            echo "🚀 Real Estate Sustainability Analysis MCP Development Environment"
            echo "==========================================="

            # Create and activate uv virtual environment if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "📦 Creating uv virtual environment..."
              uv venv --python python3.12 --prompt "real-estate-sustainability-mcp"
            fi

            # Activate the virtual environment
            source .venv/bin/activate

            # Set a recognizable name for IDEs
            export VIRTUAL_ENV_PROMPT="real-estate-sustainability-mcp"

            # Sync dependencies
            if [ -f "pyproject.toml" ]; then
              echo "🔄 Syncing dependencies..."
              uv sync --quiet
            else
              echo "⚠️  No pyproject.toml found. Run 'uv init' to create project."
            fi

            # Install pre-commit hooks if not already installed
            if [ -f ".pre-commit-config.yaml" ]; then
              if [ ! -f ".git/hooks/pre-commit" ]; then
                echo "🔧 Installing pre-commit hooks..."
                uv run pre-commit install --install-hooks
              else
                echo "✅ Pre-commit hooks: installed"
              fi
            fi

            echo ""
            echo "✅ Python: $(python --version)"
            echo "✅ uv:     $(uv --version)"
            echo "✅ Virtual environment: activated (.venv)"
            echo "✅ PYTHONPATH: $PWD/src:$PWD"
          '';

          runScript = ''
            # Set shell for the environment
            SHELL=${pkgs.zsh}/bin/zsh

            # Set PYTHONPATH to project root for module imports
            export PYTHONPATH="$PWD/src:$PWD"
            export SSL_CERT_FILE="/etc/ssl/certs/ca-bundle.crt"

            echo ""
            echo "🚀 Real Estate Sustainability Analysis MCP Quick Reference:"
            echo ""
            echo "🔧 Development:"
            echo "  uv sync                    - Sync dependencies"
            echo "  uv run pytest              - Run tests"
            echo "  uv run ruff check .        - Lint code"
            echo "  uv run ruff format .       - Format code"
            echo "  uv lock --upgrade          - Update all dependencies"
            echo ""
            echo "📦 Package Management:"
            echo "  uv add <package>           - Add runtime dependency"
            echo "  uv add --dev <package>     - Add dev dependency"
            echo "  uv remove <package>        - Remove dependency"
            echo ""
            echo "🚀 Run Server:"
            echo "  uv run real-estate-sustainability-mcp        - Run MCP server (stdio)"
            echo "  uv run real-estate-sustainability-mcp --transport sse --port 8000"
            echo ""
            echo "🔗 mcp-refcache dependency:"
            echo "  Installed from: git+https://github.com/l4b4r4b4b4/mcp-refcache"
            echo ""
            echo "🚀 Ready to build!"
            echo ""

            # Start zsh shell
            exec ${pkgs.zsh}/bin/zsh
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            exec ${fhsEnv}/bin/real-estate-sustainability-mcp-dev-env
          '';
        };

        packages.default = pkgs.python312;
      }
    );
}
