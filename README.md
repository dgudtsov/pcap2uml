# pcap2uml
IMS Call flow visualizer for HTTP, SIP, Diameter, GSM MAP and CAMEL protocols  

This program can parse inpur pcap and generate result in plantuml format.

Project page: https://github.com/dgudtsov/pcap2uml  

Uses pyshark library: http://kiminewt.github.io/pyshark/  
and plantuml sequence diagram: http://plantuml.com/

# Prerequisite
Python 2 version >= 2.6  
Python 3 is not supported  

pyshark library https://github.com/KimiNewt/pyshark  

To install it:  
pip install pyshark  

Plantuml: http://plantuml.com/download

# Configure

edit conf/conf_uml.py file:  
1. define 'participants' dict  
2. define 'uml_intro'  
3. define plantuml library and java path in JAVA_BIN and plantuml_jar params 


# Usage

run:  
./pcap2uml.py -i input.pcap -o out.uml -y filter -t format

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

## Usage notice

If you didn't define all parties in 'participants' dict in conf/conf_uml.py file, then program will dump list of undefined participants for you. You can copy that list and paste it into configuration file and then fill it values with appropriate names.

# Advanced usage

You can edit 'proto_formatter' dict in conf/conf_uml.py and define there any field from protocol that you want. Before adding new header line, please ensure the same line defined in 'headers' dict. Because only headers defined in 'headers' dict are considered.
