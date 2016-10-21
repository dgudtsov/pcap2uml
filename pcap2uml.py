#!/usr/bin/env python
# encoding: utf-8
'''
pcap2uml -- shortdesc

pcap2uml is a description

It defines classes_and_methods

@author:     Denis Gudtsov

@copyright:  2016 Denis Gudtsov. All rights reserved.

@license:    GPL

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
from optparse import OptionParser
import pyshark
import textwrap

from conf.conf_uml import *
from textwrap import dedent


__all__ = []
__version__ = 0.2
__date__ = '2016-10-18'
__updated__ = '2016-10-21'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

unkn_participants = {}

# Accounts for participants
class Participant(object):
    def __init__ (self,participant):
        if participant in participants:
            self.name = participants[participant]
        else:
            if DEBUG: print "unknown participant: ", participant
            self.name = participant
            unkn_participants[participant]=""
#        participants.get(frame.ip.src, frame.ip.src), participants

# Stores calls processed and defines line styles for new calls
class Calls(object):

    list_callids = []

    calls_processed = []

    def call_proceeded(self,msg_digest):
        self.calls_processed.append(msg_digest)

    def is_call_proceeded(self,msg_digest):
        return msg_digest in self.calls_processed


    # input: callid string
    # output: numeric value of callid in list_callids
    def order_callid (self,callid):
        if self.list_callids.count(callid) == 0:
            self.list_callids.append(callid)

        order = self.list_callids.index(callid)
        return order

    def get_line_style_by_callid (self,callid):
        return styles_callids[self.order_callid(callid) % len(styles_callids)]

    def get_color_by_callid(self,callid):
#        max_color_num = len(colors)-1
        return colors[self.order_callid(callid) % len(colors)]

    def is_first_callid (self, callid):
        return (callid not in self.list_callids)

# Universal class to process sip, diameter, map and camel messages
class Message(object):
    """
    Base class for Message object (extends Layer representation).
    """

    frame_num = 0

    msg_params = {}
    msg_digest = {}

    draw_key = None

    def __init__(self,layer):
        self.msg_params = dict()
        self.msg_digest = dict()

        self.proto = layer.layer_name
        self.process_headers(layer)
        self.layer = layer

        self.__draw_key__()

    def __draw_key__(self):
        for i in uml_draw_keys:
            if i in self.msg_params:
                self.draw_key = self.msg_params[i]

    def add_param(self,key,value):
        self.msg_params[key] = value

    def __getattr__(self,key):
        """
        Gets the key in the given key name.
        :param key: packet index
        :return: attribute value.
        """
        return self.msg_params[key]

    def process_headers (self, layer):

#        for avp_type in headers['diameter']:
#            for avp in headers['diameter'][avp_type]:

        for header_type in headers[layer.layer_name]:

#        msg_headers = headers[layer.layer_name]
#        for header in msg_headers:
            for header in headers[layer.layer_name][header_type]:
                self.extract_header(layer, header, header_type)

    def extract_header (self, layer, header, header_type):
        value = layer.get_field(header)
#        self.msg_params[header] = value.showname if (value != None) else ""

        if value == None:
            self.msg_params[header] = ""
        else:
            # todo add += in case notifeff
            if header_type == "long":
                self.msg_params[header] = value.showname
            else:
                self.msg_params[header] = value

# leaved for future use
    def __format__(self, format):

        (keyname,method) = format.partition('.')[::2]

        if method == 'showname':
            result = self.layer.get_field(keyname).showname
        else:
            result = self.layer.get_field(keyname)

        pass
        return result

# Specific class for SIP messages
class Message_SIP(Message):

    def __init__(self,layer):

        Message.__init__(self,layer)
        self.msg_params["sdp"] = ""

    def update_digest(self):
        self.msg_digest = dict( call_id = self.call_id, cseq = self.cseq, src = self.src, dst = self.dst )

    def get_hash(self):
        return dict(call_id = self.call_id, cseq = self.cseq, method = self.method)

    def has_sdp(self):
        return (self.content_length > 0) & (self.content_type == "application/sdp")

    def sdp_parse(self,layer):

        for header_type in headers['sdp']:
            for header in headers['sdp'][header_type]:
                self.extract_header(layer, header, header_type)

        a_attr = s_attr = None

        if (self.sdp_media_attr):
            for mattr in self.sdp_media_attr.fields:
                if mattr.show in sdp_media_attrs:
                    a_attr = mattr.show
                    break

        if (self.sdp_session_attr):
            for sattr in self.sdp_session_attr.fields:
                if sattr.show in sdp_media_attrs:
                    s_attr = sattr.show
                    break
        sdp_str = ""
        sdp_str += "c="+self.sdp_connection_info_address+" \\n "
        sdp_str += "m="+self.sdp_media+" \\n "

        if (a_attr): sdp_str += "a="+a_attr+" \\n "
        if (s_attr): sdp_str += "s="+s_attr+" \\n "

        self.msg_params['sdp'] = sdp_str

class Message_HTTP(Message):

    def __init__(self,layer):
        Message.__init__(self,layer)
        self.msg_params["request_line"] = ""

    def parse_request_line(self):

        if self.layer.get_field('request_line') != None:
            if len(self.layer.get_field('request_line').all_fields)>1:
                for rl in self.layer.get_field('request_line').fields:
                    for header_type in headers['http_request_line']:
                        for header in headers['http_request_line'][header_type]:
                            field_name = header.replace('.', '_').replace('-', '_').lower()
                            if rl.show.find(header) >= 0:
                                # if header is defined in configuration
                                if header_type == 'showname':
                                    value = rl.showname
                                else:
                                    value = rl.show
                            else:
                                # if header is not found = ""
                                value = ""
                            self.msg_params[field_name]=value
#                        for mattr in self.sdp_media_attr.fields:


            pass


class UML(object):
    uml = ""

    def __init__(self,uml_intro):
        self.uml = uml_intro

    def normalize(self,str):
        dedented_text = textwrap.dedent(str)
#        tw = textwrap.fill(dedented_text, width=40,fix_sentence_endings=True)

#        tw += "\n \n"

#        return tw
        return dedented_text

    def draw(self, MSG, line_style, color, style=None):

        draw = proto_formatter[MSG.proto].get(style if (style) else MSG.draw_key,
                                             proto_formatter[MSG.proto]["request"]).format(
                                                 line = line_style,
                                                 color=color,
                                                 **MSG.msg_params)

        self.uml += self.normalize(draw)

    def finalize(self):
        self.uml +="\n@enduml\n"

    def dump_to_file(self,filename):
        with open(filename, 'w') as uml_file:
            uml_file.write(self.uml)

def process_cap(cap_file, cap_filter, uml_file):

    try:
        cap = pyshark.FileCapture(input_file=cap_file, display_filter=cap_filter)
    except:
        sys.stderr.write("source pcap file is not found %s \n",sys.exc_info())
        return 2


    uml = UML(uml_intro)

    sip_calls = Calls()

    prev_sip_message={}

    for i,frame in enumerate(cap):
        if 'sip' in frame:

            for layer in frame.layers:
                if (layer.layer_name in ['sip']):

                    SIP = Message_SIP(layer)

        #            SIP.frame_num = frame.number
                    if DEBUG:
                        print "SIP frame: ",i
                        print " src: ",frame.ip.src, " dst: ", frame.ip.dst, " proto: ", frame.ip.proto
                        print " call-id: ", frame.sip.call_id


#                    sip_content_len = SIP.content_length
#                    sip_content_type = SIP.content_type

                    if SIP.has_sdp():
                        SIP.sdp_parse(layer)

        #            src, dst = participants.get(frame.ip.src, frame.ip.src), participants.get(frame.ip.dst, frame.ip.dst)

                    SIP.add_param("src",Participant(frame.ip.src).name)
                    SIP.add_param("dst",Participant(frame.ip.dst).name)

                    call_id_reinv = not sip_calls.is_first_callid(SIP.call_id)

                    line_style = sip_calls.get_line_style_by_callid (SIP.call_id)
                    color = sip_calls.get_color_by_callid(SIP.call_id)

                    SIP.update_digest()


                    #print src," ",line_style," ", dst," : ", request_line, status_line,'\\n call-id:',call_id
                    if (((SIP.method not in proto_msg_skip[layer.layer_name]['method']) & \
                        (SIP.cseq_method not in proto_msg_skip[layer.layer_name]['method']) & \
                        (SIP.status_code not in proto_msg_skip[layer.layer_name]['status_code'])) | SIP.has_sdp() ) & \
                        (not sip_calls.is_call_proceeded(SIP.msg_digest)):

                        sip_calls.call_proceeded(SIP.msg_digest)

                        if SIP.get_hash()==prev_sip_message:
                            uml.draw(SIP, line_style, color,"short")

                        elif (SIP.method=="INVITE") & (call_id_reinv):
                            uml.draw(SIP, line_style, color,"reINVITE")

                        else:

                            uml.draw(SIP, line_style, color)

                        prev_sip_message = SIP.get_hash()

                        if DEBUG: print "..."

        elif 'diameter' in frame:
            for layer in frame.layers:
                if (layer.layer_name in ['diameter']):
                    if (layer.cmd_code not in proto_msg_skip[layer.layer_name]['cmd_code']) :
                        DIAM = Message (layer)

                        DIAM.add_param("src",Participant(frame.ip.src).name)
                        DIAM.add_param("dst",Participant(frame.ip.dst).name)

                        if (DIAM.flags_request == '1'):
                            uml.draw(DIAM, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])
                        else:
                            uml.draw(DIAM, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name],"response")

        elif ('sccp' in frame):
            for layer in frame.layers:
                if (layer.layer_name in ['camel','gsm_map']):
                    SCCP = Message(layer)
                    SCCP.add_param("src",Participant(frame.sccp.calling_digits).name)
                    SCCP.add_param("dst",Participant(frame.sccp.called_digits).name)

                    uml.draw(SCCP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])

        elif ('http' in frame):
            for layer in frame.layers:
                if (layer.layer_name in ['http']):
                        HTTP = Message_HTTP (layer)
                        HTTP.add_param("src",Participant(frame.ip.src).name)
                        HTTP.add_param("dst",Participant(frame.ip.dst).name)

# len(cap[0].http.request_line.all_fields)>1
                        HTTP.parse_request_line()


                        if (HTTP.response == '1'):
                            uml.draw(HTTP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name],"response")
                        else:
                            uml.draw(HTTP, uml_line_style[layer.layer_name], uml_msg_color[layer.layer_name])

    uml.finalize()

    uml.dump_to_file(uml_file)

    if DEBUG: print "all calls processed: ",sip_calls.calls_processed

    if len(unkn_participants)>0:
        print "all unknown particiapnts:"
        print unkn_participants

    print "output wrote into file ",uml_file

    print "to visualize it, run: java -jar plantuml.jar -tpng ",uml_file

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.2"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2016 Denis Gudtsov (CPM Ltd)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-i", "--in", dest="cap_file", help="set input pcap [default: %default]", metavar="FILE")
        parser.add_option("-o", "--out", dest="uml_file", help="set output uml [default: %default]", metavar="FILE")
        parser.add_option("-y", "--filter", dest="cap_filter", help="set pcap filter [default: %default]", metavar="FILTER")
        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")

        # set defaults
        parser.set_defaults(uml_file=default_uml_file, cap_filter=defaul_cap_filter)

        # process options
        (opts, args) = parser.parse_args(argv)

        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
        if opts.cap_file:
            print("infile = %s" % opts.cap_file)
        else:
            print("infile is not defined!")
            print("for help use --help")
            return

        if opts.uml_file:
            print("outfile = %s" % opts.uml_file)
        if opts.cap_filter:
            print("filter = %s" % opts.cap_filter)

    except Exception, e:
        indent = len(program_name) * " "
        exc_tb = sys.exc_info()
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help \n")
        return 2

    # MAIN BODY #
    process_cap(cap_file = opts.cap_file, cap_filter = opts.cap_filter, uml_file = opts.uml_file)


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'pcap2uml_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
