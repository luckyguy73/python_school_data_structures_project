from datetime import datetime, time


class Package:
    # package object to load on trucks
    def __init__(self, package_id, delivery_address, delivery_city, delivery_zipcode, delivery_deadline, weight,
                 special_note):
        self.package_id = package_id
        self.delivery_address = delivery_address
        self.delivery_city = delivery_city
        self.delivery_zipcode = delivery_zipcode
        self.delivery_deadline = delivery_deadline
        self.weight = weight
        self.special_note = special_note
        self.delivery_status = 'Package arrived at WGUPS Facility'

    def __str__(self):
        return '*** Package ID# %02d ***\nDelivery Status: %s\nDelivery Address: %s' % \
               (self.package_id, self.delivery_status, self.delivery_address)


class Truck:
    # truck object to deliver packages
    def __init__(self, truck_number):
        self.truck_number = truck_number
        self.truck_time = time(hour=8)
        self.backup_time = time(hour=8)
        self.status = 'AT_HUB'
        self.last_stop = ''
        self.destination = ''
        self.mileage = 0
        self.packages = []
        self.delivered = []


class AddressNode:
    # address object is location to deliver packages and hold distance and predecessor
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.distance = float('inf')
        self.pred_node = None
        self.packages = []

    def __str__(self):
        return '\n\t%s\n\t%s' % (self.name, self.address)


class Graph:
    # graph of address nodes containing adjacent list and edge weights
    def __init__(self):
        self.adj_list = {}
        self.edge_weights = {}

    def add_address_node(self, new_address_node):
        self.adj_list[new_address_node] = []

    def add_dir_edge(self, from_address_node, to_address_node, weight=1.0):
        self.edge_weights[(from_address_node, to_address_node)] = weight
        self.adj_list[from_address_node].append(to_address_node)

    def add_undir_edge(self, address_node_a, address_node_b, weight=1.0):
        self.add_dir_edge(address_node_a, address_node_b, weight)
        self.add_dir_edge(address_node_b, address_node_a, weight)


class Hashtable:
    # data structure created to contain packages with ability to insert, remove, and search using direct access hash
    def __init__(self, initial_capacity=41):
        self.table = [None] * initial_capacity

    def insert(self, item):
        self.table[item.package_id] = item

    def remove(self, item):
        self.table[item.package_id] = None

    def search(self, item):
        return self.table[item]

    def __iter__(self):
        return iter(self.table)


def get_shortest_path(g, starting_point):
    # Modified algorithm based on Dijkstra's shortest path to traverse each node checking each distance to obtain
    # shortest path
    queue = []
    for current_vertex in g.adj_list:
        queue.append(current_vertex)
        current_vertex.distance = float('inf')
        current_vertex.pred_node = None
    if type(starting_point) is Package:
        starting_point.delivery_address.distance = 0
    else:
        starting_point.distance = 0
    while len(queue) > 0:
        least_index = 0
        for i in range(1, len(queue)):
            if queue[i].distance < queue[least_index].distance:
                least_index = i
        current_vertex = queue.pop(least_index)
        for adj_vertex in g.adj_list[current_vertex]:
            edge_weight = g.edge_weights[(current_vertex, adj_vertex)]
            alternative_path_distance = current_vertex.distance + edge_weight
            if alternative_path_distance < adj_vertex.distance:
                adj_vertex.distance = alternative_path_distance
                adj_vertex.pred_node = current_vertex


def list_sort_distance(q):
    # after arriving at each location and running shortest path sort packages by smallest distance
    q.sort(key=lambda x: x.delivery_address.distance)


class Simulation:
    # contains all the attributes and methods to preload the packages and distances from the csv files
    def __init__(self):
        self.sim_time = time(hour=8)
        self.packages = Hashtable()
        self.graph = Graph()
        self.total_mileage = 0
        self.trucks = {}
        for i in range(3):
            self.trucks['truck' + str(i + 1)] = Truck(i + 1)
        self.package_groups = [[], []]
        self.import_packages()
        self.import_distances()
        self.hub = next((a for a in self.graph.adj_list if a.name == 'Western Governors University'), None)
        self.handle_special_notes()
        self.load_packages_with_same_address()
        self.load_deadlines()
        self.load_packages_with_same_address()
        self.load_final_packages()

    def handle_special_notes(self):
        # check each package for a special note and load to corresponding group
        for package in self.packages:
            if package is None or package.special_note == '':
                continue
            if package.special_note[0].lower() == 'm':
                self.trucks['truck1'].packages.append(package)
                package.delivery_status = 'Out for delivery on Truck 1'
            if package.special_note[0].lower() == 'c':
                self.trucks['truck2'].packages.append(package)
                package.delivery_status = 'Out for delivery on Truck 2'
            if package.special_note[0].lower() == 'd':
                self.package_groups[0].append(package)
                package.delivery_status = 'Package Group 3 - Awaiting next available truck'
            if package.special_note[0].lower() == 'w':
                package.delivery_address = next((a for a in self.graph.adj_list if a.address == '410 S State St'), None)
                self.package_groups[1].append(package)
                package.delivery_status = 'Package Group 4 - Awaiting next available truck'

    def load_packages_with_same_address(self):
        # now for each package already in a group see if other packages are going to same location
        for package in self.packages:
            if package is None:
                continue
            if 'WGUPS' in package.delivery_status:
                for truck in self.trucks:
                    if truck == 'truck3':
                        self.trucks[truck].status = 'Scheduled Maintenance on %s' % datetime.today().strftime('%m/%d/%Y')
                        continue
                    for p in self.trucks[truck].packages:
                        if package.delivery_address == p.delivery_address:
                            self.trucks[truck].packages.append(package)
                            package.delivery_status = p.delivery_status
                            break
                for p in self.package_groups[0]:
                    if package.delivery_address == p.delivery_address:
                        self.package_groups[0].append(package)
                        package.delivery_status = p.delivery_status
                        break

    def load_deadlines(self):
        # load packages with deadlines as a priority
        for package in self.packages:
            if package is None:
                continue
            if 'WGUPS' in package.delivery_status:
                if package.delivery_deadline != 'EOD':
                    self.trucks['truck1'].packages.append(package)
                    package.delivery_status = 'Out for delivery on Truck 1'

    def load_final_packages(self):
        # load remaining packages that don't have special notes or deadlines
        for package in self.packages:
            if package is None:
                continue
            if 'WGUPS' in package.delivery_status:
                if int(package.delivery_zipcode[-2:]) > 16:
                    self.package_groups[0].append(package)
                    package.delivery_status = 'Package Group 3 - Awaiting next available truck'
                else:
                    self.package_groups[1].append(package)
                    package.delivery_status = 'Package Group 4 - Awaiting next available truck'
        for k, v in self.trucks.items():
            get_shortest_path(self.graph, self.hub)
            list_sort_distance(v.packages)
            v.last_stop = self.hub

    def import_packages(self):
        # import packages from csv file
        with open('packages.csv') as pf:
            # skip header
            next(pf)
            for line in pf:
                package = [p.strip() for p in line.split(',')]
                self.packages.insert(
                    Package(int(package[0]), package[1], package[2], package[3], package[4], package[5], package[6]))

    def import_distances(self):
        # import addresses and distances from csv file
        with open('distances.csv') as df:
            # skip header
            next(df)
            for line in df:
                from_add = None
                to_add = None
                address = [p.strip() for p in line.split(',')]
                if not any(address[0] == a.name for a in self.graph.adj_list):
                    from_add = AddressNode(address[0], address[1])
                    self.graph.add_address_node(from_add)
                else:
                    from_add = next((a for a in self.graph.adj_list if a.name == address[0]), None)

                if not any(address[2] == a.name for a in self.graph.adj_list):
                    to_add = AddressNode(address[2], address[3])
                    self.graph.add_address_node(to_add)
                else:
                    to_add = next((a for a in self.graph.adj_list if a.name == address[2]), None)

                self.graph.add_undir_edge(from_add, to_add, float(address[4]))

        for p in self.packages:
            for a in self.graph.adj_list:
                if p is not None:
                    if p.delivery_address == a.address:
                        a.packages.append(p)
                        p.delivery_address = a

    def show_menu(self):
        # the main menu
        print('\n\t' + '*' * 36)
        print('\t*  WGUPS Delivery Menu             *')
        print('\t*                                  *')
        print('\t*  ' + self.sim_time.strftime('%I:%M %p') + '                        *')
        print('\t*                                  *')
        print("\t*  1 - Simulate entire day         *")
        print("\t*  2 - Advance one hour            *")
        print("\t*  3 - Lookup package information  *")
        print("\t*  4 - Current status report       *")
        print("\t*  5 - Exit program                *")
        print('\t*                                  *')
        print('\t' + '*' * 36)
