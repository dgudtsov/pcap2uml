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

# now participants are stored in external file
from conf.conf_participants import participants
import os

uml_intro = """
@startuml
/'
{comment}
'/
hide unlinked
skinparam backgroundColor #EEEEEE


participant UE
participant "UE-A" as 1.2.3.6
participant "UE-B" as 1.2.3.7
participant "UAG \\n 10.0.0.1" as UAG
participant "CSCF" as CSCF
participant "TAS \\n 10.0.0.3 \\n 70772039000" as TAS
participant "DRA" as DRA

participant eNB_1
participant eNB_2
participant eNB_3
participant eNB_4
participant eNB_5
participant MME
participant MME_1
participant MME_2
participant SPGWC
participant SPGWU
participant HSS

participant PGW
participant PGW1
participant PGW2
participant PGW3
participant PGW4

participant PCRF

participant PCSCF1
participant PCSCF2
participant PCSCF3


participant "AGW \\n 10.2.23.143" as AGW
participant "RMS" as RMS
participant "MRF \\n 10.2.23.154" as MRF
participant "MGCF/MSC \\n 10.68.19.1 \\n 79770000001" as MGCF
participant "OCS \\n 79000000012" as OCS
participant "BL \\n 79000000123" as BL
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

uml_process_duration_activate='activate {participant}'
uml_process_duration_deactivate='deactivate {participant}'

uml_tables_enabled=1

# seconds to report period
time_period=3

# seconds between timeframes when exceeded uml.delay() method is invoked 
timeframe_timeout = 2
defaul_cap_filter = "sip||sccp||diameter||http||gtpv2||s1ap||pfcp"
default_uml_file = "./out.uml"

# plantuml output
JAVA_BIN = '/usr/bin/java'
# use 'os.path.expanduser' to handle "~" in path name
plantuml_jar = os.path.expanduser('~/soft/plantuml/plantuml-1.2025.2.jar')

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
    "16777251":'-[#green]/',
    #ApplicationId: 3GPP S13/S13' (16777252)
    "16777252":'-[#yellow]/'
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
        "request": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \n\n",
        
        "response": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {session_id} \\n {cmd_code} {cc_request_type} \\n{event_trigger}\\n{charging_rule_base_name}\\n\
{charging_rule_name}\\n{qos_class_identifier}\\n\
{cc_total_octets}\\n{cc_input_octets}\\n{cc_output_octets}\\n\
{monitoring_key}\\n\
{usage_monitoring_level}\\n\
{max_requested_bandwidth_dl}\\n{max_requested_bandwidth_ul}\\n\
{apn_aggregate_max_bitrate_dl}\\n{apn_aggregate_max_bitrate_ul}\\n\
{bearer_control_mode}\\n\
{revalidation_time}\\n\
{result_code} \\n {experimental_result_code} \n\n",
        
        #Sh
        #"Command Code: Subscribe-Notifications 
        "308": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {data_reference} \\n {subs_req_type} \\n {send_data_indication} \\n {3gpp_service_ind} \n\n",
        #"Command Code: User-Data (
        "306": "{src} {line} {dst} : Frame #{frame_num}at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {data_reference} \\n {3gpp_service_ind} \n\n",
                
        #Gx
        #"Command Code: Credit-Control (
        "272": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code}, {cc_request_type} \\n {session_id} \\n{event_trigger}\\n\
{charging_rule_name}\\n\
{pcc_rule_status}\\n\
{apn_aggregate_max_bitrate_dl}\\n{apn_aggregate_max_bitrate_ul}\\n\
{rule_failure_code}\\n\
{cc_total_octets}\\n{cc_input_octets}\\n{cc_output_octets}\\n\
{monitoring_key}\\n\
{usage_monitoring_level}\\n\
{ip_can_type} {rat_type} \\n {network_request_support} \\n {qos_class_identifier} \\n {bearer_usage} \\n {framed_ip_address_ipv4} \\n {called_station_id} \n\n",
        
        #Rx
        #"Command Code: AA (
        "265": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n {rx_request_type} \\n {af_application_identifier} \\n\
{af_signalling_protocol} \\n {service_info_status} \\n{specific_action}\\n {flow_usage} \\n {media_type} \\n\
{flow_number}\\n\
{max_requested_bandwidth_dl} \\n {max_requested_bandwidth_ul} \\n\
{rs_bandwidth} {rr_bandwidth} \\n\
{flow_status}\\n\
{framed_ip_address_ipv4} \n \n",
        
        #"Command Code: Re-Auth (
        "258": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n{specific_action}\\n \
{charging_rule_base_name}\\n{charging_rule_name}\\n{af_signalling_protocol}\\n\
{qos_class_identifier}\\n\
{max_requested_bandwidth_dl}\\n{max_requested_bandwidth_ul}\\n\
{guaranteed_bitrate_dl}\\n{guaranteed_bitrate_ul}\\n\
{media_component_number}\\n\
{flow_number}\\n\
{resource_allocation_notification}\\n\
{apn_aggregate_max_bitrate_dl}\\n{apn_aggregate_max_bitrate_ul}\\n\
{cc_total_octets}\\n{cc_input_octets}\\n{cc_output_octets}\\n\
{monitoring_key}\\n\
{usage_monitoring_level}\\n\
{revalidation_time}\\n\
{session_release_cause} \n \n",
        
        #"Command Code: Abort-Session (
        "274": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n {abort_cause} \n\n",
        #"Command Code: Session-Termination (
        "275": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {applicationid}, {cmd_code} \\n {session_id} \\n {termination_cause} \n\n"
    },
    "http": {
        "request": "{src} {line} {dst} : <color {color}> {request_method} {request_uri} \\n {x_3gpp_asserted_identity} \\n {content_type} \n\n",
        "response": "{src} {line} {dst} : <color {color}> {response_code} {response_phrase} \\n {content_type} \n\n"
    },
    "gtpv2": {
        "request": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {message_type} \\n {seq} \\n {teid} \\n {cause} \n\n"
    },
    "s1ap": {
        "request": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {procedurecode} \n\n"
    },
   "pfcp": {
        "request": "{src} {line} {dst} : Frame #{frame_num} at UTC {sniff_timestamp} \\n <color {color}> {msg_type} \\n {seqno} \\n {seid} \\n {cause} \n\n"       
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
    },
    "gtpv2": {
        "__message_type__":['1','2']
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
            'service_info_status', 'abort_cause', 'termination_cause',
            'cc_request_type','ip_can_type','bearer_usage','rat_type',
            'network_request_support',
            'af_signalling_protocol',
            'rx_request_type','af_application_identifier',
            'qos_information','rs_bandwidth','rr_bandwidth',
            'framed_ip_address_ipv4',
            'called_station_id',
            'session_release_cause',
            'revalidation_time',
            'flow_status',
            'bearer_control_mode'
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
                  'rule_failure_code',
                  'pcc_rule_status',
                  'flow_number',
                  'media_component_number',
                  'resource_allocation_notification',
                  'monitoring_key',
                  'cc_total_octets','cc_input_octets','cc_output_octets',
                  'usage_monitoring_level'                  
                  ],
        "multiline": [
                  'event_trigger','specific_action'
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