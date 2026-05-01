def heavy_light_decomposition(adj, root):
    n = len(adj)
    parent = [-1] * n
    depth = [0] * n
    size = [1] * n
    heavy = [-1] * n

    def dfs(node, par):
        max_size = 0
        for nei in adj[node]:
            if nei == par:
                continue
            parent[nei] = node
            depth[nei] = depth[node] + 1
            dfs(nei, node)
            size[node] += size[nei]
            if size[nei] > max_size:
                max_size = size[nei]
                heavy[node] = nei

    dfs(root, -1)

    head = [0] * n
    pos = [0] * n
    current_pos = 0

    def decompose(node, h):
        nonlocal current_pos
        head[node] = h
        pos[node] = current_pos
        current_pos += 1
        if heavy[node] != -1:
            decompose(heavy[node], h)
        for nei in adj[node]:
            if nei == parent[node] or nei == heavy[node]:
                continue
            decompose(nei, nei)

    decompose(root, root)
    return parent, heavy, head, pos, depth
