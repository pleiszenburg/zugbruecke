import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://localhost:8000')
print(s.pow(2,3))  # Returns 2**3 = 8
print(s.add(2,3))  # Returns 5
print(s.mul(5,2))  # Returns 5*2 = 10
print(s.get_current_os())  # Returns server OS information

# Print list of available methods
print(s.system.listMethods()) 
