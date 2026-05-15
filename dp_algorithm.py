def tree_dp(adj, root, has_apple):
    n = len(adj)
    parent = [-1] * n
    order = [root]
    parent[root] = root
    for node in order:
        for nei in adj[node]:
            if nei == parent[node]:
                continue
            parent[nei] = node
            order.append(nei)

    apple_count = [0] * n
    edges_needed = set()
    for node in reversed(order):
        count = 1 if has_apple[node] else 0
        for nei in adj[node]:
            if nei == parent[node]:
                continue
            count += apple_count[nei]
            if apple_count[nei] > 0:
                edges_needed.add(frozenset((node, nei)))
        apple_count[node] = count

    return len(edges_needed) * 2, edges_needed, apple_count
