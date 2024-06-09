import heapq
import copy

# 定义网格中的节点
class Node:
    def __init__(self, position, layer, parent=None):
        self.position = position
        self.layer = layer
        self.parent = parent
        self.g = 0  # 距起点的实际代价
        self.h = 0  # 启发式代价
        self.f = 0  # 总代价

    def __lt__(self, other):
        return self.f < other.f

# A*算法实现
def astar(grid1, grid2, start, end, start_layer, end_layer, layer_change_cost, bend_cost):
    start_node = Node(start, start_layer)
    end_node = Node(end, end_layer)

    open_list = []
    closed_list = set()

    heapq.heappush(open_list, start_node)

    while open_list:
        current_node = heapq.heappop(open_list)
        closed_list.add((current_node.position, current_node.layer))

        if current_node.position == end_node.position and current_node.layer == end_node.layer:
            path = []
            while current_node:
                path.append((current_node.position, current_node.layer))
                current_node = current_node.parent
            return path[::-1]  # 返回路径从起点到终点

        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # 4个方向
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            if 0 <= node_position[0] < len(grid1) and 0 <= node_position[1] < len(grid1[0]):
                if current_node.layer == 1:
                    if grid1[node_position[0]][node_position[1]] != -1 or node_position == end:
                        new_node = Node(node_position, current_node.layer, current_node)
                        children.append(new_node)
                else:
                    if grid2[node_position[0]][node_position[1]] != -1 or node_position == end:
                        new_node = Node(node_position, current_node.layer, current_node)
                        children.append(new_node)

        # 考虑层间移动
        new_layer = 1 - current_node.layer
        if new_layer == 1:
            if (0 <= current_node.position[0] < len(grid1) and
                0 <= current_node.position[1] < len(grid1[0]) and
                (grid1[current_node.position[0]][current_node.position[1]] != -1 or current_node.position == end)):
                new_node = Node(current_node.position, new_layer, current_node)
                new_node.g = current_node.g + layer_change_cost  # 加上层间移动代价
                new_node.h = manhattan_distance(new_node.position, end_node.position)
                new_node.f = new_node.g + new_node.h
                children.append(new_node)
        else:
            if (0 <= current_node.position[0] < len(grid2) and
                0 <= current_node.position[1] < len(grid2[0]) and
                (grid2[current_node.position[0]][current_node.position[1]] != -1 or current_node.position == end)):
                new_node = Node(current_node.position, new_layer, current_node)
                new_node.g = current_node.g + layer_change_cost  # 加上层间移动代价
                new_node.h = manhattan_distance(new_node.position, end_node.position)
                new_node.f = new_node.g + new_node.h
                children.append(new_node)

        for child in children:
            if (child.position, child.layer) in closed_list:
                continue

            if child.layer == 1:
                child.g = current_node.g + grid1[child.position[0]][child.position[1]]
            else:
                child.g = current_node.g + grid2[child.position[0]][child.position[1]]

            child.h = manhattan_distance(child.position, end_node.position)

            # 增加弯折代价
            if current_node.parent:
                if (current_node.position[0] - current_node.parent.position[0] !=
                    child.position[0] - current_node.position[0]) or \
                   (current_node.position[1] - current_node.parent.position[1] !=
                    child.position[1] - current_node.position[1]):
                    child.h += bend_cost  # 每次改变方向增加一个额外代价

            child.f = child.g + child.h

            if add_to_open(open_list, child):
                heapq.heappush(open_list, child)

    return None  # 如果没有找到路径，返回None

def manhattan_distance(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def add_to_open(open_list, child):
    for node in open_list:
        if child.position == node.position and child.layer == node.layer and child.g >= node.g:
            return False
    return True

# 标记路径为障碍物
def mark_path_as_obstacle(grid1, grid2, path, path_id):
    for position, layer in path:
        if layer == 1:
            grid1[position[0]][position[1]] = path_id
        else:
            grid2[position[0]][position[1]] = path_id

# 将路径结果写入文件
def write_paths_to_file(filename, paths):
    with open(filename, 'w') as file:
        file.write(f"{len(paths)}\n")
        for path in paths:
            file.write(f"{path['netID']}\n")
            if path['path']:
                prev_layer = -1
                for position, layer in path['path']:
                    if prev_layer != -1 and prev_layer != layer:
                        file.write(f"3 {position[0]} {position[1]}\n")
                    file.write(f"{layer + 1} {position[0]} {position[1]}\n")
                    prev_layer = layer
                file.write("0\n")  # 添加路径结束标识
            else:
                file.write("0\n")  # 写入 0 表示没有找到路径

# 主函数：布置N条路径
def layout_paths(layer1, layer2, start_end_list, layer_change_cost, bend_cost):
    path_id = 2  # 从2开始，因为0和1已经用于其他目的
    paths = []

    for connection in start_end_list:
        start = (connection['start_X'], connection['start_Y'])
        end = (connection['end_X'], connection['end_Y'])
        start_layer = connection['start_layer'] - 1
        end_layer = connection['end_layer'] - 1
        net_id = connection['netID']

        path = astar(layer1, layer2, start, end, start_layer, end_layer, layer_change_cost, bend_cost)
        if path:
            print(f"Path for netID {net_id} from {start} layer {start_layer + 1} to {end} layer {end_layer + 1}:", path)
            mark_path_as_obstacle(layer1, layer2, path, path_id)
            paths.append({'netID': net_id, 'path': path})
            path_id += 1
        else:
            print(f"No path found for netID {net_id} from {start} layer {start_layer + 1} to {end} layer {end_layer + 1}")
            paths.append({'netID': net_id, 'path': None})

    write_paths_to_file("paths.txt", paths)

import fileRead

# Read grid from
file_grid = 'benchmark/bench1.grid'
N, M, benPen, viaPen, layer1, layer2 = fileRead.read_grid(file_grid)
# N:cols ; M:rows  ;  viaPen: via penalty ; benPen: bend penalty

file_netlist = 'benchmark/bench1.nl'
net_num, net_target = fileRead.read_netlist(file_netlist)
# 起点和终点对列表，包含netID、start_layer和end_layer


layout_paths(layer2, layer1, net_target, viaPen, benPen)