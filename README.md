# RTX Remix Toolkit MCP Server

A Model Context Protocol (MCP) server that provides tools and resources for developing features in the RTX Remix Toolkit repository. This server enables AI assistants like Claude to understand and work with the RTX Remix Toolkit codebase more effectively.

## Overview

This MCP server provides comprehensive development assistance for the RTX Remix Toolkit, including:

- **Repository Analysis**: Analyze extensions, dependencies, and architecture
- **Extension Development**: Create new extensions and analyze existing ones
- **Build System Integration**: Interface with build system and testing
- **Code Search**: Search for patterns across the codebase
- **Documentation**: Access repository structure and development guides

## Features

### Resources
- `repo://structure` - Repository structure and architecture overview
- `repo://build_commands` - Available build and development commands

### Tools
- `list_extensions` - List all extensions with filtering by category
- `analyze_extension` - Detailed analysis of specific extensions
- `create_extension_template` - Create new extension templates
- `run_build` - Execute build system
- `run_tests` - Run tests for repository or specific extensions
- `format_code` - Format code using project standards
- `lint_code` - Lint code using project standards
- `search_code` - Search for code patterns
- `get_extension_dependencies` - Analyze extension dependency trees

## Installation

### Prerequisites

This MCP server must be cloned into the root directory of the RTX Remix Toolkit repository to function properly.

1. **Clone this repository into your RTX Remix Toolkit root**:
```bash
# Navigate to your RTX Remix Toolkit repository root
cd /path/to/your/rtx-remix-toolkit

# Clone the MCP server into the root directory
git clone https://github.com/your-org/toolkit-remix-mcp .
```

2. **Install MCP dependencies**:
```bash
pip install -r requirements-mcp.txt
```

3. **Make the server executable**:
```bash
chmod +x mcp_server.py
```

## Usage

### With Claude Code (CLI)

Add the MCP server to your Claude Code configuration:

```bash
# Add the MCP server (run from the repository root)
claude mcp add rtx-remix-toolkit python mcp_server.py

# Verify it was added
claude mcp list

# Get server details
claude mcp get rtx-remix-toolkit
```

### With Claude Desktop

Add this configuration to your Claude Desktop settings:

```json
{
  "mcpServers": {
    "rtx-remix-toolkit": {
      "command": "python",
      "args": ["/path/to/toolkit-remix/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/toolkit-remix"
      }
    }
  }
}
```

### Using with Claude Code

Once added, you can use the MCP server in your Claude Code conversations:

```bash
# Reference repository resources
@rtx-remix-toolkit:repo://structure
@rtx-remix-toolkit:repo://build_commands

# Use MCP tools in your prompts
# Ask Claude to use list_extensions, analyze_extension, etc.
# The tools are automatically available to Claude Code
```

### Direct Usage

Run the MCP server directly:
```bash
python mcp_server.py
```

## Example Usage

### List Extensions
```python
# List all extensions
extensions = list_extensions()

# List only Lightspeed extensions
lightspeed_extensions = list_extensions(category="lightspeed")

# List only Flux extensions
flux_extensions = list_extensions(category="flux")
```

### Analyze Extension
```python
# Get detailed analysis of an extension
analysis = analyze_extension("lightspeed.trex.stage_manager.widget")
print(f"Dependencies: {analysis['dependencies']}")
print(f"Has tests: {analysis['tests']['has_tests']}")
```

### Create New Extension
```python
# Create a new Lightspeed extension
result = create_extension_template(
    extension_name="lightspeed.myfeature",
    category="lightspeed",
    description="My new feature for RTX Remix",
    include_tests=True,
    include_ui=True
)
```

### Build and Test
```python
# Build the project
build_result = run_build(config="release")

# Run tests for specific extension
test_result = run_tests(
    extension_name="lightspeed.trex.stage_manager.widget",
    test_type="unit"
)

# Format code
format_result = format_code()
```

### Search Code
```python
# Search for specific patterns
matches = search_code(
    query="class.*Extension.*omni.ext.IExt",
    file_pattern="*.py"
)
```

## Development Workflow

### Creating a New Feature

1. **Plan the Extension**:
   ```python
   # Use the MCP server to understand the architecture
   structure = get_repo_structure()
   
   # List similar extensions for reference
   similar_extensions = list_extensions(category="lightspeed")
   ```

2. **Create Extension Template**:
   ```python
   result = create_extension_template(
       extension_name="lightspeed.myfeature",
       category="lightspeed",
       description="Description of my feature",
       include_tests=True,
       include_ui=True
   )
   ```

3. **Analyze Dependencies**:
   ```python
   # Look at similar extensions to understand common patterns
   deps = get_extension_dependencies("lightspeed.trex.stage_manager.widget")
   ```

4. **Implement and Test**:
   ```python
   # Build the project
   build_result = run_build()
   
   # Run tests
   test_result = run_tests(extension_name="lightspeed.myfeature")
   
   # Format code
   format_result = format_code()
   ```

### Common Development Tasks

- **Finding Extension Patterns**: Use `search_code` to find common patterns
- **Understanding Dependencies**: Use `get_extension_dependencies` to understand how extensions interact
- **Testing Strategy**: Use `analyze_extension` to see how similar extensions structure their tests
- **Architecture Understanding**: Use repository resources to understand the overall structure

## Architecture

The MCP server is built using the FastMCP framework and provides:

- **Repository Resources**: Static information about the repository structure
- **Analysis Tools**: Tools for understanding the codebase
- **Development Tools**: Tools for creating and testing extensions
- **Build Integration**: Direct integration with the build system

## Error Handling

The MCP server includes comprehensive error handling:

- Build timeouts (5 minutes)
- Test timeouts (10 minutes)
- Code formatting/linting timeouts (2 minutes)
- Search timeouts (30 seconds)
- Graceful handling of missing files or invalid configurations

## Security

The MCP server operates within the repository directory and:

- Only accesses files within the repository
- Uses subprocess timeouts to prevent hanging operations
- Validates extension names and categories
- Provides read-only access to repository structure

## Contributing

When adding new tools or resources:

1. Follow the existing pattern of error handling and timeouts
2. Add comprehensive docstrings
3. Include type hints
4. Test the functionality thoroughly
5. Update this documentation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `requirements-mcp.txt` is installed
2. **Build Failures**: Check that the repository is properly set up
3. **Test Failures**: Ensure the build has completed successfully
4. **Permission Errors**: Make sure the MCP server has appropriate file permissions

### Debug Mode

For debugging, you can run the server with additional logging:

```bash
PYTHONPATH=/path/to/toolkit-remix python mcp_server.py
```

## License

This MCP server is part of the RTX Remix Toolkit and follows the same license terms.