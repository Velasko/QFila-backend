import os

json = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

system_authentication = {
	"security_header" : os.getenv("SECURITY_HEADER1")
}