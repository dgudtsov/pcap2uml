#!/usr/bin/env python
# encoding: utf-8
'''
pcap2uml -- shortdesc

pcap2uml is a description

It defines classes_and_methods

@author:     Denis Gudtsov

@copyright:  2016-2025 Denis Gudtsov. All rights reserved.

@license:    GPL

@contact:    user_email
@deffield    updated: Updated
'''

# Minimum python version is 3.6
MIN_PYTHON = (3, 6)

import sys
import os
import subprocess
from optparse import OptionParser
import pyshark
import textwrap
import re
import time

from conf.conf_uml import *
from textwrap import dedent

from datetime import timedelta, datetime

__all__ = []
__version__ = 0.6
__date__ = '2025-03-19'
__updated__ = '2025-06-20'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

unkn_participants = {}

process_duration=0

# Accounts for participants
class Participant(object):
    def __init__(self, participant, mode_term_orig=None):
        if participant in participants:
            self.name = participants[participant]
            if mode_term_orig is not None:
                self.name += "_" + mode_term_orig
        else:
            if DEBUG: 
                print("unknown participant: ", participant)
            self.name = participant
            unkn_participants[participant] = ""

# Stores calls processed and defines line styles for new calls
class Calls(object):
    list_callids = []
    calls_processed = []

    def call_proceeded(self, msg_digest):
        """Append msg_digest into calls_processed list"""
        self.calls_processed.append(msg_digest)

    def is_call_proceeded(self, msg_digest):
        return msg_digest in self.calls_processed

    def order_callid(self, callid):
        """Get numeric value of callid in list_callids"""
        if callid not in self.list_callids:
            self.list_callids.append(callid)
        return self.list_callids.index(callid)

    def get_line_style_by_callid(self, callid):
        return styles_callids[self.order_callid(callid) % len(styles_callids)]

    def get_color_by_callid(self, callid):
        return colors[self.order_callid(callid) % len(colors)]

    def is_first_callid(self, callid):
        return callid not in self.list_callids

# Universal class to process sip, diameter, map and camel messages
class Message(object):
    """Base class for Message object (extends Layer representation)."""
    
    frame_num = 0
    msg_params = {}
    msg_digest = {}
    draw_key = None

    def __init__(self, layer):
        self.msg_params = dict()
        self.msg_digest = dict()
        self.proto = layer.layer_name
        self.process_headers(layer)
        self.layer = layer
        self.sniff_timestamp = None

        
        if self.proto in proto_msg_skip:
            self.msg_skip = proto_msg_skip[self.proto]
        self.__draw_key__()

    def __draw_key__(self):
        for i in uml_draw_keys:
            if i in self.msg_params:
                self.draw_key = self.msg_params[i]

    def add_param(self, key, value):
        self.msg_params[key] = value

    def __getattr__(self, key):
        """Gets the key in the given key name."""
        try:
            return self.msg_params[key]
        except KeyError:
            raise AttributeError(f"'Message' object has no attribute '{key}'")

    def process_headers(self, layer):
        for header_type in headers[layer.layer_name]:
            for header in headers[layer.layer_name][header_type]:
                self.extract_header(layer, header, header_type)

    def extract_header(self, layer, header, header_type):
        value = layer.get_field(header)
        if value is None:
            self.msg_params[header] = ""
        else:
            if header_type == "long":
                self.msg_params[header] = value.showname                
            elif header_type == "short" :
                #put value instead of object
                self.msg_params[header] = value.show
            elif header_type == "double":
                self.msg_params[header] = value.showname    #or showname_value
                self.msg_params[f"__{header}__"] = value.show
            elif header_type == "multi":
                if len(value.fields)==1:
                    # single value
                    self.msg_params[header] = value.showname
                elif len(value.fields)>1:
                    #list generator
                    if uml_tables_enabled:
                        self.msg_params[header]="| "+' | '.join([p.showname for p in value.fields])+" |"
                    else:
                        self.msg_params[header]=[p.showname for p in value.fields]
                                              
            elif header_type == "multiline":
                if len(value.fields)==1:
                    # single value
                    self.msg_params[header] = value.showname
                elif len(value.fields)>1:
                    #list generator

#                    self.msg_params[header]=f"|{value.showname_key} |"+' | '.join([p.showname_value for p in value.fields])+"|"
                    if uml_tables_enabled:
                        self.msg_params[header]='\\n'.join(f"|{value.showname_key} | {p.showname_value} |" for p in value.fields)
                    else:
                        self.msg_params[header]={value.showname_key:[p.showname_value for p in value.fields]}                                            

# Specific class for GTP messages
class Message_GTP(Message):
    def __init__(self, layer):
        super().__init__(layer)
    def skip(self):
        for key,values in self.msg_skip.items():
            if self.msg_params[key] in values:
                return True

# Specific class for GTP messages
class Message_PFCP(Message):
    def __init__(self, layer):
        super().__init__(layer)
        
# Specific class for S1AP messages
class Message_S1AP(Message):
    def __init__(self, layer):
        super().__init__(layer)       

# Specific class for SCCP messages
class Message_SCCP(Message):
    def __init__(self, layer):
        super().__init__(layer)    

# Specific class for Diameter messages
class Message_Diam(Message):
    def skip(self):
        for key,values in self.msg_skip.items():
            if self.msg_params[key] in values:
                return True
            
#         if self.msg_params['cmd_code'] in self.msg_skip['cmd_code']:
#             return True
#         if self.msg_params['applicationid'] in self.msg_skip['applicationid']:
#             return True
        return False

# Specific class for SIP messages
class Message_SIP(Message):
    def __init__(self, layer):
        super().__init__(layer)
        self.msg_params["sdp"] = ""
        self.msg_params["mode_term_orig"] = "term"

    def update_digest(self):
        self.msg_digest = dict(
            call_id=self.call_id,
            cseq=self.cseq,
            src=self.src,
            dst=self.dst
        )

    def get_hash(self):
        return dict(
            call_id=self.call_id,
            cseq=self.cseq,
            method=self.method
        )

    def has_sip_route(self):
        return len(self.route) > 0
    
    def route_parse(self, layer):
        route_str = ""
        for p in layer.route_param.fields:
            for param in header_params['route']:
                if param == p.showname_value:
                    route_str += p.showname_value + " "
                    if param == 'orig':
                        self.mode_term_orig = 'orig'
        self.msg_params['route'] = route_str

    def has_sdp(self):
        return (int(self.content_length) > 0) and (self.content_type == "application/sdp")

    def sdp_parse(self, layer):
        for header_type in headers['sdp']:
            for header in headers['sdp'][header_type]:
                self.extract_header(layer, header, header_type)

#TODO:
# keep single (first) sdp media attr
        a_attr = s_attr = None
        if self.sdp_media_attr:
            a_attr=self.sdp_media_attr[0]
#            for mattr in self.sdp_media_attr.fields:
#                if mattr.show in sdp_media_attrs:
#                    a_attr = mattr.show
#                    break

#TODO: find another trace, rewrite
        if self.sdp_session_attr:
            s_attr=self.sdp_session_attr[0]
#             for sattr in self.sdp_session_attr.fields:
#                 if sattr.show in sdp_media_attrs:
#                     s_attr = sattr.show
#                     break

        sdp_str = "c=" + self.sdp_connection_info_address + " \\n "
        sdp_str += "m=" + self.sdp_media + " \\n "
        if a_attr:
            sdp_str += "a=" + a_attr + " \\n "
        if s_attr:
            sdp_str += "s=" + s_attr + " \\n "
        self.msg_params['sdp'] = sdp_str

    def skip(self):
        return not (
            (self.msg_params['method'] not in self.msg_skip['method'] and
            self.msg_params['cseq_method'] not in self.msg_skip['method'] and
            self.msg_params['status_code'] not in self.msg_skip['status_code'])
            or self.has_sdp()
        )

class Message_HTTP(Message):
    def __init__(self, layer):
        super().__init__(layer)
        self.msg_params["request_line"] = ""

    def parse_request_line(self):
        if self.layer.get_field('request_line') is not None:
            if len(self.layer.get_field('request_line').all_fields) > 1:
                for rl in self.layer.get_field('request_line').fields:
                    for header_type in headers['http_request_line']:
                        for header in headers['http_request_line'][header_type]:
                            field_name = header.replace('.', '_').replace('-', '_').lower()
                            if rl.show.find(header) >= 0:
                                value = rl.showname if header_type == 'showname' else rl.show
                                self.msg_params[field_name] = value

class UML(object):
    
    def __init__(self, uml_intro):
        self.uml = uml_intro
        self.last_frame_timestamp=None

    def normalize(self, text):
        return dedent('\\n'.join(str(x) for x in text.split('\\n') if len(x)>3))

    def shorter(self, strf):
        return re.sub(r'^(.{10}).*(.{20})$', r'\g<1>...\g<2>', strf)
    
    def draw(self, MSG, line_style, color, style=None):
        
        params = MSG.msg_params.copy()
        params['frame_num'] = MSG.frame_num
        params['sniff_timestamp'] = MSG.sniff_timestamp
        
        if 'call_id' in params:
            params['call_id'] = self.shorter(params['call_id'])

        if DEBUG:
            tmp = proto_formatter[MSG.proto].get(
                style if style else MSG.draw_key,
                proto_formatter[MSG.proto]["request"]
            )
            print("drawing frame: ", MSG.frame_num)
            print(tmp)
        
        if self.last_frame_timestamp is not None:
            # sometimes frames in pcap has not presize timestampts 
            if MSG.sniff_timestamp > self.last_frame_timestamp:
                time_diff = MSG.sniff_timestamp - self.last_frame_timestamp
                if time_diff.seconds > timeframe_timeout:
                    self.delay(time_diff.seconds)
        
        try:
            draw = proto_formatter[MSG.proto].get(
                style if style else MSG.draw_key,
                proto_formatter[MSG.proto]["request"]
            ).format(
                line=line_style,
                color=color,
                **params
            )
            
            self.last_frame_timestamp=MSG.sniff_timestamp
            
        except KeyError as e:
            print(f'I got a KeyError - reason "{str(e)}"')
        else:
            self.uml += self.normalize(draw)
    
    def process(self,action):
        self.uml += self.normalize(action)
    
    def delay(self, delay_sec):
        self.uml += uml_delay.format(seconds=delay_sec)
        
    def finalize(self, legend):
        self.uml += uml_end.format(legend=legend)

    def dump_to_file(self, filename):
        with open(filename, 'w', encoding='utf-8') as uml_file:
            uml_file.write(self.uml)

def process_cap(cap_file, cap_filter, uml_file, diam_filter):
    try:
        cap = pyshark.FileCapture(input_file=cap_file, display_filter=cap_filter,keep_packets=False)
    except Exception as e:
        sys.stderr.write(f"Error opening pcap file: {str(e)} \n")
        return 2
    
    uml_legend = uml_comment_template.format(
        datetime=datetime.now(),
        prog=program_version_string,
        cap_file=cap_file,
        cap_filter=cap_filter,
        dir=os.getcwd()
    )
    
    uml = UML(uml_intro.format(comment=uml_legend))
    
    print("Processing file: ",cap_file)
    print("")
    
    sip_calls = Calls()
    prev_sip_message = {}
    last_frame_timestamp = 0

#    time_start = previous_time = time.time()

    time_start = previous_time = int(time.time())

    for frame in cap:
        if (int(time.time())-previous_time>=time_period):
            previous_time = int(time.time())
            print(f"[{previous_time-time_start} sec] Frames processed: {frame.number}")
        
        if 'sip' in frame:
            for layer in frame.layers:
                if layer.layer_name == 'sip':
                    SIP = Message_SIP(layer)
                    SIP.frame_num = frame.number
                    
                    if len(SIP.method)==0 and len(SIP.status_code)==0:
                        print("malformed SIP packet in frame #",SIP.frame_num)
                        continue
                    
                    if DEBUG:
                        print("SIP frame:", SIP.frame_num)
                        print(" src:", frame.ip.src, " dst:", frame.ip.dst)
                        print(" call-id:", SIP.call_id)

                    if SIP.has_sdp():
                        SIP.sdp_parse(layer)
                    if SIP.has_sip_route():
                        SIP.route_parse(layer)
# rescan ip layers
# useful when SIP inside GTP layer
                    for l in frame.layers:
                        if l.layer_name == 'ip':
                            src=l.src
                            dst=l.dst

#                     SIP.add_param("src", Participant(frame.ip.src).name)
#                     SIP.add_param("dst", Participant(frame.ip.dst).name)

                    SIP.add_param("src", Participant(src).name)
                    SIP.add_param("dst", Participant(dst).name)

                    #sniff_timestamp attr is used to draw uml.delay() in case of time difference between frames exceed timeframe_timeout
#                    SIP.add_param("sniff_timestamp",datetime.utcfromtimestamp(float(frame.sniff_timestamp)))
                    
                    SIP.sniff_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))


                    call_id_reinv = not sip_calls.is_first_callid(SIP.call_id)
                    line_style = sip_calls.get_line_style_by_callid(SIP.call_id)
                    color = sip_calls.get_color_by_callid(SIP.call_id)
                    SIP.update_digest()

                    if (not SIP.skip()) and (not sip_calls.is_call_proceeded(SIP.msg_digest)):
#                         if last_frame_timestamp > 0:
#                             curr_frame_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))
#                             time_diff = curr_frame_timestamp - datetime.utcfromtimestamp(float(last_frame_timestamp))
#                             if time_diff.seconds > timeframe_timeout:
#                                 uml.delay(time_diff.seconds)
                        
#                        last_frame_timestamp = frame.sniff_timestamp
                        sip_calls.call_proceeded(SIP.msg_digest)

                        if SIP.get_hash() == prev_sip_message:
                            uml.draw(SIP, line_style, color, "short")
                        elif SIP.method == "INVITE" and call_id_reinv:
                            uml.draw(SIP, line_style, color, "reINVITE")
                        else:
                            uml.draw(SIP, line_style, color)

                        prev_sip_message = SIP.get_hash()

        elif 'diameter' in frame:
            for layer in frame.layers:
                if layer.layer_name == 'diameter':
                    DIAM = Message_Diam(layer)
                    DIAM.frame_num = frame.number
                    if not DIAM.skip():
                        
                        # applying 2nd pass filter. considering all diam messages has session id attribute
                        if len(diam_filter)==0 or layer.session_id.lower() in diam_filter:
                            
                            if hasattr(frame, 'ip'):
                                # iterate over all ip layers
                                for l in frame.layers:
                                    if l.layer_name=='ip':
                                        src = l.src
                                        dst = l.dst
                            elif hasattr(frame, 'ipv6'):
                                src = f"\"{frame.ipv6.src}\""
                                dst = f"\"{frame.ipv6.dst}\""
                            else:
                                print("malformed frame #",SIP.frame_num)
                                continue
    
                                
                            
                            DIAM.add_param("src", Participant(src).name)
                            DIAM.add_param("dst", Participant(dst).name)
                            
                            #sniff_timestamp attr is used to draw uml.delay() in case of time difference between frames exceed timeframe_timeout
                            DIAM.sniff_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))
                            
                            #default
                            line_style=uml_line_style[layer.layer_name]
                            
                            # try to colorize different apps
                            try:
                                line_style=styles_appsid[DIAM.msg_params["__applicationid__"]]
                            except KeyError as e:
                                print(f"'styles_appsid' list has no definition for app id {DIAM.msg_params['applicationid']}")
                            
                            if DIAM.flags_request == '1':
                                uml.draw(DIAM, line_style, uml_msg_color[layer.layer_name])
                            else:
                                uml.draw(DIAM, line_style, uml_msg_color[layer.layer_name], "response")
                        else:
                            print(f"Skipping frame #{DIAM.frame_num}, {DIAM.session_id}")

        elif 'sccp' in frame:
            for layer in frame.layers:
                if layer.layer_name in ['camel', 'gsm_map']:
                    SCCP = Message_SCCP(layer)
                    SCCP.add_param("src", Participant(frame.sccp.calling_digits).name)
                    SCCP.add_param("dst", Participant(frame.sccp.called_digits).name)
                    uml.draw(SCCP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])

        elif 'http' in frame:
            for layer in frame.layers:
                if layer.layer_name == 'http':
                    HTTP = Message_HTTP(layer)
                    HTTP.add_param("src", Participant(frame.ip.src).name)
                    HTTP.add_param("dst", Participant(frame.ip.dst).name)
                    HTTP.parse_request_line()
                    if HTTP.response == '1':
                        uml.draw(HTTP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name], "response")
                    else:
                        uml.draw(HTTP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])
        elif 'gtpv2' in frame:
            for layer in frame.layers:
                if layer.layer_name == 'gtpv2':
                    GTP = Message_GTP(layer)
                    GTP.frame_num = frame.number
                    
                    if not GTP.skip():
                        GTP.add_param("src", Participant(frame.ip.src).name)
                        GTP.add_param("dst", Participant(frame.ip.dst).name)
                            
                            #sniff_timestamp attr is used to draw uml.delay() in case of time difference between frames exceed timeframe_timeout
                        GTP.sniff_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))
                        
                        uml.draw(GTP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])

        elif 's1ap' in frame:
            for layer in frame.layers:
                if layer.layer_name == 's1ap':
                    S1AP = Message_S1AP(layer)
                    S1AP.frame_num = frame.number
                    
                    S1AP.add_param("src", Participant(frame.ip.src).name)
                    S1AP.add_param("dst", Participant(frame.ip.dst).name)
                        
                        #sniff_timestamp attr is used to draw uml.delay() in case of time difference between frames exceed timeframe_timeout
                    S1AP.sniff_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))
                    
                    uml.draw(S1AP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])                    
                    
        elif 'pfcp' in frame:
            for layer in frame.layers:
                if layer.layer_name == 'pfcp':
                    PFCP = Message_PFCP(layer)
                    PFCP.frame_num = frame.number
                    PFCP.add_param("src", Participant(frame.ip.src).name)
                    PFCP.add_param("dst", Participant(frame.ip.dst).name)
                        
                        #sniff_timestamp attr is used to draw uml.delay() in case of time difference between frames exceed timeframe_timeout
                    PFCP.sniff_timestamp = datetime.utcfromtimestamp(float(frame.sniff_timestamp))
                    
                    uml.draw(PFCP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])
                    
    uml.finalize(uml_legend)
    uml.dump_to_file(uml_file)

    if DEBUG:
        print("all calls processed:", sip_calls.calls_processed)

    if unkn_participants:
        print("Unknown participants:")
        print("--add this into conf_participants.py:")
#        print(unkn_participants)
        print (", ".join(map(lambda item: f"'{item[0]}':'NAME'", unkn_participants.items())))

        print("\n--OR add this into participants.csv:")
        print ("\n".join(map(lambda item: f"{item[0]},NAME", unkn_participants.items())))
        print("\nReplacing NAME with actual node name\n")
    print("UML output written to", uml_file)

def main(argv=None):
    '''Command line options.'''
    
    program_name = os.path.basename(sys.argv[0])
    program_version = __version__
    program_build_date = __updated__
    global program_version_string 
    program_version_string = f'{program_name} {program_version} ({program_build_date})'
    
    program_license = "Copyright (c) 2016-2025 Denis Gudtsov. Licensed under Apache 2.0 License"
    
    print(program_version_string)


    if argv is None:
        argv = sys.argv[1:]
    
    try:
        parser = OptionParser(version=program_version_string, epilog=program_license)
        parser.add_option("-i", "--in", dest="cap_file", help="Input pcap file")
        parser.add_option("-o", "--out", dest="uml_file", help="Output uml file")
        parser.add_option("-t", "--to", dest="render_format", action="append", help="Output image format: svg, eps, png, txt")
        parser.add_option("-y", "--filter", dest="cap_filter", help="Pcap filter")
        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="Verbosity level")
        parser.add_option("-p", "--process", dest="process", action="count", help="add process duration on each participant")
        parser.add_option("-d", "--diam", dest="diam", action="count", help="cut diam sessions")

        parser.set_defaults(uml_file=default_uml_file, cap_filter=defaul_cap_filter)
        opts, args = parser.parse_args(argv)

        if not opts.cap_file:
            print("Input file is required!")
            return 2

    except Exception as e:
        print(f"Error: {e}")
        return 2

    if opts.verbose:
        print("verbose mode ON")
        DEBUG=1
        
    if opts.process:
        print("process duration on")
        process_duration=1
    # TODO: add sip.Call-ID filter as well, add radius Acct-Session-Id
    d=[]
    if opts.diam:
        if 'diameter.Session-Id'.lower() in opts.cap_filter.lower():
            d = re.findall(r'diameter\.session-id\s*==\s*"([^"]*)"', opts.cap_filter.lower())
            print("diam sessions filter:")
            print('\n'.join(d))
        else:
            print("-d/--diam option is enabled, but nothing 'diameter.Session-Id' found in -t/--filter option. Ignoring '-d/--diam'")
    
    process_cap(opts.cap_file, opts.cap_filter, opts.uml_file,d)

    if opts.render_format is not None:
        for format in opts.render_format:
            plantuml_format = f"-t{format}"
            exec_string = f"{JAVA_BIN} -jar {plantuml_jar} -duration -enablestats {plantuml_format} {opts.uml_file}"
            print(f"Rendering UML: {exec_string}")
            subprocess.call([JAVA_BIN, "-jar", plantuml_jar, "-duration","-enablestats",plantuml_format, opts.uml_file])
        else:
            print(f"output generated to: {opts.render_format}\n")
            print("for pdf use: inkscape input.svg -o output.pdf")
            print("or: rsvg-convert -f pdf -o output.pdf input.svg")

if __name__ == "__main__":
    
    assert sys.version_info >= MIN_PYTHON, f"requires Python {'.'.join([str(n) for n in MIN_PYTHON])} or newer"
    
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        cProfile.run('main()', 'pcap2uml_profile')
    sys.exit(main())