def dfs_with_return(adj, root):
    n = len(adj)
    tin = [0] * n
    tout = [0] * n
    timer = 0
    tour = []

    def dfs(node, parent):
        nonlocal timer
        timer += 1
        tin[node] = timer
        tour.append(node)
        for nei in adj[node]:
            if nei == parent:
                continue
            dfs(nei, node)
            tour.append(node)
        timer += 1
        tout[node] = timer

    dfs(root, -1)
    return tin, tout, tour


def min_time_collect_apples(adj, root, has_apple):
    edges_needed = set()

    def dfs(node, parent):
        contains = has_apple[node]
        for nei in adj[node]:
            if nei == parent:
                continue
            child_contains = dfs(nei, node)
            if child_contains:
                edges_needed.add(frozenset((node, nei)))
                contains = True
        return contains

    dfs(root, -1)
    return len(edges_needed) * 2, edges_needed
