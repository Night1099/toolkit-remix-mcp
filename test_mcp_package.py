#!/usr/bin/env python3
"""
Test script for RTX Remix Toolkit MCP Server package
"""

import subprocess
import sys
import tempfile
import venv
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


def test_package_build():
    """Test building the package."""
    print("📦 Testing package build...")
    
    # Clean previous builds
    for path in ["build", "dist", "*.egg-info"]:
        run_command(["rm", "-rf", path], check=False)
    
    # Build the package
    run_command([sys.executable, "-m", "build"])
    
    # Check that dist files were created
    dist_path = Path("dist")
    if not dist_path.exists():
        print("❌ dist/ directory not created")
        sys.exit(1)
    
    wheel_files = list(dist_path.glob("*.whl"))
    tar_files = list(dist_path.glob("*.tar.gz"))
    
    if not wheel_files:
        print("❌ No wheel file created")
        sys.exit(1)
    
    if not tar_files:
        print("❌ No source distribution created")
        sys.exit(1)
    
    print(f"✅ Package built successfully:")
    print(f"   Wheel: {wheel_files[0].name}")
    print(f"   Source: {tar_files[0].name}")
    
    return wheel_files[0], tar_files[0]


def test_package_install(wheel_file):
    """Test installing the package in a virtual environment."""
    print("🔧 Testing package installation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        
        # Create virtual environment
        print(f"Creating virtual environment at {venv_path}")
        venv.create(venv_path, with_pip=True)
        
        # Get python executable
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Install the package
        print(f"Installing package from {wheel_file}")
        run_command([str(pip_exe), "install", str(wheel_file)])
        
        # Test import
        print("Testing import...")
        result = run_command([str(python_exe), "-c", "import mcp_server; print('Import successful')"])
        if "Import successful" not in result.stdout:
            print("❌ Import test failed")
            sys.exit(1)
        
        # Test entry points
        print("Testing entry points...")
        for entry_point in ["rtx-remix-mcp", "remix-mcp"]:
            if sys.platform == "win32":
                cmd_path = venv_path / "Scripts" / f"{entry_point}.exe"
            else:
                cmd_path = venv_path / "bin" / entry_point
            
            if not cmd_path.exists():
                print(f"❌ Entry point {entry_point} not found at {cmd_path}")
                sys.exit(1)
            
            # Test --version flag
            result = run_command([str(cmd_path), "--version"], check=False)
            if result.returncode != 0:
                print(f"❌ Entry point {entry_point} --version failed")
                print(f"STDERR: {result.stderr}")
                sys.exit(1)
            
            if "RTX Remix Toolkit MCP Server" not in result.stdout:
                print(f"❌ Entry point {entry_point} version output incorrect")
                print(f"Output: {result.stdout}")
                sys.exit(1)
        
        print("✅ Package installation test passed")


def test_mcp_functionality():
    """Test basic MCP server functionality."""
    print("🔍 Testing MCP server functionality...")
    
    # Create a minimal test to verify the server can start
    test_script = """
import sys
sys.path.insert(0, '.')
import mcp_server

# Test that main resources and tools are available
mcp = mcp_server.mcp

# Check resources
resources = [resource.name for resource in mcp.list_resources()]
expected_resources = ["repo://structure", "repo://build_commands"]

for expected in expected_resources:
    if expected not in resources:
        print(f"Missing resource: {expected}")
        sys.exit(1)

# Check tools
tools = [tool.name for tool in mcp.list_tools()]
expected_tools = [
    "list_extensions",
    "analyze_extension", 
    "create_extension_template",
    "run_build",
    "run_tests",
    "format_code",
    "lint_code",
    "search_code",
    "get_extension_dependencies"
]

for expected in expected_tools:
    if expected not in tools:
        print(f"Missing tool: {expected}")
        sys.exit(1)

print("MCP server functionality test passed")
"""
    
    result = run_command([sys.executable, "-c", test_script])
    if "MCP server functionality test passed" not in result.stdout:
        print("❌ MCP functionality test failed")
        sys.exit(1)
    
    print("✅ MCP server functionality test passed")


def main():
    """Main test function."""
    print("🧪 RTX Remix Toolkit MCP Server Package Test")
    print("=" * 50)
    
    # Check that we're in the right directory
    if not Path("mcp_server.py").exists():
        print("❌ Must run from the toolkit-remix repository root")
        sys.exit(1)
    
    # Install build dependencies if needed
    try:
        import build
    except ImportError:
        print("Installing build dependencies...")
        run_command([sys.executable, "-m", "pip", "install", "build"])
    
    try:
        # Test package build
        wheel_file, tar_file = test_package_build()
        
        # Test package installation
        test_package_install(wheel_file)
        
        # Test MCP functionality
        test_mcp_functionality()
        
        print("\n🎉 All tests passed!")
        print(f"Package is ready for distribution:")
        print(f"  - Wheel: {wheel_file}")
        print(f"  - Source: {tar_file}")
        print(f"\nTo install locally: pip install {wheel_file}")
        print(f"To publish to PyPI: twine upload dist/*")
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()