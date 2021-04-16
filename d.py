import os
import getopt
import time
import sys
from socket import *
import json
import collections
import copy 

suffix = ".clic.cs.columbia.edu"
UNI = 'ls3586'


class Node:
    # Build a UDP socket, store your arguments
    # Initialize your routing table, etc.
    # Port could be none. If it is, use 10000 + os.geteuid()
    # Cities is: ['rome:1', 'paris':7]
    def __init__(self, port, cities):
        self._port = 30000 + os.getuid() # 21498  # 3000+os.getuid() if port is None else port
        self._ft = {}
        self._sender = socket(AF_INET, SOCK_DGRAM)
        self._server = socket(AF_INET, SOCK_DGRAM)
        self._server.bind(('0.0.0.0', self._port))
        self._sender.settimeout(5)
        self._server.settimeout(5)
        self._neighbors = []
        self._updated = {}
        self._needs_to_send = False
        self._name = gethostname()
        self._filename = self._name + "_routing.txt"

        self._ft[self._name] = [0, self._name]
        for city in cities:
            city_info = city.split(":")
            # city : [dist, next node]
            self._neighbors.append(city_info[0])
            self._ft[city_info[0]] = [int(city_info[1]), city_info[0]]
        #print(self._ft)

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
        info = {'reachable': copy.deepcopy(self._ft), 'from-city': str(gethostname())}  # distances I can reach to
        del info['reachable'][self._name]
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
        #print("RECEIVED: ", end='')
        #print(received_info)
        from_city = received_info['from-city']
        reachables = received_info['reachable']
        # updates = []
        for city, vals in reachables.items():
            # distance = vals[0]
            # if city not in self._ft:
            #     updates.append([city, int(distance), from_city, int(self._ft[from_city][0])])
            # # if b to c + my dist to b, i need to update the ft to be bellmanfords
            # # my distance plus b to c distance, and route to b
            # elif int(distance) < self._ft[city][0]:
            #     self._needs_to_send = True
            #     info = [int(distance), from_city]
            #     self._ft[city] = info
            #     self._updated[city] = int(distance)
            self.bellman_ford(city, vals, from_city)

    # Called from inbound. Update Routing Table given what neighbor told you
    # argument: routing is the unpacked JSON file of routing table from neighbor
    def update_routing_table(self, routing):
        pass

    # Called from inbound. After getting routing table updates
    # run Bellman Ford to update Routing Table values
    def bellman_ford(self, city, values, b_city):
        # if received can reach a city I cannot reach,
        # I need to add that city fo my list of forwarding tables, and add the cumulative
        # distance, of whatever city it came from + its distance, + distance other city takes
        my_dist_to_neighbor = self._ft[b_city][0]
        neighbor_to_city_c_dist = int(values[0])

        # if b can reach c, c is not me, and overall dist to c is less than what I have
        # add it to my ft.
        if city in self._ft and city != self._name and \
                neighbor_to_city_c_dist + my_dist_to_neighbor < self._ft[city][0]:
            self._ft[city] = [my_dist_to_neighbor + neighbor_to_city_c_dist, b_city]
            self._needs_to_send = True
        # elif it is not me, it is unknown to me, add to my ft.
        elif city != self._name and city not in self._ft:
            self._ft[city] = [my_dist_to_neighbor + neighbor_to_city_c_dist, b_city]
            self._needs_to_send = True

        # for update in updates:
        #     city = update[0]
        #     from_city = update[2]
        #     from_city_dist_to_city = updates[1]
        #     from_city_dist = updates[3]
        #     self._ft[city] = [from_city_dist + from_city_dist_to_city, from_city]


    def update(self):
        return self._needs_to_send

    def print_ft(self):
        # print(self._ft)
        attributes = []
        for city, vals in self._ft.items():
            attributes.append((city, int(vals[0])))

        sorted(attributes)
        items = list(map(lambda x: str(x[0]) + " " + str(x[1]), attributes))

        with open(self._filename, "a+") as f:
            f.write("|".join(items))
            f.write("\n")


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
    node.send_routing_table()

    while True:
        try:
            # I'll leave this to you to implement
            # Should be obvious which order of functions to call in what order

            # updated = {}
            # receive info
            # parse info
            # for each in received, calculated
            try:
                node.inbound()
            except timeout:
                pass
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

