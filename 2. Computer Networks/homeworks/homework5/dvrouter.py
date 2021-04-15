import os
import getopt
import time
import sys
from socket import *
import json
import collections


suffix = ".clic.cs.columbia.edu"
UNI = 'ls3586'


class Node:
    # Build a UDP socket, store your arguments
    # Initialize your routing table, etc.
    # Port could be none. If it is, use 10000 + os.geteuid()
    # Cities is: ['rome:1', 'paris':7]
    def __init__(self, port, cities):
        self._port = 3000+os.getuid() if port is None else port
        self._ft = {}
        self._filename = "" # TODO - perhaps check what the hostname is?
        self._sender = socket(AF_INET, SOCK_DGRAM)
        self._server = socket(AF_INET, SOCK_DGRAM)
        self._server.bind(('0.0.0.0', self._port))
        self._sender.settimeout(5)
        self._server.settimeout(5)
        self._neighbors = []
        self._updated = {}
        self._needs_to_send = False
        for city in cities:
            city_info = city.split(":")
            # city : [dist, next node]
            self._neighbors.append(city_info[0])
            self._ft[city_info[0]] = [int(city_info[1]), city_info[0]]
        print(self._ft)

    # Dump current list of all nodes this router knows and
    # the weight of shortest path.
    # Please see berlin_routing.txt, paris_routing.txt
    # PLEASE USE <hostname>_routing.txt names.
    # For a sanity check, you can check the last line of your text file
    # with mine. If it matches, great!
    def dump_routing_table(self):
        pass

    # Parse Arguments
    # Initialize list of neighbors and T = 0 of RIP Table
    # Only call this once
    # Cities is: ['rome:1', 'paris':7]
    # def parse_nodes(self, cities):
    #     pass

    # Send all neighbors your current routing table
    def send_routing_table(self):
        info = {'reachable': self._ft, 'from-city': str(gethostname())}  # distances I can reach to
        packet = json.dumps(info).encode()
        for city in self._neighbors:
            addr = city + suffix
            self._sender.sendto(packet, (addr, self._port))
        self._needs_to_send = False
        self._updated = {}

    # Receive data from a neighbor of their routing table
    # Update our rating table as needed
    def inbound(self):
        encoded = self._server.recv(1024)
        received_info = json.loads(encoded.decode())
        from_city = received_info['from-city']
        reachables = received_info['reachable']
        for city, vals in reachables.items():
            distance = vals[0]
            if int(distance) < self._ft[city][0]:
                self._needs_to_send = True
                info = [int(distance), from_city]
                self._ft[city] = info
                self._updated[city] = int(distance)



    # Called from inbound. Update Routing Table given what neighbor told you
    # argument: routing is the unpacked JSON file of routing table from neighbor
    def update_routing_table(self, routing):
        pass

    # Called from inbound. After getting routing table updates
    # run Bellman Ford to update Routing Table values
    def bellman_ford(self):
        pass

    def update(self):
        return self._needs_to_send

    def print_ft(self):
        print(self._ft)

def main():
    # Turns: ["-p" "8000", "berlin:1", "Vienna:1"] to ("-p", "8000"), ["berlin:1", "Vienna:1"]
    # If no -p passed you get
    # ["berlin:1", "Vienna:1"] to (-p, None), ["berlin:1", "Vienna:1"]
    options, cities = getopt.getopt(sys.argv[1:], "p:")
    try:
        port = int(options[1])
    except IndexError:
        port = None
    except ValueError:
        port = None
    node = Node(port, cities)

    # send broadcast

    while True:
        try:
            # I'll leave this to you to implement
            # Should be obvious which order of functions to call in what order

            # updated = {}
            # receive info
            # parse info
            # for each in received, calculated
            node.inbound()
            node.print_ft()
            if node.update():

                node.send_routing_table()
            # print FT
            # if updated is not {} then broadcast updated to each in FT.

            # It should converge super-fast without the timer!
            # But feel free to use sleep()
            # both for troubleshooting, and minimize risk of overloading CLIC
            # Although Please Remove any sleep in final submission!
            time.sleep(30)

        # Use CTRL-C to exit
        # You do NOT need to worry of updating routing table
        # if a node drops!
        # Show final routing table for checking if RIP worked
        except KeyboardInterrupt:
            node.dump_routing_table()
            break


if __name__ == '__main__':
    main()
