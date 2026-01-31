import socket
import sys

def is_port_free(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            return True
    except:
        return False

def find_free_port(start_port):
    """Find the next available port starting from start_port"""
    port = start_port
    while port < start_port + 100:
        if is_port_free(port):
            return port
        port += 1
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    try:
        requested_port = int(sys.argv[1])
        free_port = find_free_port(requested_port)
        if free_port:
            print(free_port)
            sys.exit(0)
        else:
            sys.exit(1)
    except:
        sys.exit(1)
