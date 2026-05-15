def centroid_decomposition(adj, start):
    n = len(adj)
    parent = [-1] * n
    level = [0] * n
    used = [False] * n
    sizes = [0] * n

    def calc_size(node, par):
        sizes[node] = 1
        for nei in adj[node]:
            if nei == par or used[nei]:
                continue
            calc_size(nei, node)
            sizes[node] += sizes[nei]

    def find_centroid(node, par, total):
        for nei in adj[node]:
            if nei == par or used[nei]:
                continue
            if sizes[nei] > total // 2:
                return find_centroid(nei, node, total)
        return node

    def build(node, par, depth):
        calc_size(node, -1)
        centroid = find_centroid(node, -1, sizes[node])
        parent[centroid] = par
        level[centroid] = depth
        used[centroid] = True
        for nei in adj[centroid]:
            if used[nei]:
                continue
            build(nei, centroid, depth + 1)

    build(start, -1, 0)
    return parent, level
