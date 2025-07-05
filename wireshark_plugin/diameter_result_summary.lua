--[[
    This is part of pcap2uml Wireshark Plugin
    This plugin adds a menu item to Wireshark that allows users to see the summary of Diameter result codes.
    It also allows to see the summary of Diameter result codes by source IP.

    Author: Denis Gudtsov
    Version: 1.0
    Date: 2025-07-03
]]
local cat=[[    
             *     ,MMM8&&&.            *
                  MMMM88&&&&&    .
                 MMMM88&&&&&&&
     *           MMM88&&&&&&&&
                 MMM88&&&&&&&&
                 'MMM88&&&&&&'
                   'MMM8&&&'      *
          |\___/|
         =) ^Y^ (=            .              '
          \  ^  /
           )=*=(       *
          /     \
          |     |
         /| | | |\
         \| | |_|/\
  jgs_/\_//_// ___/\_/\_/\_/\_/\_/\_/\_/\_/\_
  |  |  |  | \_) |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  ]]

  --[=[ https://user.xmission.com/~emailbox/ascii_cats.htm ]=]


local result_code_field = Field.new("diameter.Result-Code")
local exp_result_code_field = Field.new("diameter.Experimental-Result-Code")
local cmd_code_field = Field.new("diameter.cmd.code")  
local app_id_field = Field.new("diameter.applicationId") 
local cc_request_type_field = Field.new("diameter.CC-Request-Type")

local function generate_diam_stats()

    local win = TextWindow.new("Diameter Result Code Summary")
    win:append("Please wait while the plugin is generating the summary...\n\n")
    win:append(cat)

    local tap = Listener.new("frame", "diameter")
    local result_counts = {}
    local result_names = {}
    local total = 0

    -- For per-source-IP grouping
    local ip_result_counts = {}  -- ip_result_counts[src_ip][code][app_display] = count
    local ip_result_names = {}   -- ip_result_names[src_ip][code][app_display] = name
    local ip_totals = {}        -- ip_totals[src_ip] = total for that IP
    local ip_app_display = {}   -- ip_app_display[src_ip][code][app_display] = app_display

    -- For per-command-code grouping
    local cmd_result_counts = {}  -- cmd_result_counts[cmd_code][code] = count
    local cmd_result_names = {}   -- cmd_result_names[cmd_code][code] = name
    local cmd_totals = {}        -- cmd_totals[cmd_code] = total for that command code
    local cmd_display_names = {}  -- cmd_display_names[cmd_code] = display string
    local app_display_names = {}  -- app_display_names[cmd_code][app_id] = display string

    -- For per-command-code with CC-Request-Type grouping
    local cmd_cc_req_result_counts = {}  -- cmd_cc_req_result_counts[cmd_code][code][app_display] = count
    local cmd_cc_req_result_names = {}   -- cmd_cc_req_result_names[cmd_code][code] = name
    local cmd_cc_req_totals = {}        -- cmd_cc_req_totals[cmd_code] = total for that command code
    local cmd_cc_req_display_names = {}  -- cmd_cc_req_display_names[cmd_code] = display string
    local app_cc_req_display_names = {}  -- app_cc_req_display_names[cmd_code][app_id] = display string
    local cc_req_type_display_names = {} -- cc_req_type_display_names[cmd_code][app_id] = display string

    function tap.packet(pinfo, tvb)
        -- Try both result code fields
        local rc = result_code_field()  -- FieldInfo or nil
        local exp_rc = exp_result_code_field()  -- FieldInfo or nil
        local code_fi = rc or exp_rc
        if not code_fi then return end
        local val = tostring(code_fi.value)
        local name = tostring(code_fi.display)
        local cc = cmd_code_field and cmd_code_field() or nil
        local app = app_id_field and app_id_field() or nil
        local cc_req_type = cc_request_type_field and cc_request_type_field() or nil
        result_counts[val] = (result_counts[val] or 0) + 1
        result_names[val] = name
        total = total + 1

        -- Per-source-IP
        if code_fi.value > 2001 then
            local src_ip = tostring(pinfo.src)
            local app_display = app and tostring(app.display) or ""
            if not ip_result_counts[src_ip] then
                ip_result_counts[src_ip] = {}
                ip_result_names[src_ip] = {}
                ip_app_display[src_ip] = {}
                ip_totals[src_ip] = 0
            end
            if not ip_result_counts[src_ip][val] then
                ip_result_counts[src_ip][val] = {}
                ip_result_names[src_ip][val] = {}
                ip_app_display[src_ip][val] = {}
            end
            ip_result_counts[src_ip][val][app_display] = (ip_result_counts[src_ip][val][app_display] or 0) + 1
            ip_result_names[src_ip][val][app_display] = name
            ip_app_display[src_ip][val][app_display] = app_display
            ip_totals[src_ip] = ip_totals[src_ip] + 1
        end

        -- Per-command-code and application id
        if cc and code_fi.value > 2001 then
            local cmd_code = tostring(cc.value)
            local cmd_display = tostring(cc.display)
            local app_display = app and tostring(app.display) or ""
            if not cmd_result_counts[cmd_code] then
                cmd_result_counts[cmd_code] = {}
                cmd_result_names[cmd_code] = {}
                cmd_totals[cmd_code] = 0
                cmd_display_names[cmd_code] = cmd_display
                app_display_names[cmd_code] = {}
            end
            local app_key = app_display
            if not cmd_result_counts[cmd_code][val] then
                cmd_result_counts[cmd_code][val] = {}
            end
            cmd_result_counts[cmd_code][val][app_key] = (cmd_result_counts[cmd_code][val][app_key] or 0) + 1
            cmd_result_names[cmd_code][val] = name
            cmd_totals[cmd_code] = cmd_totals[cmd_code] + 1
            cmd_display_names[cmd_code] = cmd_display
            app_display_names[cmd_code][app_key] = app_display
        end

        -- Per-command-code with CC-Request-Type and application id
        if cc and code_fi.value > 2001 then
            local cmd_code = tostring(cc.value)
            local cmd_display = tostring(cc.display)
            local app_display = app and tostring(app.display) or ""
            local cc_req_type_display = (cc_req_type and cc_req_type.display) and tostring(cc_req_type.display) or "-"
            if not cmd_cc_req_result_counts[cmd_code] then
                cmd_cc_req_result_counts[cmd_code] = {}
                cmd_cc_req_result_names[cmd_code] = {}
                cmd_cc_req_totals[cmd_code] = 0
                cmd_cc_req_display_names[cmd_code] = cmd_display
                app_cc_req_display_names[cmd_code] = {}
                cc_req_type_display_names[cmd_code] = {}
            end
            local app_key = app_display
            if not cmd_cc_req_result_counts[cmd_code][val] then
                cmd_cc_req_result_counts[cmd_code][val] = {}
            end
            cmd_cc_req_result_counts[cmd_code][val][app_key] = (cmd_cc_req_result_counts[cmd_code][val][app_key] or 0) + 1
            cmd_cc_req_result_names[cmd_code][val] = name
            cmd_cc_req_totals[cmd_code] = cmd_cc_req_totals[cmd_code] + 1
            cmd_cc_req_display_names[cmd_code] = cmd_display
            app_cc_req_display_names[cmd_code][app_key] = app_display
            cc_req_type_display_names[cmd_code][app_key] = cc_req_type_display
        end
    end

    local function remove()
		tap:remove();
	end

    function tap.draw()
        win:clear()
        win:append("Diameter Result Code Summary\n\n")
        win:append(string.format("%-15s %-45s %-10s %-10s\n", "Result Code", "Result Name", "Count", "Percent"))
        win:append(string.rep("-", 80) .. "\n")

        -- Collect and sort codes numerically
        local codes = {}
        for code, _ in pairs(result_counts) do
            table.insert(codes, tonumber(code))
        end
        table.sort(codes)
        for _, code_num in ipairs(codes) do
            local code = tostring(code_num)
            local count = result_counts[code]
            local name = result_names[code] or ""
            local percent = (count / total) * 100
            win:append(string.format("%-15s %-45s %-10d %-6.2f%%\n", code, name, count, percent))
        end
        win:append("\nTotal messages with result code: " .. total .. "\n\n")

        -- Per-source-IP table, sorted globally by result code
        win:append("Error Codes Summary by Source IP\n\n")
        win:append(string.format("%-15s %-45s %-18s %-30s %-10s %-10s\n", "Result Code", "Result Name", "Source IP", "App ID", "Count", "Percent"))
        win:append(string.rep("-", 130) .. "\n")
        -- Collect all (code, ip, app_display) rows
        local code_ip_app_rows = {}
        for ip, code_table in pairs(ip_result_counts) do
            for code, app_table in pairs(code_table) do
                for app_display, count in pairs(app_table) do
                    table.insert(code_ip_app_rows, {
                        code_num = tonumber(code),
                        code = code,
                        name = ip_result_names[ip][code][app_display] or "",
                        ip = ip,
                        app_display = ip_app_display[ip][code][app_display] or app_display,
                        count = count,
                        percent = (count / total) * 100
                    })
                end
            end
        end
        table.sort(code_ip_app_rows, function(a, b)
            if a.code_num == b.code_num then
                return a.count > b.count  -- Sort by count descending
            else
                return a.code_num < b.code_num
            end
        end)
        for _, row in ipairs(code_ip_app_rows) do
            win:append(string.format("%-15s %-45s %-18s %-30s %-10d %-6.2f%%\n", row.code, row.name, row.ip, row.app_display, row.count, row.percent))
        end

        -- Per-command-code and application id table, sorted globally by result code
        win:append("\nError Codes Summary by Command Code and Application ID\n\n")
        win:append(string.format("%-15s %-45s %-30s %-30s %-10s %-10s\n", "Result Code", "Result Name", "Cmd Code", "App ID", "Count", "Percent"))
        win:append(string.rep("-", 140) .. "\n")
        -- Collect all (code, cmd_code, app_id) pairs
        local code_cmd_app_rows = {}
        for cmd_code, code_table in pairs(cmd_result_counts) do
            for code, app_table in pairs(code_table) do
                for app_key, count in pairs(app_table) do
                    table.insert(code_cmd_app_rows, {
                        code_num = tonumber(code),
                        code = code,
                        name = cmd_result_names[cmd_code][code] or "",
                        cmd_code = cmd_code,
                        cmd_display = cmd_display_names[cmd_code] or cmd_code,
                        app_display = app_display_names[cmd_code][app_key] or app_key,
                        count = count,
                        percent = (count / total) * 100
                    })
                end
            end
        end
        -- Sort by code number, then by command code, then by application id
        table.sort(code_cmd_app_rows, function(a, b)
            if a.code_num == b.code_num then
                        return a.count > b.count  -- Sort by count descending

            else
                return a.code_num < b.code_num
            end
        end)
        for _, row in ipairs(code_cmd_app_rows) do
            win:append(string.format("%-15s %-45s %-30s %-30s %-10d %-6.2f%%\n", row.code, row.name, row.cmd_display, row.app_display, row.count, row.percent))
        end

        -- Per-command-code with CC-Request-Type and application id table, sorted globally by result code
        win:append("\nError Codes Summary by Command Code, CC-Request-Type and Application ID\n\n")
        win:append(string.format("%-15s %-45s %-30s %-30s %-30s %-10s %-10s\n", "Result Code", "Result Name", "Cmd Code", "CC-Request-Type", "App ID", "Count", "Percent"))
        win:append(string.rep("-", 173) .. "\n")
        -- Collect all (code, cmd_code, cc_req_type, app_id) rows
        local code_cmd_cc_req_app_rows = {}
        for cmd_code, code_table in pairs(cmd_cc_req_result_counts) do
            for code, app_table in pairs(code_table) do
                for app_key, count in pairs(app_table) do
                    table.insert(code_cmd_cc_req_app_rows, {
                        code_num = tonumber(code),
                        code = code,
                        name = cmd_cc_req_result_names[cmd_code][code] or "",
                        cmd_code = cmd_code,
                        cmd_display = cmd_cc_req_display_names[cmd_code] or cmd_code,
                        cc_req_type_display = cc_req_type_display_names[cmd_code][app_key] or "-",
                        app_display = app_cc_req_display_names[cmd_code][app_key] or app_key,
                        count = count,
                        percent = (count / total) * 100
                    })
                end
            end
        end
        -- Sort by code number, then by count descending
        table.sort(code_cmd_cc_req_app_rows, function(a, b)
            if a.code_num == b.code_num then
                return a.count > b.count  -- Sort by count descending
            else
                return a.code_num < b.code_num
            end
        end)
        for _, row in ipairs(code_cmd_cc_req_app_rows) do
            win:append(string.format("%-15s %-45s %-30s %-30s %-30s %-10d %-6.2f%%\n", row.code, row.name, row.cmd_display, row.cc_req_type_display, row.app_display, row.count, row.percent))
        end

        -- we tell the window to call the remove() function when closed
        win:set_atclose(remove)
    end
    
    retap_packets()
end

-- Register the plugin menu
local function register_plugin_menu()

    -- Create submenu
    register_menu("Diameter Result Code Summary", generate_diam_stats,MENU_TOOLS_UNSORTED)

end

-- Initialize the plugin
local function init()
    register_plugin_menu()
    print("Diameter Result Summary Wireshark Plugin loaded successfully!")
end

if not gui_enabled() then return end
-- Plugin initialization
init() 