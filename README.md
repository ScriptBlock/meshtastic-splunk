There are two distinct Splunk apps in this repository

Splunk TA (add-on) for Meshtastic

This Splunk add-on facilitates data collection from Meshtastic devices over TCP via the python API.

Requirements
  A splunk.com username
  Splunk Enterprise 8.0+: https://www.splunk.com/en_us/download/splunk-enterprise.html
  python3 (must be located at /usr/bin/python3)
  meshtastic python module


Splunk App for Meshtastic

This app contains the dashboards, reports, and other knowledge objects that help interpret the data retrieved by the TA.  If the TA is properly installed and an input is configured, this content does not require any configuration.

Requirements
  Splunk TA for Meshtastic
  Location Tracker Custom visualization: https://splunkbase.splunk.com/app/3164/ (requires splunk.com login)


Installation Instructions

I prepare my installation by placing the splunk TGZ along with the prerequisite SPL files into my installation directory and executing all of these commands from that location.

1. Install & start Splunk
	a. wget -O splunk-8.1.1-08187535c166-Linux-x86_64.tgz 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=8.1.1&product=splunk&filename=splunk-8.1.1-08187535c166-Linux-x86_64.tgz&wget=true'
	b. tar xvf splunk-8.1.1-08187535c166-Linux-x86_64.tgz
	c. ./splunk/bin/splunk start --accept-license (create admin credentials here)
	d. ./splunk/bin/splunk enable boot-start
2. Ensure python3 and pip3 are installed
	a. apt-get install -y python3
	b. apt-get install -y python3-pip
3. Install meshtastic python module
	a. pip3 install meshtastic
4. Install the Splunk TA for Meshtastic
	a. ./splunk/bin/splunk install app TA-meshtastic-data-collection-0.1.0.spl
5. Install the Splunk App for Meshtastic
	a. ./splunk/bin/splunk install app meshtastic-app.spl
6. Restart Splunk
	a. ./splunk/bin/splunk restart


Configure Inputs for your Meshtastic devices

1. Open Splunk Enterprise at http://<serverip>:8000 and log in with the credentials used during installation
2. Open the app listing and select "Meshtastic Data Collection"
3. In the Inputs menu, click the "Create New Input" button
4. You will add 1 input per meshtastic device that you will connect to via TCP
	Name: the name of this input.  This is arbitrary and is just descriptive.
	Interval: the data collection script will try to restart every <interval> seconds.  This is used to ensure that the script starts back up in the event that it crashes, or when the script naturally terminates (see script timeout below).  This should be set to a relatively low number (10-30 seconds), as the script is smart enough to not create multiple copies of the script.  Interval will only apply if the script has already terminated for some reason.
	Index: the TA automatically creates the "meshtastic" index and the app expects data to be in this index.  Select "meshtastic" here.
	Device IP: the IP address of the meshtastic device that this input will read from/listen to
	Script Timeout: the amount of time the script will run before gracefully ending.  While scripts can run forever, it's often useful to let them terminate and restart occasionally.  Especially with alpha/beta code since API may not be entirely reliable.  This setting should be considered in conjunction with the "Interval" setting for understanding the persistence and reliability of this collection mechanism.
	Collect Node Info: If selected, the node info and radio information APIs will be used to collect data from this device.
	Node Info Interval: The number of seconds between API calls to the info and radio endpoints.
	Collect Mesh Info: If selected, the meshdata information API will be used to collect data from this device.
	Mesh Info interval: The number of seconds between API calls to the mesh data endpoints.


Troubleshooting:
	How can I tell if the script is running or not?
	Execute ps -ef | grep meshaio on the splunk server.  If you do not see meshaio.py running, then a prerequisite is missing.


