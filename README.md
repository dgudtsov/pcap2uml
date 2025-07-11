# pcap2uml
IMS Call flow visualizer for HTTP, SIP, Diameter, GSM MAP and CAMEL protocols  

This program can parse inpur pcap and generate result in plantuml format.

Project page: https://github.com/dgudtsov/pcap2uml  

Uses pyshark library: http://kiminewt.github.io/pyshark/  
and plantuml sequence diagram: http://plantuml.com/

# Prerequisite
Python 3.6

pyshark library https://github.com/KimiNewt/pyshark  

To install it:  
pip install pyshark  

Plantuml: http://plantuml.com/download

# What's new?
* Rewrote to Python 3.6, now support latest pyshark and lxml

* Added protocols:

  * GVPv2
  * PFCP
  * S1AP

* Improved protocol details render for diameter

* Modified sip details render according to new version of pyshark lib

* Now support multiple render_format, i.e. can generate png and svg at one pass

* Now participants configuration stored in separate file

* New experimental plugin for wireshark. Is doesn't ready for production yet, work in progress

* Added S13 interface, chnaged participants parsing behaviour: now list of csv files is used. Look at [readme](conf/participants/readme.txt)

* Added '-d/--diam' option. It is usefull in conjunction with '-y' filter option for cases when single frame contains more than one diameter packets. In such case wireshark doesn't apply properly diameter.Session-Id filter. Thus, session_id filter which mentioned in '-y' option will be applied in application level at second pass to filter out junk sessions messages which are not relevant to session beening selected.

# Configure

edit conf/conf_uml.py file:  
1. define 'participants' dict  
2. define 'uml_intro'  
3. define plantuml library and java path in JAVA_BIN and plantuml_jar params 


# Usage

run:  
./pcap2uml.py -i input.pcap -o out.uml -y filter -d -t format

where:  
input.pcap - source pcap (mandatory)  
out.uml - result diagram in PlanUML format (optional, default is ./out.uml)  
filter - wireshark view filter (optional, default = 'sip||sccp||diameter||http')  
format - png,svg,eps,pdf (optional)

As a result, plantuml diagram will be generated.  
If you have defined -t option, then appropriate document will be generated as well along with uml source

Then, to generate graphical version of diagram, run (if you didn't define -t option):  
java -jar plantuml.jar -tpng out.uml

The plantuml will generate out.png in result.

Or now you can generate in multiple formats at one pass:
python3 pcap2uml.py -i pcap.pcap -o out.uml -t png -t svg -t jpg

Thus you will get uml output plus png, jpg and svg are generated

## Usage notice

If you didn't define all parties in 'participants' dict in conf/conf_uml.py file OR in CSV files under conf/participants, then program will dump list of undefined participants for you. You can copy that list and paste it into configuration file and then fill it values with appropriate names.

Please note about filter syntax. It should be escaped and do not contains whitespaces, e.g.:
sip.Call-ID==\"0feX8451416300Q3beGhEfIgAke@SIP\"\\|\\|sip.Call-ID==\"0050569E78EF-554c-acc81700-becf6-588f3c46-495a\"

It is recommended to use '-d' option together with '-y'. This will give you exact match by diameter session-id in cases when more than one message exist in single frame. 

# Advanced usage

You can edit 'proto_formatter' dict in conf/conf_uml.py and define there any field from protocol that you want. Before adding new header line, please ensure the same line defined in 'headers' dict. Because only headers defined in 'headers' dict are considered.
