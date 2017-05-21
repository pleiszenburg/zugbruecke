
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from sys import platform


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
	
    rpc_paths = ('/RPC2',)


# Create server
server = SimpleXMLRPCServer(("localhost", 8000), requestHandler = RequestHandler)

server.register_introspection_functions()

# Register pow() function; this will use the value of
# pow.__name__ as the name, which is just 'pow'.
server.register_function(pow)

# Register a function under a different name
def adder_function(x,y):
	return x + y
server.register_function(adder_function, 'add')

# Register OS check
def get_current_os():
	return str(platform)
server.register_function(get_current_os, 'get_current_os')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'mul').
class MyFuncs:
	def mul(self, x, y):
		return x * y

server.register_instance(MyFuncs())

# Run the server's main loop
server.serve_forever()
