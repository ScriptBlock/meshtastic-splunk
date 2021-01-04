import os
import sys
import time
import datetime
import meshtastic
import queue
import json
from datetime import timedelta
from pubsub import pub

def getDeviceInfo(interface):
    #get normal device info
    info = interface.myInfo
    results = { "ip": sys.argv[1] }
    results["device_info"] = {}
    for field in info.ListFields():
        results["device_info"][field[0].name] = field[1]

    #get device radio information
    info = interface.radioConfig
    
    results["radio_info"] = {}
    results["radio_info"]["preferences"] = {}
    for field in info.preferences.ListFields():
        results["radio_info"]["preferences"][field[0].name] = field[1]
    results["radio_info"]["channel_settings"] = {}
    for field in info.channel_settings.ListFields():
        results["radio_info"]["channel_settings"][field[0].name] = str(field[1])

    return json.dumps(results)
     
def getDeviceMeshNodes(interface):
    result = { "ip": sys.argv[1], "meshnodes": interface.nodes }
    return json.dumps(result)


def onReceive(packet, interface): # called when a packet arrives
    #print("Meshtastic Debug: received message packet")
    packet["decoded"]["data"]["payload"] = str(packet["decoded"]["data"]["payload"])
    data = json.dumps(packet)
    q.put(data)

taName = "TA-meshtastic-data-collection"

lastDeviceInfoCollection = datetime.datetime.now()
lastDeviceMeshCollection = datetime.datetime.now()
scriptStartTime = datetime.datetime.now()

sh = os.environ.get('SPLUNK_HOME')

global q 
q = queue.Queue()


opt_device_ip = sys.argv[1]
opt_collect_device_info = sys.argv[2].lower() == 'true'
opt_device_info_interval_s_ = int(sys.argv[3])
opt_collect_mesh_nodes = sys.argv[4].lower() == 'true'
opt_mesh_info_interval_s_ = int(sys.argv[5])
abort_timeout = int(sys.argv[6])


print("Meshtastic Debug: Starting data collection for " + opt_device_ip)
print("Meshtastic Debug: Collect Device Info: " + str(opt_collect_device_info))
print("Meshtastic Debug: Device Info Interval: " + str(opt_device_info_interval_s_))
print("Meshtastic Debug: Collect Mesh Info: " + str(opt_collect_mesh_nodes))
print("Meshtastic Debug: Mesh Info Interval: " + str(opt_mesh_info_interval_s_))
print("Meshtastic Debug: Abort Timeout: " + str(abort_timeout))

pub.subscribe(onReceive, "meshtastic.receive")
interface = meshtastic.TCPInterface(opt_device_ip)

running = True

while running:
    loopTime = datetime.datetime.now()
    
    while not q.empty():
        data = q.get()
        f = open(sh + "/etc/apps/" + taName + "/bin/data/messages-" + sys.argv[1] + ".log", "a")
        f.write(data + "\r\n")
        f.close()

    if opt_collect_device_info:
        if (loopTime-lastDeviceInfoCollection).seconds > opt_device_info_interval_s_:
            data = getDeviceInfo(interface)
            f = open(sh + "/etc/apps/" + taName + "/bin/data/deviceinfo-" + sys.argv[1] + ".log", "a")
            f.write(data + "\r\n")
            f.close()
            lastDeviceInfoCollection = loopTime
            
    if opt_collect_mesh_nodes:
        if (loopTime-lastDeviceMeshCollection).seconds > opt_mesh_info_interval_s_:
            data = getDeviceMeshNodes(interface)
            f = open(sh + "/etc/apps/" + taName + "/bin/data/meshinfo-" + sys.argv[1] + ".log", "a")
            f.write(data + "\r\n")
            f.close()
            lastDeviceMeshCollection = loopTime
    
    if (loopTime-scriptStartTime).seconds > abort_timeout:
        interface.sendData(b'closing api hack')
        print("Meshtastic Debug: aborting script due to time limit.  closing")
        running = False

interface.close()
