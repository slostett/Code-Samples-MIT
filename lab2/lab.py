#!/usr/bin/env python3

import pickle


# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for lab 2 will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).

def search_database_by_id(id_list):
    '''
    given a list of ids returns names
    '''
    with open('resources/names.pickle', 'rb') as f:
        namesdb = pickle.load(f)

    names_flipped = dict(zip(namesdb.values(), namesdb.keys()))

    return [names_flipped[id_list[i]] for i in range(len(id_list))]


def acted_together(data, actor_id_1, actor_id_2):
    '''
    Take in data in form of filename, and actors by id.
    Returns True if they acted together, False otherwise
    '''

    for tup in data:
        if actor_id_1 in tup and actor_id_2 in tup:
            return True

    return False


def build_actor_set(data):
    '''
    :param data: List of tuples of actors and their movies
    :return: set of all actors
    '''
    actor_set = set()

    for tup in data:
        for actor in tup[:2]:
            actor_set.add(actor)

    return actor_set


def generate_costar_dict(data):
    '''
    :param data: List of tuples of actors and their movies
    :return: dict. keys are actors, values are sets of all they acted with
    '''
    costar_dict = {}

    list_1 = list(list(zip(*data))[0])  # list of actor 1
    list_2 = list(list(zip(*data))[1])  # list of actor 2

    for i in range(len(list_1)):
        if list_1[i] not in costar_dict:
            costar_dict[list_1[i]] = {list_2[i]}
        elif not list_1 == list_2[i]:
            costar_dict[list_1[i]].add(list_2[i])
        if list_2[i] not in costar_dict:
            costar_dict[list_2[i]] = {list_1[i]}
        elif not list_1 == list_2[i]:
            costar_dict[list_2[i]].add(list_1[i])

    return costar_dict


def actors_with_bacon_number(data, n):
    '''
    Given a list of tuples which represent actors acting together in a movie,
    return a set of all the actors with a given bacon number n
    '''
    if n == 0:
        return {4724}

    bacon_number_dict = {0: {4724}}

    i = 0

    already_added = {4724}  # list of numbers we have already added

    costar_dict = generate_costar_dict(data)

    while bacon_number_dict[i]:  # iterate as long as we can still find bacon neighbors

        with_bacon_number = set()  # initialize list of actors with given bacon number

        for actor in bacon_number_dict[i]:
            costars = costar_dict[actor]  # get costars of actor of interest
            costars -= already_added  # take away costars we already looked at
            with_bacon_number |= costars  # add costars remaining to those with given bacon number
            already_added |= costars  # add costars to ones we have already seen

        i += 1

        bacon_number_dict[i] = with_bacon_number  # assign those with bacon # to a spot in the bacon dict.

        if i == n:  # if we have already found the actors for the number we want we can exit early.
            return bacon_number_dict[i]

    return set()  # if we stop finding neighbors we can return the empty set


def bacon_path(data, actor_id, start=4724):
    '''
    Find the shortest bacon path.
    :param data: data as a list of tuples
    :param actor_id: an integer actor id
    :return: list of shortest path between two actors
    '''
    to_check = [start]

    i = 0

    already_added = {start}  # list of numbers we have already added

    costar_dict = generate_costar_dict(data)

    predecessor = {start: None}

    path = []

    while to_check:  # iterate as long as we can still find bacon neighbors

        if i > len(data) + 1:  # this is an upper bound. There can't be a higher bn than the # of connections.
            return None

        check_next = set()  # initialize list of actors with given bacon number

        for actor in to_check:

            for costar in costar_dict[actor]:  # each time we get costars, set their predecessor to the current actor

                if costar not in already_added:
                    already_added.add(costar)
                    check_next.add(costar)
                    predecessor[costar] = actor

                    if costar == actor_id:  # if costar is the one we're looking for, we can get ready to return path.
                        while predecessor[actor_id] is not None:  # As long as we can pull predecessors that aren't None
                            actor_id = predecessor[actor_id]
                            path = [actor_id] + path

                        path.append(costar)  # add the one we terminated on

                        return path

        i += 1
        to_check = check_next


def actor_to_actor_path(data, actor_id_1, actor_id_2):
    '''
    Find path between two actors.
    :param data: Data in same form as usual
    :param actor_id_1: actor 1 by integer id
    :param actor_id_2: actor 2 by integer id
    :return:path between actors
    '''
    return bacon_path(data, actor_id_2, actor_id_1)


def films_connecting_actors(data, actor1, actor2):
    '''
    :param data: Data as list of tuples
    :param actor1: Integer start actor id
    :param actor2: integer end actor id
    :return: list of films that connect actors.
    '''
    path = bacon_path(data, actor1, actor2)  # generate our path

    film_path = []

    for i in range(len(path) - 1):  # for each two films, check the data and add the film we need.
        index_1 = path[i]
        index_2 = path[i + 1]
        for tup in data:
            if (tup[0] == index_1 and tup[1] == index_2) or (tup[1] == index_1 and tup[0] == index_2):
                film_path.append(tup[2])

    film_path.reverse()

    return film_path


def actor_path(data, actor_id_1, goal_test_function):
    '''
    :param data: Data as list of tuples
    :param actor_id_1: Integer actor ID to start
    :param goal_test_function: Function to know when we've reached the end
    :return: Shortest path between actor and endpoint determined by goal test function
    '''

    if goal_test_function(actor_id_1):
        return [actor_id_1]

    to_check = [actor_id_1]

    i = 0

    already_added = {actor_id_1}  # list of numbers we have already added

    costar_dict = generate_costar_dict(data)

    predecessor = {actor_id_1: None}

    path = []

    while to_check:  # iterate as long as we can still find bacon neighbors

        if i > len(data) + 1:  # this is an upper bound. There can't be a higher bn than the # of connections.
            return None

        check_next = set()  # initialize list of actors with given bacon number

        for actor in to_check:

            for costar in costar_dict[actor]:  # each time we get costars, set their predecessor to the current actor

                if costar not in already_added:
                    already_added.add(costar)
                    check_next.add(costar)
                    predecessor[costar] = actor

                    if goal_test_function(costar):  # if costar is good, we can get ready to return the path.
                        costar_2 = costar #we have to duplicate since there aren't separate start/end
                        while predecessor[costar_2] is not None:  # As long exist predecessors that aren't None
                            costar_2 = predecessor[costar_2]
                            path = [costar_2] + path

                        path.append(costar)  # add the one we terminated on

                        return path

        i += 1
        to_check = check_next


def generate_film_dict(data):
    '''
    :param data: Data in usual format
    :return: Dict where keys are film ids, values sets of actors in each film
    '''
    film_dict = {}

    list_1 = list(list(zip(*data))[0])  # list of actor 1
    list_2 = list(list(zip(*data))[1])  # list of actor 2
    film_list = list(list(zip(*data))[2])  # list of films

    for tup in data:
        if tup[2] not in film_dict:
            film_dict[tup[2]] = {tup[0], tup[1]}
        else:
            film_dict[tup[2]].add(tup[0])
            film_dict[tup[2]].add(tup[1])

    return film_dict


def actors_connecting_films(data, film1, film2):
    '''
    given data in usual format and 2 film ids, return shortest actor path between 2 films
    '''
    film_dict = generate_film_dict(data)

    pathlist = []

    for actor in film_dict[film1]:
        path = actor_path(data, actor, lambda x: x in film_dict[film2])
        pathlist.append(path)

    return min(pathlist, key=lambda x: len(x))


if __name__ == '__main__':
    with open('resources/large.pickle', 'rb') as f:
        smalldb = pickle.load(f)


    def is_169337(n):
        if n == 169337:
            return True
        return False

    #print(smalldb['Katherine LaNasa'], smalldb['Anton Radacic'])
    # print(smalldb)

    print(actor_path(smalldb, 1345461, is_169337))

    # print(search_database_by_id([1338712, 105288, 64722, 6465, 879]))

    # costar_dict = generate_costar_dict(smalldb)

    # search_id = int(input("Provide id "))
    # print([name for name, age in smalldb.items() if age == search_id])
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
