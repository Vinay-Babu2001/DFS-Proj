This project Writen on Python 3.6
To run this project, do the following:

* Run the client application: **python client.py**
* Run the directory service: **python directory_service.py**
* Run the locking service: **python locking_service.py**
* Run fileserver A in a separate directory - fileserver A is holds the primary copy for replication and can be written to: **python fileserverA.py**
* Run fileserver B in a separate directory - fileserver B only takes read requests: **python fileserverB.py**
* Run fileserver C in a separate directory - fileserver C (like fileserver B) only takes read requests: **python fileserverC.py**

On the client server we have to run these following commands:

	<write> filename 
	.... content
	<end>

<read> filename
<quit>