# Ian De Bie Student ID #001114841
import classes
import operator

s = classes.Simulation()
selection = 0

def run_simulation(duration):
    '''
    Main Function called by choosing either option 1 or 2 from the menu
    Sets the new simulation time either for the full day or increment an hour based on menu selection
    loop through the two active trucks (truck 3 is out for maintenance today) :)
    deliver packages as long as not exceeding the simulation time

    :param duration: how much time to increment
    '''
    s.sim_time = min(s.sim_time.replace(hour=s.sim_time.hour + duration), classes.time(hour=17))
    for i in range(1, 3):
        truck = s.trucks['truck' + str(i)]
        while len(truck.packages) > 0:
            prepare_next_destination(truck)
            set_truck_destination(truck, truck.packages[0].delivery_address)
            get_time(truck, truck.packages[0].delivery_address.distance)
            if truck.truck_time < s.sim_time:
                deliver_package(truck)
            else:
                truck.truck_time = truck.backup_time
                break
        print('*' * 10)
        print('\nTruck #%s mileage: %.01f\n' % (truck.truck_number, truck.mileage))
        print('*' * 10)
    print('\nTotal Mileage: %.01f' % (s.trucks['truck1'].mileage + s.trucks['truck2'].mileage))

def get_time(v, d):
    '''
    check the amount of time it will take to go from current location to new destination
    :param v: the active truck
    :param d: the distance to travel to new destination
    :return:
    '''
    v.backup_time = v.truck_time
    new_minutes = round(v.truck_time.minute + float((d / 0.3) % 60))
    if new_minutes > 59:
        v.truck_time = v.truck_time.replace(hour=v.truck_time.hour + 1, minute=new_minutes - 60)
        new_minutes = v.truck_time.minute
    else:
        v.truck_time = v.truck_time.replace(minute=new_minutes)

def deliver_package(v):
    '''
    Deliver package function which updates delivery status and pops package from queue and appends to delivered queue
    :param v: the active truck
    :return:
    '''
    package_to_deliver = v.packages[0]
    package_to_deliver.delivery_status = 'Delivered at %s' % v.truck_time.strftime('%I:%M %p')
    v.mileage += package_to_deliver.delivery_address.distance
    print(package_to_deliver)
    temp = v.packages.pop(0)
    v.delivered.append(temp)
    v.last_stop = package_to_deliver.delivery_address
    if  len(v.packages) < 1:
        set_truck_destination(v, s.hub)
        v.mileage += s.hub.distance
        get_time(v, s.hub.distance)
        if v.truck_number == 1 and len(s.package_groups) > 1:
            reload_truck(v)
        elif v.truck_number == 2 and len(s.package_groups) > 0:
            reload_truck(v)

def prepare_next_destination(v):
    '''
    call the methods to update the distances for each address node and then sort the package queue
    :param v: the active truck
    :return:
    '''
    classes.get_shortest_path(s.graph, v.last_stop)
    classes.list_sort_distance(v.packages)

def set_truck_destination(truck, d):
    '''
    update the trucks destination and status attributes and then print it out
    :param truck: the active truck
    :param d: the new destination
    :return:
    '''
    truck.destination = d
    truck.status = 'Destination: %s' % truck.destination
    print_truck_status(truck)

def print_truck_status(truck):
    '''
    print the trucks status
    :param truck: the active truck
    :return:
    '''
    print('\nTruck #: %s\nPackages onboard: %s\nPackages delivered: %s\nLocation: %s\n%s\nDistance: %.01f miles\n' %
          (truck.truck_number, len(truck.packages), len(truck.delivered), truck.last_stop, truck.status,
           truck.destination.distance))

def reload_truck(v):
    '''
    the truck delivered all its packages and needs to reload and update status to show went back to hub
    :param v: the active truck
    :return:
    '''
    l = s.package_groups.pop()
    [v.packages.append(s) for s in l]
    for p in v.packages:
        p.delivery_status = 'Out for delivery on Truck %s' % v.truck_number
    v.last_stop = s.hub
    print('\n*** Returning to Hub to reload ***\n')

def are_all_packages_delivered():
    '''
    quick check to make sure all 40 packages were delivered
    :return:
    '''
    total = 0
    for k, truck in s.trucks.items():
        total += len(truck.delivered)
    return total == 40

def simulation_complete():
    '''
    print out in menu when user selects option 1 or 2 after packages have already been delivered
    :return:
    '''
    print('\nAll packages delivered')
    print('Simulation Complete')
    print('Select 3 to lookup package or')
    print('Select 4 to view status report')
    print('Select 5 to exit')

while True:
    # loop to display menu options until user exits
    s.show_menu()
    selection = input('\nEnter choice (1 - 5): ')

    try:
        selection = int(selection)
    except ValueError:
        print('Not a number! Enter a number from 1 - 5.')
        continue
    if selection not in (range(1, 6)):
        print('Invalid number! Enter a number from 1 - 5.')
        continue

    if selection == 1:
        if s.sim_time.hour == 17 or are_all_packages_delivered():
            simulation_complete()
            if s.sim_time.hour < 17:
                s.sim_time = s.sim_time.replace(hour=s.sim_time.hour + 1)
        else:
            run_simulation(9)
    elif selection == 2:
        if s.sim_time.hour == 17 or are_all_packages_delivered():
            simulation_complete()
            if s.sim_time.hour < 17:
                s.sim_time = s.sim_time.replace(hour=s.sim_time.hour + 1)
        else:
            run_simulation(1)
    elif selection == 3:
        pkg_id = input('\nEnter package ID number: ')
        try:
            pkg_id = int(pkg_id)
        except ValueError:
            print('Not a number! Enter a number from 1 - 5.')
            continue
        if pkg_id not in (range(1, 41)):
            print('Invalid number! Enter a number from 1 - 40.')
            continue
        package = s.packages.search(pkg_id)
        print('Package # %02d' % package.package_id)
        print('Address: %s' % package.delivery_address)
        print('City: %s' % package.delivery_city)
        print('Zip Code: %s' % package.delivery_zipcode)
        print('Deadline: %s' % package.delivery_deadline)
        print('Weight: %s' % package.weight)
        print('Special Note: %s' % package.special_note)
        print('Status: %s' % package.delivery_status)
    elif selection == 4:
        for k, truck in s.trucks.items():
            print('\nTruck #%s\nPackages delivered: %s\nMiles driven: %.01f' %
                  (truck.truck_number, len(truck.delivered), truck.mileage))
            print('Status: %s\n' % truck.status)
        for p in s.packages:
            if p is None:
                continue
            print('Package #%02d %s' % (p.package_id, p.delivery_status))
    elif selection == 5:
        print('Exiting Simulation')
        raise SystemExit


