# pcap2uml Wireshark Plugin

This Wireshark plugin integrates the `pcap2uml.py` script directly into Wireshark, allowing you to generate UML sequence diagrams from pcap files with a single click.

## Features

- **Seamless Integration**: Access pcap2uml functionality directly from Wireshark's Tools menu
- **Current File Support**: Automatically uses the currently opened pcap file
- **Display Filter Support**: Applies the current Wireshark display filter to the analysis
- **Automatic Output**: Generates timestamped output files in a dedicated directory
- **Multiple Formats**: Supports various output formats (PNG, SVG, PDF, etc.)

## Prerequisites

Before installing the plugin, ensure you have:

1. **Wireshark** installed and working
2. **Python 3.6+** installed
3. **pyshark** Python module: `pip3 install pyshark`
4. **Java** (for PlantUML image generation): `java -version`
5. **PlantUML** JAR file (configured in `conf/conf_uml.py`)

## Installation

### Automatic Installation (Recommended)

1. Download or clone the pcap2uml repository
2. Navigate to the repository directory
3. Run the installation script:

```bash
./install_wireshark_plugin.sh
```

The script will:
- Detect your Wireshark installation
- Install the plugin to the correct directory
- Update the plugin configuration with the correct paths
- Create the output directory
- Check dependencies

### Manual Installation

If the automatic installation doesn't work, you can install manually:

1. **Find your Wireshark plugin directory**:
   - Linux: `~/.local/lib/wireshark/plugins` or `~/.wireshark/plugins`
   - macOS: `~/Library/Application Support/Wireshark/plugins`
   - Windows: `%APPDATA%\Wireshark\plugins`

2. **Copy the plugin file**:
   ```bash
   cp pcap2uml_wireshark.lua /path/to/wireshark/plugins/
   ```

3. **Edit the plugin configuration**:
   Open `pcap2uml_wireshark.lua` and update the `pcap2uml_script` path to point to your `pcap2uml.py` file.

4. **Restart Wireshark**

## Configuration

The plugin configuration is located at the top of `pcap2uml_wireshark.lua`:

```lua
local config = {
    -- Path to pcap2uml.py script (modify this to match your installation)
    pcap2uml_script = "/path/to/pcap2uml.py",
    -- Default output directory for generated UML files
    output_dir = os.getenv("HOME") .. "/pcap2uml_output",
    -- Default output format
    output_format = "png"
}
```

### Configuration Options

- **pcap2uml_script**: Full path to your `pcap2uml.py` script
- **output_dir**: Directory where generated files will be saved
- **output_format**: Default output format (png, svg, pdf, etc.)

## Usage

### Basic Usage

1. **Open a pcap file** in Wireshark
2. **Apply a display filter** (optional) to focus on specific traffic
3. **Go to Tools > pcap2uml > Generate UML Diagram**
4. **Check the output directory** for generated files

### Advanced Usage

- **Show Plugin Info**: View plugin version and configuration
- **Open Output Directory**: Quickly access generated files
- **Custom Filters**: Apply complex display filters before generating diagrams

### Example Workflow

1. Open a SIP capture file in Wireshark
2. Apply filter: `sip || diameter`
3. Go to Tools > pcap2uml > Generate UML Diagram
4. Find generated files in `~/pcap2uml_output/`

## Output Files

The plugin generates two types of files:

1. **UML Source File** (`.uml`): PlantUML source code
2. **Image File** (`.png`, `.svg`, etc.): Rendered diagram

Files are named with timestamps: `pcap2uml_YYYYMMDD_HHMMSS.*`

## Troubleshooting

### Plugin Not Appearing

1. **Check installation**: Verify the plugin file is in the correct directory
2. **Restart Wireshark**: Plugins are loaded at startup
3. **Check permissions**: Ensure the plugin file is readable
4. **View Wireshark logs**: Check for Lua errors in Wireshark's console

### Script Execution Errors

1. **Check Python path**: Ensure `python3` is in your PATH
2. **Verify dependencies**: Install missing Python modules
3. **Check file paths**: Ensure `pcap2uml.py` path is correct
4. **Test manually**: Try running `pcap2uml.py` directly from command line

### Common Issues

- **"Script not found"**: Update the `pcap2uml_script` path in the plugin
- **"Permission denied"**: Check file permissions and Python execution rights
- **"No output generated"**: Verify PlantUML and Java are properly configured
- **"Stack overflow"**: This was a bug in v1.0 that has been fixed. Update to the latest version.

### Known Issues and Fixes

#### Stack Overflow Error (Fixed in v1.1)
If you see a "stack overflow" error when loading the plugin, this was caused by a recursive function call in the menu registration. This has been fixed by renaming the internal function to avoid conflicts with Wireshark's built-in functions.

## Plugin Menu Structure

```
Tools
└── pcap2uml
    ├── Generate UML Diagram
    ├── Show Plugin Info
    └── Open Output Directory
```

## Development

### Plugin Structure

- **Main Plugin File**: `pcap2uml_wireshark.lua`
- **Installation Script**: `install_wireshark_plugin.sh`
- **Configuration**: Embedded in the plugin file

### Extending the Plugin

To add new features:

1. **Add new menu items** in the `register_menu()` function
2. **Create new functions** for additional functionality
3. **Update configuration** for new options
4. **Test thoroughly** with different Wireshark versions

### Debugging

Enable debug output by adding print statements to the Lua code. Output appears in Wireshark's console (Help > About Wireshark > Wireshark).

## Support

For issues and questions:

1. **Check the troubleshooting section** above
2. **Verify your installation** matches the requirements
3. **Test with a simple pcap file** first
4. **Check Wireshark and Python logs** for error messages

## License

This plugin is part of the pcap2uml project and follows the same license terms.

## Version History

- **v1.0**: Initial release with basic functionality
  - Automatic file detection
  - Display filter support
  - Multiple output formats
  - Installation script 