#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Circular road creation utility
#
# Generate all necessary network SUMO files for simulating circular traffic.
# Vehicle definition must be done by hand. SUMO must be correctly installed and
# present in your system PATH (see SUMO wiki for details on installation).
#
# Copyright (C) 2017-2018 Luca Terruzzi <luca.terruzzi@studenti.unitn.it>
# Copyright (C) 2017-2018 Riccardo Colombo <riccardo.colombo@studenti.unitn.it>
# Successive modifications by Michele Segata <segata@ccs-labs.org>
#

import argparse
import math
import subprocess
import sys

# Parser for retrieving command arguments
parser = argparse.ArgumentParser(description="Create a circular road to be "
                                             "used in SUMO.")
parser.add_argument('-r', '--radius', type=float, default=100,
                    help='Radius of the circle in metres (min 10). Default'
                    '100m.')
parser.add_argument('-n', '--name', help='Name of the output files.',
                    default="circle")
parser.add_argument('-e', '--edges', help='Number of edges. Default 10.',
                    type=int, default=10)
parser.add_argument('-l', '--lanes', help='Number of lanes. Default 1.',
                    type=int, default=1)
parser.add_argument('-s', '--speed', type=float, default=13.9,
                    help='Maximum speed allowed in m/s. Default 13.9 m/s.')
parser.add_argument('-d', '--dimension', type=float,
                    help='Total length of the ring. If present overrides '
                         'radius.')
args = parser.parse_args()

# Arguments validity check
if args.dimension is not None:
    if args.dimension <= 0:
        print ("Ring dimension must be positive")
        print ("Exiting on error")
        exit(1)
    args.radius = (args.dimension / args.edges) / (2 * math.sin(math.pi /
                                                                args.edges))

if args.radius < 10 and args.dimension is not None:
    print ("Radius is too small")
    print ("Exiting on error")
    exit(1)

if args.edges < 3:
    print ("Too few edges to construct a circle")
    print ("Exiting on error")
    exit(1)

if args.lanes < 1:
    print ("There must be at least one lane")
    print ("Exiting on error")
    exit(1)

if args.speed < 0:
    print ("Speed must be positive")
    print ("Exiting on error")
    exit(1)

side = 2 * args.radius * math.sin(math.pi / args.edges)
if side < 1:
    print ("Edge length is too small!. Choose a bigger radius/dimension or "
           "reduce the number of edges.")
    print ("Exiting on error")
    exit(1)

# Calculate the position of the first node between the first two vertexes
first_node = (0, args.radius)
# Calculate the secod node at 0.1 from first node
# second_node = (args.mov, first_node[1])
second_node = (0, -args.radius)

c1 = [first_node]
c2 = [second_node]
for i in range(1, args.edges/2):
    angle = float(i) / (args.edges/2) * math.pi + math.pi/2
    c1.append((-math.cos(angle)*args.radius, math.sin(angle)*args.radius))
    angle = float(args.edges/2-i) / (args.edges/2) * math.pi + math.pi/2
    c2.append((math.cos(angle)*args.radius, math.sin(angle)*args.radius))

c1.append(second_node)
c2.append(first_node)

node1 = (0.5 * (c1[0][0] + c1[1][0]), 0.5 * (c1[0][1] + c1[1][1]))
node2 = (0.5 * (c2[0][0] + c2[1][0]), 0.5 * (c2[0][1] + c2[1][1]))

shape1 = [node1]
shape1.extend(c1[1:])
shape1.append(node2)

shape2 = [node2]
shape2.extend(c2[1:])
shape2.append(node1)

coord1 = ' '.join(["%.2f,%.2f" % x for x in shape1])
coord2 = ' '.join(["%.2f,%.2f" % x for x in shape2])

print ("Creating node file..."),
gen_string = "<!-- Generated with %s -->\n" % (' '.join(sys.argv))
# Write the two nodes in the node file
with open(args.name + ".nod.xml", "w") as node_file:
    node_file.write(gen_string)
    node_file.write("<nodes>\n")
    node_file.write("    <node id=\"node1\" x=\"%.2f\" y=\"%.2f\"/>\n" %
                    node1)
    node_file.write("    <node id=\"node2\" x=\"%.2f\" y=\"%.2f\"/>\n" %
                    node2)
    node_file.write("</nodes>\n")

print ("OK")
print ("Creating edge file..."),
# Write the two edges in the edge file
with open(args.name + ".edg.xml", "w") as edge_file:
    edge_file.write(gen_string)
    edge_file.write("<edges>\n")
    edge_file.write("    <edge id=\"edg1\" from=\"node1\" to=\"node2\" "
                    "numLanes=\"%d\" speed=\"%f\" length=\"%f\" "
                    "shape=\"%s\"/>\n" %
                    (args.lanes, args.speed, side * args.edges / 2, coord1))
    edge_file.write("    <edge id=\"edg2\" from=\"node2\" to=\"node1\" "
                    "numLanes=\"%d\" speed=\"%f\" length=\"%f\" "
                    "shape=\"%s\"/>\n" %
                    (args.lanes, args.speed, side * args.edges / 2, coord2))
    edge_file.write("</edges>\n")

print ("OK")
print ("Building net file..."),

# Launch SUMO command netconvert to create the network from nod end edg files
status = 0
try:
    status = subprocess.call(["netconvert", "-e", args.name + ".edg.xml",
                              "-n", args.name + ".nod.xml", "-o", args.name +
                              ".net.xml"])
except OSError as e:
    print ("Error in launching SUMO netconvert, is SUMO bin folder present in"
           "your system PATH?")
    print ("Exiting on error")

# Check for return status of SUMO netconvert
if status != 0:
    print ("Error in network creation")
    print ("Exiting on error")
    exit(2)

print ("OK")
print ("Creating additional file..."),
# Write the necessary routes and rerouters in thet additional file
with open(args.name + ".add.xml", "w") as additional_file:
    additional_file.write(gen_string)
    additional_file.write("<additionals>\n")
    additional_file.write("    <route id=\"r1\" edges=\"edg2 edg1\"/>\n")
    additional_file.write("    <route id=\"r2\" edges=\"edg1 edg2\"/>\n")
    additional_file.write("    <rerouter id=\"rerouter1\" edges=\"edg1\">\n")
    additional_file.write("        <interval end=\"1e9\">\n")
    additional_file.write("            <routeProbReroute id=\"r2\"/>\n")
    additional_file.write("        </interval>\n")
    additional_file.write("    </rerouter>\n")
    additional_file.write("    <rerouter id=\"rerouter2\" edges=\"edg2\">\n")
    additional_file.write("        <interval end=\"1e9\">\n")
    additional_file.write("            <routeProbReroute id=\"r1\"/>\n")
    additional_file.write("        </interval>\n")
    additional_file.write("    </rerouter>\n")
    additional_file.write("</additionals>\n")

print ("OK")

print("Network length -> " + format(side * args.edges, '.2f'))
print ("Success.")