def read_grid(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        first_line = file.readline().strip().split()
        # read first line of .grid file and split them into 4 parts
        N = int(first_line[0])
        M = int(first_line[1])
        benPen = int(first_line[2])
        viaPen = int(first_line[3])

        # init layer matrix
        layer1 = []
        layer2 = []

        # read layer1
        for _ in range(M):
            line = file.readline().strip().split()
            layer1.append([int(x) for x in line])

        # read layer2
        for _ in range(M):
            line = file.readline().strip().split()
            layer2.append([int(x) for x in line])

    return N, M, benPen, viaPen, layer1, layer2

def read_netlist(filename):
    with open(filename, 'r') as file:
        # read first line of .nl file
        net_num_line = file.readline().strip()
        net_num = int(net_num_line)

        # init netlist storage
        net_target = []

        # read each line of .nl
        for _ in range(net_num):
            line = file.readline().strip()
            elements = line.split()

            if len(elements) != 7:
                raise ValueError("wrong file format!")
            # using dictionary to record netlist information
            net_dict = {
                'netID': int(elements[0]),
                'start_layer': int(elements[1]),
                'start_X': int(elements[2]),
                'start_Y': int(elements[3]),
                'end_layer': int(elements[4]),
                'end_X': int(elements[5]),
                'end_Y': int(elements[6])
            }

            net_target.append(net_dict)

    return net_num, net_target
