#!/bin/bash

# pcap2uml Wireshark Plugin Installation Script
# This script installs the pcap2uml Wireshark plugin

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to detect OS and find Wireshark directories
detect_wireshark_dirs() {
    print_status "Detecting Wireshark installation..."
    
    # Common Wireshark plugin directories
    local possible_dirs=(
        "$HOME/.local/lib/wireshark/plugins"
        "$HOME/.wireshark/plugins"
        "/usr/local/lib/wireshark/plugins"
        "/usr/lib/wireshark/plugins"
        "/opt/wireshark/lib/plugins"
        "/Applications/Wireshark.app/Contents/PlugIns/wireshark"
    )
    
    for dir in "${possible_dirs[@]}"; do
        if [ -d "$dir" ]; then
            WIRESHARK_PLUGIN_DIR="$dir"
            print_status "Found Wireshark plugin directory: $WIRESHARK_PLUGIN_DIR"
            return 0
        fi
    done
    
    print_error "Could not find Wireshark plugin directory"
    print_warning "Please install Wireshark first or manually specify the plugin directory"
    return 1
}

# Function to get the current script directory
get_script_dir() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    print_status "Script directory: $SCRIPT_DIR"
}

# Function to update plugin configuration
update_plugin_config() {
    print_status "Updating plugin configuration..."
    
    local plugin_file="$WIRESHARK_PLUGIN_DIR/pcap2uml_wireshark.lua"
    
    if [ ! -f "$plugin_file" ]; then
        print_error "Plugin file not found: $plugin_file"
        return 1
    fi
    
    # Get the absolute path to pcap2uml.py
    local pcap2uml_script="$SCRIPT_DIR/pcap2uml.py"
    
    if [ ! -f "$pcap2uml_script" ]; then
        print_error "pcap2uml.py not found at: $pcap2uml_script"
        print_warning "Please ensure pcap2uml.py is in the same directory as this script"
        return 1
    fi
    
    # Update the script path in the plugin
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|pcap2uml_script = \".*\"|pcap2uml_script = \"$pcap2uml_script\"|" "$plugin_file"
    else
        # Linux
        sed -i "s|pcap2uml_script = \".*\"|pcap2uml_script = \"$pcap2uml_script\"|" "$plugin_file"
    fi
    
    print_status "Updated plugin configuration with script path: $pcap2uml_script"
}

# Function to install the plugin
install_plugin() {
    print_status "Installing pcap2uml Wireshark plugin..."
    
    local source_file="$SCRIPT_DIR/pcap2uml_wireshark.lua"
    local target_file="$WIRESHARK_PLUGIN_DIR/pcap2uml_wireshark.lua"
    
    if [ ! -f "$source_file" ]; then
        print_error "Plugin source file not found: $source_file"
        return 1
    fi
    
    # Create plugin directory if it doesn't exist
    mkdir -p "$WIRESHARK_PLUGIN_DIR"
    
    # Copy the plugin file
    cp "$source_file" "$target_file"
    
    if [ $? -eq 0 ]; then
        print_status "Plugin installed successfully to: $target_file"
    else
        print_error "Failed to install plugin"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        print_warning "Please install Python 3 to use pcap2uml"
        return 1
    fi
    
    # Check if pyshark is available
    if ! python3 -c "import pyshark" &> /dev/null; then
        print_warning "pyshark Python module is not installed"
        print_warning "Please install it with: pip3 install pyshark"
    fi
    
    # Check if Java is available (for PlantUML)
    if ! command -v java &> /dev/null; then
        print_warning "Java is not installed or not in PATH"
        print_warning "PlantUML image generation may not work without Java"
    fi
    
    print_status "Dependency check completed"
}

# Function to create output directory
create_output_dir() {
    local output_dir="$HOME/pcap2uml_output"
    mkdir -p "$output_dir"
    print_status "Created output directory: $output_dir"
}

# Function to show usage instructions
show_usage_instructions() {
    print_header "Installation Complete!"
    echo
    echo "The pcap2uml Wireshark plugin has been installed successfully."
    echo
    echo "To use the plugin:"
    echo "1. Restart Wireshark"
    echo "2. Open a pcap file"
    echo "3. Go to Tools > pcap2uml > Generate UML Diagram"
    echo
    echo "The plugin will:"
    echo "• Use the currently opened pcap file"
    echo "• Apply the current display filter (if any)"
    echo "• Generate UML diagrams in: $HOME/pcap2uml_output"
    echo
    echo "For more information, go to Tools > pcap2uml > Show Plugin Info"
    echo
}

# Main installation function
main() {
    print_header "pcap2uml Wireshark Plugin Installer"
    echo
    
    # Get script directory
    get_script_dir
    
    # Check dependencies
    check_dependencies
    
    # Detect Wireshark directories
    if ! detect_wireshark_dirs; then
        print_error "Installation failed: Could not find Wireshark plugin directory"
        exit 1
    fi
    
    # Install the plugin
    if ! install_plugin; then
        print_error "Installation failed: Could not install plugin"
        exit 1
    fi
    
    # Update plugin configuration
    if ! update_plugin_config; then
        print_warning "Could not update plugin configuration"
        print_warning "You may need to manually edit the plugin file"
    fi
    
    # Create output directory
    create_output_dir
    
    # Show usage instructions
    show_usage_instructions
}

# Run main function
main "$@" 