### Customer specific configuration

### Customer specific configuration

# define your known UML participants here
# key can be:
# - ip address (for HTTP, SIP & Diameter)
# - SCCP GT (global title) for MAP & CAMEL
# it is allowed to define multiple keys (even IP & GT) pointing to the same
# node
# !!! it doesn't matter order of definition
# this list is unordered

participants = {
    '1.1.1.1':'TAS'
    ,'2.2.2.2':'CSCF'
# for example, one logical DRA has two instances
    ,'3.3.3.3':'DRA'
    ,'4.4.4.4':'DRA'
# GT
    ,'79111111111':'MSS'
    ,'79222222222':'OCS'
    ,'79333333333':'HLR'
# TAS GT in addition to it's IP
    ,'79444444444':'TAS'
    }

# here you define the same set of participants
# but order of declaration is important
# the only name of participant has a matter, other parameters are just for
# decoration purpose

uml_intro = """
@startuml
/'
{comment}
'/
hide unlinked

participant "UE-A" as 1.2.1.2

participant "UE-B" as 1.2.1.3

participant "CSCF \\n 2.2.2.2" as CSCF
participant "DRA" as DRA

participant "TAS \\n 4.4.4.4 \\n 7944444444" as TAS

participant "OCS \\n 79222222222" as OCS

participant "HLR" as HLR

autonumber "<b>[000]"

"""

# you can define your own UML style

### End of Customer specific configuration


uml_comment_template = """\n
source file: {cap_file}
current dir: {dir}
filter: {cap_filter}
generated at: {datetime}
using: {prog}
"""

uml_end = """
legend right
{legend}
endlegend
@enduml
"""
# in seconds
uml_delay = "\n... {seconds} seconds later...\n"

# seconds to report period
time_period=3

# seconds between timeframes when exceeded uml.delay() method is invoked 
timeframe_timeout = 2
defaul_cap_filter = "sip||sccp||diameter||http||gtpv2||s1ap||pfcp"
default_uml_file = "./out.uml"

# plantuml output
JAVA_BIN = '/usr/bin/java'
plantuml_jar = '/home/denis/soft/plantuml/plantuml-1.2025.0.jar'

# FOR SIP ONLY
# If callid index exceed list size, then color rules will be reused from begining
colors = ['red', 'blue', 'green', 'black', 'aqua', 'Brown', 'Coral', 'Magenta']

# FOR SIP ONLY
styles_callids = [f"-[#{color}]>" for color in colors[:-1]]

# FOR DIAM
styles_appsid = {
    #ApplicationId: 3GPP Gx (16777238)
    "16777238":'-[#blue]/',
    #ApplicationId: 3GPP Rx (16777236)
    "16777236":'-[#red]/',
    #ApplicationId: 3GPP S6a/S6d (16777251)
    "16777251":'-[#green]/'
    }

# FOR OTHER PROTO
uml_msg_color = {
    "diameter": "black",
    "gsm_map": "black",
    "camel": "black",
    "http": "green",
    "gtpv2":"red",
    "s1ap":"red",
    "pfcp":"red"
}

uml_line_style = {
    "diameter": "-[#black]/",
    "gsm_map": "-[#black]>o",
    "camel": "-[#black]>o",
    "http": "-[#green]>>",
    "gtpv2":"-[#red]>>",
    "s1ap":"-[#red]>>",
    "pfcp":"-[#red]>>"
}

# UML Draw templates
# headers that is used here must be defined in headers dict below
proto_formatter = {
    "camel": {
        "request": "{src} {line} {dst} : <color {color}> {local} {serviceKey} \\n {isup_calling} \\n {isup_called} \n\n"
    },
    "gsm_map": {
        "request": "{src} {line} {dst} : <color {color}> {gsm_old_localValue} {gsm_old_routingInfo} \n\n"
    },
    "sip": {
        "INVITE": "{src} {line} {dst} : {frame_num} <color {color}> {request_line} {status_line} \\n from: {from_user} \\n to: {to_user} \\n callid: {call_id} \\n {route} \\n supported: {supported} \\n p_early_media: {p_early_media} \\n require: {require} \\n {sdp}  \n\n",
        "reINVITE": "{src} {line} {dst} : {frame_num} <color {color}> re-INIVITE \\n callid: {call_id} \\n {route} \\n supported: {supported} \\n p_early_media: {p_early_media} \\n require: {require} \\n {sdp}  \n\n",
        "REFER": "{src} {line} {dst} : <color {color}> {request_line} {status_line} \\n from: {from_user} \\n to: {to_user} \\n refer-to: {refer_to:.40} \\n refered-by: {refered_by} \\n callid: {call_id} \n\n",
        "MESSAGE": "{src} {line} {dst} : <color {color}> {method} {status_line} \\n to: {to_user} \\n callid: {call_id} \\n {content_type} \\n {gsm_a_rp_msg_type} \\n gsm da: {gsm_sms_tp_da} \\n {gsm_sms_tp_mti}  \n\n",
        "INFO": "{src} {line} {dst} : <color {color}> {method} {status_line} \\n callid: {call_id} \\n {content_type} \n\n",
        "NOTIFY": "{src} {line} {dst} : <color {color}> {method} {status_line} \\n callid: {call_id} \\n event: {event} \\n state:{subscription_state} \n\n",
        "request": "{src} {line} {dst} : {frame_num} <color {color}> {method} {status_line} \\n callid: {call_id} \\n {sdp}  \n\n",
        "short": "{src} {line} {dst} : {frame_num} <color {color}> {method} {status_line} \n\n"
    },
    "diameter": {
        "request": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \n\n",
        
        "response": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {charging_rule_base_name} \\n \
{charging_rule_name} \\n {qos_class_identifier} \\n \
{max_requested_bandwidth_dl} \\n {max_requested_bandwidth_ul} \\n \
{apn_aggregate_max_bitrate_dl} {apn_aggregate_max_bitrate_ul} \\n \
{result_code} \\n {experimental_result_code} \n\n",
        
        #Sh
        #"Command Code: Subscribe-Notifications 
        "308": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {data_reference} \\n {subs_req_type} \\n {send_data_indication} \\n {3gpp_service_ind} \n\n",
        #"Command Code: User-Data (
        "306": "{src} {line} {dst} : Frame #{frame_num}at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {data_reference} \\n {3gpp_service_ind} \n\n",
                
        #Gx
        #"Command Code: Credit-Control (
        "272": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {cc_request_type} \\n {event_trigger} \\n {qos_class_identifier} \\n {bearer_usage} \n\n",
        
        #Rx
        #"Command Code: AA (
        "265": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n {rx_request_type} \\n {af_application_identifier} \\n \
{af_signalling_protocol} \\n {service_info_status} \\n {specific_action} \\n {flow_usage} \\n {media_type} \\n \
{max_requested_bandwidth_dl} \\n {max_requested_bandwidth_ul} \\n \
{rs_bandwidth} {rr_bandwidth} \n\n ",
        
        #"Command Code: Re-Auth (
        "258": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {specific_action} \\n {qos_class_identifier} \\n \
{charging_rule_base_name} \\n {charging_rule_name} \\n {af_signalling_protocol} \\n \
{max_requested_bandwidth_dl} \\n {max_requested_bandwidth_ul} \\n \
{guaranteed_bitrate_dl} \\n {guaranteed_bitrate_ul} \\n \
{apn_aggregate_max_bitrate_dl} \\n {apn_aggregate_max_bitrate_ul} \n\n",
        
        #"Command Code: Abort-Session (
        "274": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {abort_cause} \n\n",
        #"Command Code: Session-Termination (
        "275": "{src} {line} {dst} : Frame #{frame_num} at {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n {termination_cause} \n\n"
    },
    "http": {
        "request": "{src} {line} {dst} : <color {color}> {request_method} {request_uri} \\n {x_3gpp_asserted_identity} \\n {content_type} \n\n",
        "response": "{src} {line} {dst} : <color {color}> {response_code} {response_phrase} \\n {content_type} \n\n"
    },
    "gtpv2": {
        "request": "{src} {line} {dst} : {frame_num} <color {color}> {message_type} \\n {seq} \\n {teid} \\n {cause} \n\n"
    },
    "s1ap": {
        "request": "{src} {line} {dst} : {frame_num} <color {color}> {procedurecode} \n\n"
    },
   "pfcp": {
        "request": "{src} {line} {dst} : {frame_num} <color {color}> {msg_type} \\n {seqno} \\n {seid} \\n {cause} \n\n"       
   }
}

uml_draw_keys = ['local', 'gsm_old_localValue', 'method', '__cmd_code__', 'request_method','__message_type__','__msg_type__']

proto_msg_skip = {
    "sip": {
        "method": ['PRACK', 'ACK'],
        "status_code": ['100', '180', '183']
    },
    "diameter": {
        # filter by private (short) cmd code
        "__cmd_code__": ['280','996','999'],
        "__applicationid__":['16777294']
    }
}

sdp_media_attrs = ['sendrecv', 'sendonly', 'recvonly', 'inactive']

# headers per each protocol that will be extracted
headers = {
    "camel": {"long": ['local', 'serviceKey', 'isup_called', 'isup_calling']},
    "gsm_map": {"long": ['gsm_old_localValue', 'gsm_old_routingInfo']},
    "sip": {
        "short": [
            'request_line', 'status_line', 'method', 'cseq_method', 'cseq',
            'status_code', 'from_user', 'to_user', 'refer_to', 'refered_by',
            'content_length', 'content_type', 'call_id', 
           # for preconditions and early media
            'require', 'supported','p_early_media',
           # notify
           'event','subscription_state',
           # have to be here to extract term/orig and skipifc params
            'route', 
           # MESSAGE parameters
            'gsm_sms_tp_da'
        ],
        # MESSAGE parameters with description
        "long": ['gsm_sms_tp_mti', 'gsm_a_rp_msg_type']
    },
    "sdp": {
        "short": [
            'sdp_connection_info_address','sdp_media'
        ],
        "multi": [
            'sdp_media_attr','sdp_session_attr'
            ]
    },
    "diameter": {
        "long": [
            'user_authorization_type','session_id',
            'experimental_result_code', 'result_code', 'data_reference',
            'subs_req_type', 'send_data_indication', '3gpp_service_ind',
            'service_info_status', 'specific_action', 'abort_cause', 'termination_cause',
            'cc_request_type','ip_can_type','bearer_usage',
            'af_signalling_protocol',
            'rx_request_type','af_application_identifier',
            'qos_information','rs_bandwidth','rr_bandwidth'
        ],
        "short": ['flags_request'],
        # double will do the following:
        # put long version into value as assigned
        # put short version into value with prefix "__" and suffix "__" (as private var)
        "double": ['cmd_code','applicationid'],
        "multi": ['charging_rule_name','charging_rule_base_name',
                  'qos_class_identifier',
                  'apn_aggregate_max_bitrate_dl','apn_aggregate_max_bitrate_ul',
                  'max_requested_bandwidth_dl','max_requested_bandwidth_ul',
                  'guaranteed_bitrate_dl','guaranteed_bitrate_ul',
                  'flow_usage','media_type',
                  'event_trigger'                  
                  ]
    },
    "http": {
        "short": [
            'request_uri', 'request_method', 'response_code', 'response',
            'response_phrase', 'request', 'content_length', 'content_type'
        ]
    },
    "http_request_line": {
        "short": ['x-3gpp-asserted-identity']
    },
    "gtpv2" : { "double":["message_type"],
               "long":["rat_type","teid","cause","seq"]
        
    },
    "s1ap" : { "double":["procedurecode"]
    },
   "pfcp" : {"double":["msg_type"],
            "long":["seid","cause","seqno"]
             }
}

header_params = {
    "route": ['orig', 'mode=terminating', 'skipIFC']
}