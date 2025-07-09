#!/usr/bin/env python3
"""
RTX Remix Toolkit MCP Server

A Model Context Protocol server that provides tools and resources for developing
features in the RTX Remix Toolkit repository.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource


# Initialize MCP server
mcp = FastMCP("RTX Remix Toolkit Developer")

# Repository root path
REPO_ROOT = Path(__file__).parent
EXTENSIONS_ROOT = REPO_ROOT / "source" / "extensions"
APPS_ROOT = REPO_ROOT / "source" / "apps"
DOCS_ROOT = REPO_ROOT / "docs"


@mcp.resource("repo://structure")
def get_repo_structure() -> str:
    """Get the high-level repository structure and architecture overview."""
    return """
# RTX Remix Toolkit Repository Structure

## Key Directories:
- `source/extensions/` - Extension implementations (Lightspeed & Flux)
- `source/apps/` - Application configurations and entry points
- `docs/` - User documentation and guides
- `docs_dev/` - Developer documentation
- `tools/` - Build and development tools

## Extension Categories:
- **Lightspeed** (`lightspeed.*`) - RTX Remix specific functionality
- **Flux** (`omni.flux.*`) - Generic reusable components

## Main Applications:
- `lightspeed.app.trex.kit` - Main RTX Remix application
- `lightspeed.app.trex.stagecraft.kit` - Stage editing tool
- `lightspeed.app.trex.ingestcraft.kit` - Asset ingestion tool
- `lightspeed.app.trex.texturecraft.kit` - Texture processing tool

## Architecture:
- Event-driven architecture with `lightspeed.events_manager`
- Plugin system for extensibility
- USD-based 3D content pipeline
- Omniverse Kit SDK foundation
"""


@mcp.resource("repo://build_commands")
def get_build_commands() -> str:
    """Get available build and development commands."""
    return """
# RTX Remix Toolkit Build Commands

## Core Commands:
- `./build.sh -r` - Build release version
- `./build.sh -d` - Build debug version
- `./repo.sh test` - Run all tests
- `./format_code.sh` - Format code
- `./lint_code.sh` - Lint code

## Application Launch:
- `./_build/windows-x86_64/release/lightspeed.app.trex.bat` - Main app
- `./_build/windows-x86_64/release/lightspeed.app.trex_dev.bat` - Dev version

## Testing:
- `./_build/windows-x86_64/release/tests-[extension].sh` - Test specific extension
- Add `--coverage` flag for coverage reports

## Development Flags:
- `--/telemetry/enableSentry=false` - Disable Sentry
- `--/rtx/verifyDriverVersion/enabled=false` - Skip driver check
- `--enable omni.kit.debug.pycharm` - Enable PyCharm debugger
"""


@mcp.tool()
def list_extensions(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all extensions in the repository.
    
    Args:
        category: Filter by category ('lightspeed' or 'flux'), or None for all
    """
    extensions = []
    
    if not EXTENSIONS_ROOT.exists():
        return extensions
    
    for ext_dir in EXTENSIONS_ROOT.iterdir():
        if not ext_dir.is_dir():
            continue
            
        ext_name = ext_dir.name
        
        # Filter by category if specified
        if category:
            if category.lower() == "lightspeed" and not ext_name.startswith("lightspeed"):
                continue
            if category.lower() == "flux" and not ext_name.startswith("omni.flux"):
                continue
        
        # Read extension.toml for metadata
        config_path = ext_dir / "config" / "extension.toml"
        metadata = {}
        if config_path.exists():
            try:
                import tomllib
                with open(config_path, "rb") as f:
                    config = tomllib.load(f)
                    metadata = config.get("package", {})
            except Exception:
                pass
        
        extensions.append({
            "name": ext_name,
            "path": str(ext_dir),
            "category": "lightspeed" if ext_name.startswith("lightspeed") else "flux",
            "description": metadata.get("description", ""),
            "version": metadata.get("version", ""),
            "has_tests": (ext_dir / "tests").exists(),
            "has_docs": (ext_dir / "docs").exists(),
        })
    
    return extensions


@mcp.tool()
def analyze_extension(extension_name: str) -> Dict[str, Any]:
    """
    Analyze a specific extension in detail.
    
    Args:
        extension_name: Name of the extension to analyze
    """
    ext_path = EXTENSIONS_ROOT / extension_name
    
    if not ext_path.exists():
        return {"error": f"Extension '{extension_name}' not found"}
    
    analysis = {
        "name": extension_name,
        "path": str(ext_path),
        "category": "lightspeed" if extension_name.startswith("lightspeed") else "flux",
        "structure": {},
        "dependencies": [],
        "metadata": {},
        "tests": {},
        "files": []
    }
    
    # Analyze structure
    structure = {}
    for item in ext_path.iterdir():
        if item.is_dir():
            structure[item.name] = "directory"
        else:
            structure[item.name] = "file"
    analysis["structure"] = structure
    
    # Read extension.toml
    config_path = ext_path / "config" / "extension.toml"
    if config_path.exists():
        try:
            import tomllib
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
                analysis["metadata"] = config.get("package", {})
                analysis["dependencies"] = list(config.get("dependencies", {}).keys())
        except Exception as e:
            analysis["config_error"] = str(e)
    
    # Analyze tests
    tests_path = ext_path / "tests"
    if tests_path.exists():
        test_info = {"has_tests": True, "test_files": []}
        for test_file in tests_path.rglob("*.py"):
            test_info["test_files"].append(str(test_file.relative_to(tests_path)))
        analysis["tests"] = test_info
    else:
        analysis["tests"] = {"has_tests": False}
    
    # List Python files
    python_files = []
    for py_file in ext_path.rglob("*.py"):
        python_files.append(str(py_file.relative_to(ext_path)))
    analysis["files"] = python_files
    
    return analysis


@mcp.tool()
def create_extension_template(
    extension_name: str,
    category: str,
    description: str = "",
    include_tests: bool = True,
    include_ui: bool = False
) -> Dict[str, Any]:
    """
    Create a new extension template.
    
    Args:
        extension_name: Name of the new extension (e.g., 'lightspeed.myfeature')
        category: Category ('lightspeed' or 'flux')
        description: Description of the extension
        include_tests: Whether to include test structure
        include_ui: Whether to include UI components
    """
    if category not in ["lightspeed", "flux"]:
        return {"error": "Category must be 'lightspeed' or 'flux'"}
    
    # Validate extension name
    if category == "lightspeed" and not extension_name.startswith("lightspeed."):
        return {"error": "Lightspeed extensions must start with 'lightspeed.'"}
    if category == "flux" and not extension_name.startswith("omni.flux."):
        return {"error": "Flux extensions must start with 'omni.flux.'"}
    
    ext_path = EXTENSIONS_ROOT / extension_name
    if ext_path.exists():
        return {"error": f"Extension '{extension_name}' already exists"}
    
    try:
        # Create directory structure
        ext_path.mkdir(parents=True)
        (ext_path / "config").mkdir()
        (ext_path / "data").mkdir()
        (ext_path / "docs").mkdir()
        
        # Create namespace directories
        namespace_parts = extension_name.split(".")
        code_path = ext_path
        for part in namespace_parts:
            code_path = code_path / part
            code_path.mkdir(exist_ok=True)
            (code_path / "__init__.py").touch()
        
        # Create extension.toml
        toml_content = f'''[package]
name = "{extension_name}"
version = "1.0.0"
description = "{description}"
authors = ["RTX Remix Team"]
repository = "https://github.com/NVIDIAGameWorks/toolkit-remix"
category = "extension"
keywords = ["rtx", "remix", "omniverse"]

[dependencies]
"omni.kit.usd" = {{}}
"omni.ui" = {{}}
'''
        
        if category == "lightspeed":
            toml_content += '"lightspeed.common" = {}\n'
        else:
            toml_content += '"omni.flux.utils.common" = {}\n'
        
        if include_ui:
            toml_content += '"omni.ui" = {}\n'
        
        if include_tests:
            toml_content += '''
[[test]]
dependencies = [
    "omni.kit.test",
]
'''
        
        with open(ext_path / "config" / "extension.toml", "w") as f:
            f.write(toml_content)
        
        # Create extension.py
        module_path = ext_path / namespace_parts[0]
        for part in namespace_parts[1:]:
            module_path = module_path / part
        
        extension_py_content = f'''"""
{extension_name} extension
"""

import omni.ext
import omni.ui as ui


class {extension_name.replace(".", "_").title()}Extension(omni.ext.IExt):
    """Extension class for {extension_name}"""
    
    def on_startup(self, ext_id):
        """Called when extension starts up"""
        print(f"[{extension_name}] startup")
        
        # Initialize your extension here
        self._setup_extension()
        
    def on_shutdown(self):
        """Called when extension shuts down"""
        print(f"[{extension_name}] shutdown")
        
        # Clean up resources
        self._cleanup_extension()
    
    def _setup_extension(self):
        """Set up the extension"""
        # Add your initialization code here
        pass
    
    def _cleanup_extension(self):
        """Clean up the extension"""
        # Add your cleanup code here
        pass
'''
        
        with open(module_path / "extension.py", "w") as f:
            f.write(extension_py_content)
        
        # Create test structure if requested
        if include_tests:
            (ext_path / "tests").mkdir()
            (ext_path / "tests" / "unit").mkdir()
            (ext_path / "tests" / "e2e").mkdir()
            
            # Create basic test file
            test_content = f'''"""
Unit tests for {extension_name}
"""

import unittest
from unittest.mock import Mock, patch


class Test{extension_name.replace(".", "_").title()}(unittest.TestCase):
    """Test cases for {extension_name}"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_extension_startup(self):
        """Test extension startup"""
        # Add your test code here
        pass


if __name__ == "__main__":
    unittest.main()
'''
            with open(ext_path / "tests" / "unit" / "test_extension.py", "w") as f:
                f.write(test_content)
        
        # Create basic documentation
        readme_content = f'''# {extension_name}

{description}

## Overview

This extension provides...

## Usage

...

## Development

### Testing

```bash
./repo.sh test {extension_name}
```

### Building

```bash
./build.sh -r
```
'''
        
        with open(ext_path / "docs" / "README.md", "w") as f:
            f.write(readme_content)
        
        # Create changelog
        changelog_content = f'''# Changelog

All notable changes to {extension_name} will be documented in this file.

## [1.0.0] - {__import__("datetime").datetime.now().strftime("%Y-%m-%d")}

### Added
- Initial extension creation
'''
        
        with open(ext_path / "docs" / "CHANGELOG.md", "w") as f:
            f.write(changelog_content)
        
        # Create premake5.lua
        premake_content = f'''-- {extension_name} premake5.lua

local ext = get_current_extension_info()

project_ext(ext)
'''
        
        with open(ext_path / "premake5.lua", "w") as f:
            f.write(premake_content)
        
        return {
            "success": True,
            "message": f"Extension '{extension_name}' created successfully",
            "path": str(ext_path),
            "files_created": [
                "config/extension.toml",
                f"{'/'.join(namespace_parts)}/extension.py",
                "docs/README.md",
                "docs/CHANGELOG.md",
                "premake5.lua"
            ] + (["tests/unit/test_extension.py"] if include_tests else [])
        }
        
    except Exception as e:
        return {"error": f"Failed to create extension: {str(e)}"}


@mcp.tool()
def run_build(config: str = "release") -> Dict[str, Any]:
    """
    Run the build system.
    
    Args:
        config: Build configuration ('release' or 'debug')
    """
    try:
        build_script = REPO_ROOT / "build.sh"
        flag = "-r" if config == "release" else "-d"
        
        result = subprocess.run(
            [str(build_script), flag],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": f"./build.sh {flag}"
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Build timed out after 5 minutes"}
    except Exception as e:
        return {"error": f"Build failed: {str(e)}"}


@mcp.tool()
def run_tests(extension_name: Optional[str] = None, test_type: str = "all") -> Dict[str, Any]:
    """
    Run tests for the repository or specific extension.
    
    Args:
        extension_name: Specific extension to test (optional)
        test_type: Type of tests to run ('unit', 'e2e', or 'all')
    """
    try:
        if extension_name:
            # Test specific extension
            test_script = REPO_ROOT / "_build" / "windows-x86_64" / "release" / f"tests-{extension_name}.sh"
            if not test_script.exists():
                return {"error": f"Test script for '{extension_name}' not found"}
            
            cmd = [str(test_script)]
            if test_type in ["unit", "e2e"]:
                cmd.append(f"--/exts/omni.kit.test/runTestsFilter='{extension_name}.*.tests.{test_type}.*'")
        else:
            # Run all tests
            repo_script = REPO_ROOT / "repo.sh"
            cmd = [str(repo_script), "test"]
        
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for tests
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd)
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Tests timed out after 10 minutes"}
    except Exception as e:
        return {"error": f"Test execution failed: {str(e)}"}


@mcp.tool()
def format_code() -> Dict[str, Any]:
    """Format code using the project's formatting tools."""
    try:
        format_script = REPO_ROOT / "format_code.sh"
        
        result = subprocess.run(
            [str(format_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": "./format_code.sh"
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Code formatting timed out after 2 minutes"}
    except Exception as e:
        return {"error": f"Code formatting failed: {str(e)}"}


@mcp.tool()
def lint_code() -> Dict[str, Any]:
    """Lint code using the project's linting tools."""
    try:
        lint_script = REPO_ROOT / "lint_code.sh"
        
        result = subprocess.run(
            [str(lint_script)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": "./lint_code.sh"
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Code linting timed out after 2 minutes"}
    except Exception as e:
        return {"error": f"Code linting failed: {str(e)}"}


@mcp.tool()
def search_code(query: str, file_pattern: str = "*.py") -> List[Dict[str, Any]]:
    """
    Search for code patterns in the repository.
    
    Args:
        query: Search query (regex pattern)
        file_pattern: File pattern to search in (default: *.py)
    """
    try:
        import subprocess
        
        # Use ripgrep for fast searching
        result = subprocess.run(
            ["rg", "--json", "--type", "py" if file_pattern == "*.py" else "all", query],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        matches = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "match":
                    matches.append({
                        "file": data["data"]["path"]["text"],
                        "line": data["data"]["line_number"],
                        "column": data["data"]["submatches"][0]["start"],
                        "content": data["data"]["lines"]["text"],
                        "match": data["data"]["submatches"][0]["match"]["text"]
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return matches
        
    except subprocess.TimeoutExpired:
        return [{"error": "Search timed out after 30 seconds"}]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool()
def get_extension_dependencies(extension_name: str) -> Dict[str, Any]:
    """
    Get the dependency tree for an extension.
    
    Args:
        extension_name: Name of the extension
    """
    ext_path = EXTENSIONS_ROOT / extension_name
    
    if not ext_path.exists():
        return {"error": f"Extension '{extension_name}' not found"}
    
    # Read extension.toml
    config_path = ext_path / "config" / "extension.toml"
    if not config_path.exists():
        return {"error": f"No extension.toml found for '{extension_name}'"}
    
    try:
        import tomllib
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        
        dependencies = config.get("dependencies", {})
        
        # Analyze dependency types
        dep_analysis = {
            "direct_dependencies": list(dependencies.keys()),
            "lightspeed_deps": [dep for dep in dependencies.keys() if dep.startswith("lightspeed.")],
            "flux_deps": [dep for dep in dependencies.keys() if dep.startswith("omni.flux.")],
            "kit_deps": [dep for dep in dependencies.keys() if dep.startswith("omni.kit.")],
            "other_deps": [dep for dep in dependencies.keys() if not any(
                dep.startswith(prefix) for prefix in ["lightspeed.", "omni.flux.", "omni.kit."]
            )],
            "total_count": len(dependencies)
        }
        
        return {
            "extension": extension_name,
            "analysis": dep_analysis,
            "raw_dependencies": dependencies
        }
        
    except Exception as e:
        return {"error": f"Failed to analyze dependencies: {str(e)}"}


def main():
    """Main entry point for the MCP server."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="RTX Remix Toolkit MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rtx-remix-mcp                    # Run MCP server via stdio
  remix-mcp                        # Same as above (shorter alias)
  
For use with Claude Code:
  claude mcp add rtx-remix-toolkit python rtx-remix-mcp
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="RTX Remix Toolkit MCP Server 1.0.0"
    )
    
    parser.add_argument(
        "--repo-path",
        help="Path to RTX Remix Toolkit repository (default: current directory)",
        default="."
    )
    
    args = parser.parse_args()
    
    # Update the repository path if provided
    global REPO_ROOT
    REPO_ROOT = Path(args.repo_path).resolve()
    
    # Verify this is a valid RTX Remix Toolkit repository
    if not (REPO_ROOT / "source" / "extensions").exists():
        print(f"Error: {REPO_ROOT} does not appear to be a valid RTX Remix Toolkit repository", file=sys.stderr)
        print("Expected to find 'source/extensions' directory", file=sys.stderr)
        sys.exit(1)
    
    # Update global paths
    global EXTENSIONS_ROOT, APPS_ROOT, DOCS_ROOT
    EXTENSIONS_ROOT = REPO_ROOT / "source" / "extensions"
    APPS_ROOT = REPO_ROOT / "source" / "apps"
    DOCS_ROOT = REPO_ROOT / "docs"
    
    # Run the MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nMCP server stopped", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()