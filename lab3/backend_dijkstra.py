#!/usr/bin/env python3
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}

DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)

    Builds a dictionary where keys are node ids, and values are sets of tuples of
    (node, distance, time) where node is a viable node to visit next.
    """
    legal_ways = get_legal(ways_filename, 'ways')
    legal_nodes = get_legal(ways_filename, 'nodes')
    node_locations = build_node_loc_dict(ways_filename, nodes_filename)

    connections_by_node = {node: set() for node in legal_nodes}

    for way in read_osm_data(ways_filename):
        if way['id'] in legal_ways:
            if 'oneway' in way['tags']:
                if 'yes' in way['tags']['oneway']:
                    for i in range(len(way['nodes'])):
                        if 0 < i + 1 < len(way['nodes']):
                            dist = great_circle_distance(node_locations[way['nodes'][i]],
                                                         node_locations[way['nodes'][i + 1]])
                            if 'maxspeed_mph' in way['tags']:
                                speed = dist / way['tags']['maxspeed_mph']
                            else:
                                speed = dist/DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                            connections_by_node[way['nodes'][i]].add((way['nodes'][i + 1],# only node after, bc oneway
                                                                      dist,
                                                                      speed))

                else:
                    for i in range(len(way['nodes'])):
                        if 0 <= i + 1 < len(way['nodes']):  # if i in list range
                            dist = great_circle_distance(node_locations[way['nodes'][i]],
                                                         node_locations[way['nodes'][i + 1]])
                            if 'maxspeed_mph' in way['tags']:
                                speed = dist / way['tags']['maxspeed_mph']
                            else:
                                speed = dist/DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                            connections_by_node[way['nodes'][i]].add((way['nodes'][i + 1],  # node after on road
                                                                      dist,
                                                                      speed))

                        if 0 <= i - 1 < len(way['nodes']):  # if i in list range
                            dist = great_circle_distance(node_locations[way['nodes'][i]],
                                                         node_locations[way['nodes'][i - 1]])
                            if 'maxspeed_mph' in way['tags']:
                                speed = dist / way['tags']['maxspeed_mph']
                            else:
                                speed = dist/DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                            connections_by_node[way['nodes'][i]].add((way['nodes'][i - 1],  # node before on road
                                                                      dist,
                                                                      speed))
            else:
                for i in range(len(way['nodes'])):
                    if 0 <= i + 1 < len(way['nodes']):  # if i in list range
                        dist = great_circle_distance(node_locations[way['nodes'][i]],
                                                     node_locations[way['nodes'][i + 1]])
                        if 'maxspeed_mph' in way['tags']:
                            speed = dist / way['tags']['maxspeed_mph']
                        else:
                            speed = dist / DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                        connections_by_node[way['nodes'][i]].add((way['nodes'][i + 1],  # node after on road
                                                                  dist,
                                                                  speed))

                    if 0 <= i - 1 < len(way['nodes']):  # if i in list range
                        dist = great_circle_distance(node_locations[way['nodes'][i]],
                                                     node_locations[way['nodes'][i - 1]])
                        if 'maxspeed_mph' in way['tags']:
                            speed = dist / way['tags']['maxspeed_mph']
                        else:
                            speed = dist / DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]
                        connections_by_node[way['nodes'][i]].add((way['nodes'][i - 1],  # node before on road
                                                                  dist,
                                                                  speed))

    return connections_by_node, node_locations


def find_short_path(aux_structures, loc1, loc2, heuristic = False):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    connections_by_node, node_locations = aux_structures #pull dictionaries from aux structures function

    node_1 = find_nearest_node(node_locations, loc1)  # find start node
    node_2 = find_nearest_node(node_locations, loc2)  # find end node

    if node_1 == node_2:
        return []  # If start = end return empty list

    agenda = set()  # set of all nodes

    distanceTo = {node_1: 0}  # cost from start to each node

    agenda.add((node_1, 0)) #add start node with cost of 0

    predecessor = {node: None for node in connections_by_node.keys()} #dict of predecessors for when we rebuild

    ready_to_return = False# indicator that tells us if we are ready to return after valid node found

    valid_path_length = None # Lets us check if we find a valid path shorter than the one we've already found

    if heuristic: #if we use the heuristic we can check min using another function
        heuristic = lambda x: great_circle_distance(node_locations[x[0]], (42.5465, -71.1787)) + x[1]
    else:
        heuristic = lambda node: node[1]

    i = 0

    while agenda:  #as long as nodes are in our agenda
        i += 1
        current_node = min(agenda, key=heuristic)#take min according to heuristic
        if current_node[1] == float('inf'):#if the best we can do is an infinite distance we must break. No valid paths
            break

        if ready_to_return and current_node[1] >= valid_path_length:#if ready to return and we start taking nodes
            break#worse than the one we already have we can break

        for next_node in connections_by_node[current_node[0]]:#check all next nodes from current
            possible_path = current_node[1] + next_node[1]  # distance from start to current, + to next

            if next_node[0] not in distanceTo:  #if the node isn't in distance to, assign it infinity and move along
                distanceTo[next_node[0]] = float('inf')
            distance_to_next = distanceTo[next_node[0]] #allows us to use value in distance to without checking 10x

            if possible_path < distance_to_next:  # if this path the shortest yet, put it in distanceTo
                agenda.add((next_node[0], possible_path))  # add to agenda node id, and possible pathlength
                distanceTo[next_node[0]] = possible_path
                distance_to_next = possible_path
                predecessor[next_node[0]] = current_node  # make the predecessor in the best path the current node

            if next_node[0] == node_2: # checks if we've found an end node
                valid_path_length = distance_to_next
                ready_to_return = True

        agenda.remove(current_node)

    shortest_path = []
    current_node = (node_2, 0)

    while predecessor[current_node[0]] is not None: # classic unpack of predecessor dict to find the best path
        shortest_path.insert(0, node_locations[current_node[0]])
        current_node = predecessor[current_node[0]]  # move back in chain

    if shortest_path:
        shortest_path.insert(0, node_locations[node_1])
    else:
        return None

    return shortest_path

def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    connections_by_node, node_locations = aux_structures  # pull dictionaries from aux structures function

    node_1 = find_nearest_node(node_locations, loc1)  # find start node
    node_2 = find_nearest_node(node_locations, loc2)  # find end node

    if node_1 == node_2:
        return []  # If start = end return empty list

    agenda = set()  # set of all nodes

    distanceTo = {node_1: 0}  # cost from start to each node

    agenda.add((node_1, 0, 0))  # add start node with cost of 0

    predecessor = {node: None for node in connections_by_node.keys()}  # dict of predecessors for when we rebuild

    ready_to_return = False  # indicator that tells us if we are ready to return after valid node found

    valid_path_length = None  # Lets us check if we find a valid path shorter than the one we've already found

    i = 0

    while agenda:  # as long as nodes are in our agenda
        i += 1
        current_node = min(agenda, key=lambda node: node[2])  # take min according to heuristic
        if current_node[2] == float(
                'inf'):  # if the best we can do is an infinite distance we must break. No valid paths
            break

        if ready_to_return and current_node[2] >= valid_path_length:  # if ready to return and we start taking nodes
            break  # worse than the one we already have we can break

        for next_node in connections_by_node[current_node[0]]:  # check all next nodes from current
            possible_path = current_node[2] + next_node[2]  # distance from start to current, + to next

            if next_node[0] not in distanceTo:  # if the node isn't in distance to, assign it infinity and move along
                distanceTo[next_node[0]] = float('inf')
            distance_to_next = distanceTo[next_node[0]]  # allows us to use value in distance to without checking 10x

            if possible_path < distance_to_next:  # if this path the shortest yet, put it in distanceTo
                agenda.add((next_node[0],0, possible_path))  # add to agenda node id, and possible pathlength
                distanceTo[next_node[0]] = possible_path
                distance_to_next = possible_path
                predecessor[next_node[0]] = current_node  # make the predecessor in the best path the current node

            if next_node[0] == node_2:  # checks if we've found an end node
                valid_path_length = distance_to_next
                ready_to_return = True

        agenda.remove(current_node)

    shortest_path = []
    current_node = (node_2, 0)

    while predecessor[current_node[0]] is not None:  # classic unpack of predecessor dict to find the best path
        shortest_path.insert(0, node_locations[current_node[0]])
        current_node = predecessor[current_node[0]]  # move back in chain

    if shortest_path:
        shortest_path.insert(0, node_locations[node_1])
    else:
        return None

    return shortest_path



def distance_between_ids(filename, id1, id2):
    '''
    :param filename: String name of file
    :param id1: Start node id
    :param id2: End node id
    :return: distance between those two nodes
    '''
    for node in read_osm_data(filename):
        if node['id'] == id1:
            loc1 = (node['lat'], node['lon'])
        if node['id'] == id2:
            loc2 = (node['lat'], node['lon'])

    return great_circle_distance(loc1, loc2)


def build_node_loc_dict(ways_filename, nodes_filename):
    '''
    :param nodes_filename: String filename of nodes
    :return: Dict of node ids: (node lat, node long)
    '''
    locations_by_node = {}

    legal_nodes = get_legal(ways_filename, 'nodes')

    for node in read_osm_data(nodes_filename):
        if node['id'] in legal_nodes:
            locations_by_node[node['id']] = (node['lat'], node['lon'])

    return locations_by_node


def get_legal(ways_filename, type):
    '''
    :param ways_filename: String filename of ways
    :param type: either 'ways' to get legal ways, or 'nodes' to get legal nodes.
    :return: A set of ids of either legal ways or nodes, depending on user specification.
    '''
    legal = set()

    if type == 'ways':
        for way in read_osm_data(ways_filename):
            if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                legal.add(way['id'])

        return legal

    if type == 'nodes':
        legal_way_ids = get_legal(ways_filename, 'ways')

        for way in read_osm_data(ways_filename):
            if way['id'] in legal_way_ids:
                legal.update(way['nodes'])

        return legal


def find_nearest_node(node_locs, start_loc):
    '''
    :param node_locs: String filename of node locs
    :param start_loc: tuple starting location
    :return: Nearest node id
    '''
    distances = {}

    for node in node_locs:
        current_loc = node_locs[node]
        distances[node] = great_circle_distance(start_loc, current_loc)

    min_distance = float('inf')
    min_distance_id = ''

    for node in distances:
        if distances[node] < min_distance:
            min_distance = distances[node]
            min_distance_id = node

    return min_distance_id


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    a = 'CUNNINGHAM'

    # for way in read_osm_data('resources/mit.ways'):
    #     print(way)

    structures = (build_auxiliary_structures('resources/mit.nodes', 'resources/mit.ways'))
    print(structures)

    #(find_short_path(structures, (42.3858, -71.0783), (42.5465, -71.1787), True))
    #(find_short_path(structures, (42.3858, -71.0783), (42.5465, -71.1787)))

    #with Heuristic: 48435 agenda checks
    #without Heuristic: 377582 agenda checks

    print(a)
