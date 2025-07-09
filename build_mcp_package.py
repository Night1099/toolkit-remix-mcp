#!/usr/bin/env python3
"""
Build script for RTX Remix Toolkit MCP Server package
"""

import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    return result


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    paths_to_clean = [
        "build",
        "dist", 
        "*.egg-info",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache"
    ]
    
    for path_pattern in paths_to_clean:
        for path in Path(".").glob(path_pattern):
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  Removed directory: {path}")
                else:
                    path.unlink()
                    print(f"  Removed file: {path}")


def check_dependencies():
    """Check and install build dependencies."""
    print("📋 Checking build dependencies...")
    
    required_packages = ["build", "wheel", "setuptools"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} is available")
        except ImportError:
            print(f"  📦 Installing {package}...")
            run_command([sys.executable, "-m", "pip", "install", package])


def validate_package_files():
    """Validate that required package files exist."""
    print("✅ Validating package files...")
    
    required_files = [
        "mcp_server.py",
        "setup.py", 
        "pyproject.toml",
        "README-MCP.md",
        "requirements-mcp.txt",
        "MANIFEST.in"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        sys.exit(1)


def build_package():
    """Build the package."""
    print("🔨 Building package...")
    
    # Build both wheel and source distribution
    run_command([sys.executable, "-m", "build"])
    
    # Check that files were created
    dist_path = Path("dist")
    if not dist_path.exists():
        print("❌ dist/ directory not created")
        sys.exit(1)
    
    wheel_files = list(dist_path.glob("*.whl"))
    tar_files = list(dist_path.glob("*.tar.gz"))
    
    if not wheel_files or not tar_files:
        print("❌ Build artifacts missing")
        sys.exit(1)
    
    print(f"✅ Package built successfully:")
    for wheel in wheel_files:
        print(f"  📦 {wheel.name}")
    for tar in tar_files:
        print(f"  📦 {tar.name}")
    
    return wheel_files, tar_files


def generate_install_instructions(wheel_files, tar_files):
    """Generate installation instructions."""
    print("\n📋 Installation Instructions")
    print("=" * 50)
    
    wheel_file = wheel_files[0] if wheel_files else None
    tar_file = tar_files[0] if tar_files else None
    
    print("Local Installation:")
    if wheel_file:
        print(f"  pip install {wheel_file}")
    
    print("\nDevelopment Installation:")
    print("  pip install -e .")
    
    print("\nUsage with Claude Code:")
    print("  claude mcp add rtx-remix-toolkit python rtx-remix-mcp")
    
    print("\nUsage standalone:")
    print("  rtx-remix-mcp --help")
    
    if tar_file and wheel_file:
        print(f"\nTo publish to PyPI:")
        print(f"  twine check dist/*")
        print(f"  twine upload dist/*")
    
    print(f"\nPackage files created in dist/:")
    for file in Path("dist").glob("*"):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  {file.name} ({size_mb:.2f} MB)")


def main():
    """Main build function."""
    print("🏗️  RTX Remix Toolkit MCP Server Package Builder")
    print("=" * 55)
    
    # Check that we're in the right directory
    if not Path("mcp_server.py").exists():
        print("❌ Must run from the toolkit-remix repository root")
        sys.exit(1)
    
    try:
        # Clean previous builds
        clean_build_artifacts()
        
        # Check dependencies
        check_dependencies()
        
        # Validate files
        validate_package_files()
        
        # Build package
        wheel_files, tar_files = build_package()
        
        # Generate instructions
        generate_install_instructions(wheel_files, tar_files)
        
        print("\n🎉 Build completed successfully!")
        print("\nNext steps:")
        print("  1. Test the package: python test_mcp_package.py")
        print("  2. Install locally: pip install dist/*.whl")
        print("  3. Test with Claude Code: claude mcp add rtx-remix-toolkit python rtx-remix-mcp")
        
    except KeyboardInterrupt:
        print("\n❌ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()