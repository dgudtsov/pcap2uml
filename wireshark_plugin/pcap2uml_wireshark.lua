--[[
    pcap2uml Wireshark Plugin
    This plugin adds a menu item to Wireshark that allows users to generate UML diagrams
    from the current pcap file using the pcap2uml.py script.
    
    Author: Denis Gudtsov
    Version: 1.1
    Date: 2025-06-20
]]

-- Plugin information
local plugin_info = {
    version = "1.1",
    author = "Denis Gudtsov",
    description = "Generate UML diagrams from pcap files using pcap2uml.py",
    repository = "https://github.com/dgudtsov/pcap2uml"
}

-- Register a dummy protocol to enable preferences
local pcap2uml_proto = Proto("pcap2uml", "pcap2uml Utility Plugin")
local pcap2uml_prefs = pcap2uml_proto.prefs

pcap2uml_prefs.script_path = Pref.string("Script path", "/Users/denis/git/pcap2uml/pcap2uml.py", "Path to pcap2uml.py script")
pcap2uml_prefs.output_dir = Pref.string("Output directory", os.getenv("HOME") .. "/pcap2uml_output", "Directory for UML output files")
pcap2uml_prefs.output_format = Pref.string("Output format", "png", "Output image format (png, svg, etc.)")

pcap2uml_prefs.execution_mode = Pref.enum(
    "Execution mode",
    0,
    "Show output in Wireshark popup or terminal",
    {
        { 0,  "popup", 0 },
        { 1,  "terminal",  1  },
    }
)

-- Utility function to check if file exists
local function file_exists(path)
    local file = io.open(path, "r")
    if file then
        file:close()
        return true
    end
    return false
end

-- Utility function to create directory if it doesn't exist
local function ensure_dir_exists(dir_path)
    if not file_exists(dir_path) then
        os.execute("mkdir -p '" .. dir_path .. "'")
    end
end

-- Utility function to get current timestamp for unique filenames
local function get_timestamp()
    return os.date("%Y%m%d_%H%M%S")
end

-- Function to get the current pcap file path
local function get_current_pcap_file()

    local fname = nil
    if current_capturefile then
        fname = current_capturefile()
        print("current_capturefile via current_capturefile(): " .. fname)
    elseif get_tshark_capture_filename then
        fname = get_tshark_capture_filename()
        print("current_capturefile via get_tshark_capture_filename(): " .. fname)
    end

    return fname
    
end

-- Function to get the current display filter
local function get_current_display_filter()
    local filter = get_filter()
    if filter and filter ~= "" then
        return filter
    end
    return nil
end

-- Function to generate output filename
local function generate_output_filename(output_dir)
    local timestamp = get_timestamp()
    local base_filename = "pcap2uml_" .. timestamp

    return output_dir .. "/" .. base_filename
end

-- Function to get the script path from preferences
local function get_pref_path()
    return pcap2uml_prefs.script_path
end

-- Function to get the output directory from preferences
local function get_pref_output_dir()
    return pcap2uml_prefs.output_dir
end

-- Function to get the output format from preferences
local function get_pref_output_format()
    return pcap2uml_prefs.output_format
end

-- Function to get the execution mode from preferences
local function get_pref_execution_mode()
    local idx = pcap2uml_prefs.execution_mode
    if idx == 0 then
        return "popup"
    else
        return "terminal"
    end
end

-- Function to execute pcap2uml.py
local function execute_pcap2uml(pcap_file, display_filter, output_file)
    local script_path = get_pref_path()
    local output_format = get_pref_output_format()
    local execution_mode = get_pref_execution_mode()
    local cmd = string.format(
        "python3 '%s' -i '%s' -o '%s.uml' -t %s",
        script_path,
        pcap_file,
        output_file,
        output_format
    )
    
    -- Add display filter if provided
    if display_filter and display_filter ~= "" then
        cmd = cmd .. string.format(" -y '%s'", display_filter)
    end
    
    if execution_mode == "terminal" then
        -- macOS
        if package.config:sub(1,1) == "/" and os.getenv("OSTYPE") and os.getenv("OSTYPE"):match("darwin") then
            os.execute('osascript -e ' ..
                string.format("'tell application \"Terminal\" to do script \"%s\"'", cmd:gsub('"', '\\"')))
        -- Linux
        elseif package.config:sub(1,1) == "/" then
            -- Try gnome-terminal, x-terminal-emulator, or xterm
            local term_cmd = nil
            if os.execute("command -v gnome-terminal > /dev/null 2>&1") == 0 then
                term_cmd = string.format("gnome-terminal -- bash -c '%s; exec bash'", cmd)
            elseif os.execute("command -v x-terminal-emulator > /dev/null 2>&1") == 0 then
                term_cmd = string.format("x-terminal-emulator -e bash -c '%s; exec bash'", cmd)
            elseif os.execute("command -v xterm > /dev/null 2>&1") == 0 then
                term_cmd = string.format("xterm -e '%s; bash'", cmd)
            end
            if term_cmd then
                os.execute(term_cmd)
            else
                -- Fallback to popup if no terminal found
                local tmp_output = os.tmpname()
                os.execute(cmd .. string.format(" > '%s' 2>&1", tmp_output))
                local f = io.open(tmp_output, "r")
                local result = f and f:read("*a") or "(No output)"
                if f then f:close() end
                local win = TextWindow.new("pcap2uml Execution Output")
                win:set(result)
            end
        else
            -- Unknown OS, fallback to popup
            local tmp_output = os.tmpname()
            os.execute(cmd .. string.format(" > '%s' 2>&1", tmp_output))
            local f = io.open(tmp_output, "r")
            local result = f and f:read("*a") or "(No output)"
            if f then f:close() end
            local win = TextWindow.new("pcap2uml Execution Output")
            win:set(result)
        end
    else
        -- Default: popup mode
        local tmp_output = os.tmpname()

        local f_log = io.open(tmp_output, "w")
        if f_log then
            f_log:write("Executing command: " .. cmd .. "\n")
            f_log:close()
        end
        os.execute(cmd .. string.format(" >> '%s' 2>&1", tmp_output))
        local f = io.open(tmp_output, "r")
        local result = f and f:read("*a") or "(No output)"
        if f then f:close() end
        local win = TextWindow.new("pcap2uml Execution Output")
        win:set(result)
    end
end

-- Main function to generate UML diagram
local function generate_uml_diagram()
    -- Get current pcap file
    local pcap_file = get_current_pcap_file()
    -- Get current display filter
    local display_filter = get_current_display_filter()
    -- Ensure output directory exists
    ensure_dir_exists(get_pref_output_dir())
    -- Generate output filename
    local output_file = generate_output_filename(get_pref_output_dir())

    new_dialog(
        "Generate UML Diagram",
        function(fields)
            -- If user provided a new value for Input file, Output file, or Display filter, use them
            local user_pcap_file = fields and fields["Input file"] or pcap_file
            local user_output_file = fields and fields["Output file"] or (output_file .. ".uml")
            local user_display_filter = fields and fields["Display filter"] or display_filter

            -- Remove .uml extension if present, since execute_pcap2uml adds it
            user_output_file = tostring(user_output_file)
            if user_output_file:sub(-4) == ".uml" then
                user_output_file = user_output_file:sub(1, -5)
            end

            execute_pcap2uml(user_pcap_file, user_display_filter, user_output_file)
        end,
        { name = "Script path", value = get_pref_path() },
        { name = "Input file", value = pcap_file or "<none>" },
        { name = "Display filter", value = display_filter or "<none>" },

        { name = "Output directory", value = get_pref_output_dir() },
        { name = "Output file", value = output_file .. ".uml" },
        { name = "Output format", value = get_pref_output_format() }
        
    )
end

-- Function to show plugin information
local function show_plugin_info()
    local info = "pcap2uml Wireshark Plugin\n\n"
    info = info .. "Version: " .. plugin_info.version .. "\n"
    info = info .. "Author: " .. plugin_info.author .. "\n"
    info = info .. "Description: " .. plugin_info.description .. "\n\n"
    info = info .. "Configuration (from preferences):\n"
    info = info .. "• Script path: " .. get_pref_path() .. "\n"
    info = info .. "• Output directory: " .. get_pref_output_dir() .. "\n"
    info = info .. "• Output format: " .. get_pref_output_format() .. "\n"
    info = info .. "• Execution mode: " .. get_pref_execution_mode() .. "\n"

    local win = TextWindow.new("pcap2uml Plugin Info")
    win:set(info)
end

-- Function to open output directory
local function open_output_directory()
    local cmd = "open '" .. get_pref_output_dir() .. "'"
    os.execute(cmd)
    print("Opening output directory: " .. get_pref_output_dir())
end

-- Register the plugin menu
local function register_plugin_menu()
    -- Add menu item to Tools menu
    local menu = "Tools"
    local submenu = "pcap2uml"
    
    -- Create submenu
    register_menu("pcap2uml/Generate UML Diagram", generate_uml_diagram,MENU_TOOLS_UNSORTED)
    register_menu("pcap2uml/Show Plugin Info", show_plugin_info,MENU_TOOLS_UNSORTED)
    register_menu("pcap2uml/Open Output Directory", open_output_directory,MENU_TOOLS_UNSORTED)
end

-- Initialize the plugin
local function init()

        register_plugin_menu()

    print("pcap2uml Wireshark Plugin loaded successfully!")
    print("Version: " .. plugin_info.version)
    print("Script path: " .. get_pref_path())
    print("Output directory: " .. get_pref_output_dir())
    print("Execution mode: " .. get_pref_execution_mode())
    
    -- Register menu items
end
if not gui_enabled() then return end
-- Plugin initialization
init() 