import sys
import tkinter as tk
from tkinter import messagebox, ttk

MAX_RECURSION_DEPTH = 10000
COLOR_SCALE_START = (82, 148, 255)
COLOR_SCALE_END = (255, 141, 82)
CENTROID_PALETTE = ["#6ea8ff", "#7dd87d", "#ffd56e", "#f7a572", "#d69bf8", "#7ad1e8"]
EDGE_BASE_COLOR = "#b0b0b0"
EDGE_HLD_HEAVY_COLOR = "#f39c12"
NODE_DEFAULT_COLOR = "#6ea8ff"
NODE_OUTLINE_COLOR = "#3d3d3d"


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


def tree_dp(adj, root):
    n = len(adj)
    parent = [-1] * n
    depth = [0] * n
    order = []
    stack = [root]
    parent[root] = root
    while stack:
        node = stack.pop()
        order.append(node)
        for nei in adj[node]:
            if nei == parent[node]:
                continue
            parent[nei] = node
            depth[nei] = depth[node] + 1
            stack.append(nei)

    size = [1] * n
    max_depth = [0] * n
    for node in reversed(order):
        for nei in adj[node]:
            if nei == parent[node]:
                continue
            size[node] += size[nei]
            max_depth[node] = max(max_depth[node], max_depth[nei] + 1)
    return size, depth, max_depth


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


class TreeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Алгоритмы на дереве: DFS, DP, Centroid, HLD")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self._build_ui()
        self._load_sample()

    def _build_ui(self):
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(container, padding=12)
        control_frame.grid(row=0, column=0, sticky="ns")

        canvas_frame = ttk.Frame(container, padding=(0, 12, 12, 12))
        canvas_frame.grid(row=0, column=1, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.rowconfigure(1, weight=0)

        ttk.Label(control_frame, text="Параметры дерева", font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )

        ttk.Label(control_frame, text="Количество вершин:").grid(row=1, column=0, sticky="w", pady=(8, 2))
        self.nodes_var = tk.StringVar(value="7")
        ttk.Entry(control_frame, textvariable=self.nodes_var, width=10).grid(row=1, column=1, sticky="w", pady=(8, 2))

        ttk.Label(control_frame, text="Корень:").grid(row=2, column=0, sticky="w", pady=2)
        self.root_var = tk.StringVar(value="1")
        ttk.Entry(control_frame, textvariable=self.root_var, width=10).grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(control_frame, text="Рёбра (u v):").grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 2))

        edges_frame = ttk.Frame(control_frame)
        edges_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
        edges_frame.columnconfigure(0, weight=1)
        edges_frame.rowconfigure(0, weight=1)

        self.edges_text = tk.Text(edges_frame, width=28, height=12, wrap="none")
        self.edges_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(edges_frame, orient="vertical", command=self.edges_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.edges_text.configure(yscrollcommand=scrollbar.set)

        ttk.Label(control_frame, text="Алгоритм:").grid(row=5, column=0, columnspan=2, sticky="w", pady=(12, 4))
        self.algorithm_var = tk.StringVar(value="dfs")
        algo_frame = ttk.Frame(control_frame)
        algo_frame.grid(row=6, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(algo_frame, text="Полный DFS с возвратом", variable=self.algorithm_var, value="dfs").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Radiobutton(algo_frame, text="DP на дереве", variable=self.algorithm_var, value="dp").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Radiobutton(algo_frame, text="Центроидная декомпозиция", variable=self.algorithm_var, value="centroid").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Radiobutton(algo_frame, text="Heavy-Light Decomposition", variable=self.algorithm_var, value="hld").grid(
            row=3, column=0, sticky="w"
        )

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(12, 6))
        button_frame.columnconfigure(0, weight=1)
        ttk.Button(button_frame, text="Загрузить пример", command=self._load_sample).grid(row=0, column=0, sticky="ew")
        ttk.Button(button_frame, text="Запустить", command=self._run).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        ttk.Label(control_frame, text="Результаты:").grid(row=8, column=0, columnspan=2, sticky="w", pady=(12, 4))
        self.output_text = tk.Text(control_frame, width=32, height=14, wrap="word", state="disabled")
        self.output_text.grid(row=9, column=0, columnspan=2, sticky="nsew")

        self.canvas = tk.Canvas(canvas_frame, background="white", highlightthickness=1, highlightbackground="#d0d0d0")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        ttk.Label(
            canvas_frame,
            text="Визуализация: цвет узлов/рёбер отражает выбранный алгоритм",
            foreground="#555",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _load_sample(self):
        self.nodes_var.set("9")
        self.root_var.set("1")
        sample_edges = "\n".join(
            [
                "1 2",
                "1 3",
                "2 4",
                "2 5",
                "3 6",
                "3 7",
                "6 8",
                "6 9",
            ]
        )
        self.edges_text.delete("1.0", tk.END)
        self.edges_text.insert(tk.END, sample_edges)
        self._run()

    def _parse_input(self):
        try:
            n = int(self.nodes_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Количество вершин должно быть числом.")
            return None
        if n <= 0:
            messagebox.showerror("Ошибка", "Количество вершин должно быть положительным.")
            return None
        try:
            root = int(self.root_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Корень должен быть числом.")
            return None
        if not 1 <= root <= n:
            messagebox.showerror("Ошибка", "Корень должен быть в диапазоне 1..n.")
            return None
        root -= 1

        edges = []
        seen_edges = set()
        for line in self.edges_text.get("1.0", tk.END).strip().splitlines():
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 2:
                messagebox.showerror("Ошибка", f"Некорректная строка рёбер: {line}")
                return None
            try:
                u, v = (int(parts[0]) - 1, int(parts[1]) - 1)
            except ValueError:
                messagebox.showerror("Ошибка", f"Некорректная строка рёбер: {line}")
                return None
            if not (0 <= u < n and 0 <= v < n):
                messagebox.showerror("Ошибка", "Вершины должны быть в диапазоне 1..n.")
                return None
            if u == v:
                messagebox.showerror("Ошибка", "Ребро не может соединять вершину саму с собой.")
                return None
            edge = (min(u, v), max(u, v))
            if edge in seen_edges:
                messagebox.showerror("Ошибка", "В рёбрах найдены дубликаты.")
                return None
            seen_edges.add(edge)
            edges.append((u, v))

        if len(edges) != n - 1:
            messagebox.showerror("Ошибка", "Для дерева должно быть ровно n-1 ребро.")
            return None

        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        stack = [root]
        visited = [False] * n
        visited[root] = True
        while stack:
            node = stack.pop()
            for nei in adj[node]:
                if visited[nei]:
                    continue
                visited[nei] = True
                stack.append(nei)
        if not all(visited):
            messagebox.showerror("Ошибка", "Граф должен быть связным деревом.")
            return None

        return n, adj, root

    def _compute_layout(self, adj, root):
        n = len(adj)
        parent = [-1] * n
        children = [[] for _ in range(n)]
        order = [root]
        parent[root] = root
        for node in order:
            for nei in adj[node]:
                if nei == parent[node]:
                    continue
                parent[nei] = node
                children[node].append(nei)
                order.append(nei)

        x = [0.0] * n
        y = [0.0] * n
        leaf_index = 0

        def dfs(node, depth):
            nonlocal leaf_index
            if not children[node]:
                x[node] = leaf_index
                leaf_index += 1
            else:
                for child in children[node]:
                    dfs(child, depth + 1)
                x[node] = sum(x[child] for child in children[node]) / len(children[node])
            y[node] = depth

        dfs(root, 0)
        max_depth = max(y) if y else 0
        return x, y, max_depth

    @staticmethod
    def _color_scale(value, min_value, max_value, start=COLOR_SCALE_START, end=COLOR_SCALE_END):
        if max_value == min_value:
            t = 0.5
        else:
            t = (value - min_value) / (max_value - min_value)
        r = int(start[0] + t * (end[0] - start[0]))
        g = int(start[1] + t * (end[1] - start[1]))
        b = int(start[2] + t * (end[2] - start[2]))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, adj, root, node_colors, extra_labels, edge_styles):
        self.canvas.delete("all")
        self.update_idletasks()
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 600

        x_raw, y_raw, max_depth = self._compute_layout(adj, root)
        min_x, max_x = min(x_raw), max(x_raw)
        margin = 50
        scale_x = (width - 2 * margin) / max(1.0, (max_x - min_x))
        scale_y = (height - 2 * margin) / max(1.0, max_depth)

        def sx(idx):
            return margin + (x_raw[idx] - min_x) * scale_x

        def sy(idx):
            return margin + y_raw[idx] * scale_y

        n = len(adj)
        for u in range(n):
            for v in adj[u]:
                if v < u:
                    continue
                style = edge_styles.get(frozenset((u, v)), {})
                color = style.get("color", EDGE_BASE_COLOR)
                width_line = style.get("width", 2)
                self.canvas.create_line(sx(u), sy(u), sx(v), sy(v), fill=color, width=width_line)

        radius = 16
        for node in range(n):
            cx, cy = sx(node), sy(node)
            color = node_colors.get(node, NODE_DEFAULT_COLOR)
            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=color,
                outline=NODE_OUTLINE_COLOR,
            )
            self.canvas.create_text(cx, cy, text=str(node + 1), fill="black", font=("TkDefaultFont", 10, "bold"))
            extra = extra_labels.get(node, "")
            if extra:
                self.canvas.create_text(cx, cy + radius + 10, text=extra, fill="#333", font=("TkDefaultFont", 8))

    def _set_output(self, lines):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "\n".join(lines))
        self.output_text.configure(state="disabled")

    def _run(self):
        parsed = self._parse_input()
        if not parsed:
            return
        n, adj, root = parsed
        algorithm = self.algorithm_var.get()

        node_colors = {}
        extra_labels = {}
        edge_styles = {}
        output_lines = []

        if algorithm == "dfs":
            tin, tout, tour = dfs_with_return(adj, root)
            min_t, max_t = min(tin), max(tin)
            for node in range(n):
                node_colors[node] = self._color_scale(tin[node], min_t, max_t)
                extra_labels[node] = f"{tin[node]}/{tout[node]}"
            output_lines.append("DFS с возвратом (Эйлеров обход):")
            output_lines.append("Путь: " + " ".join(str(v + 1) for v in tour))
            output_lines.append("tin: " + " ".join(str(t) for t in tin))
            output_lines.append("tout: " + " ".join(str(t) for t in tout))
        elif algorithm == "dp":
            size, depth, max_depth = tree_dp(adj, root)
            min_s, max_s = min(size), max(size)
            for node in range(n):
                node_colors[node] = self._color_scale(size[node], min_s, max_s)
                extra_labels[node] = f"s={size[node]}"
            output_lines.append("DP на дереве:")
            output_lines.append("subtree_size: " + " ".join(str(s) for s in size))
            output_lines.append("depth: " + " ".join(str(d) for d in depth))
            output_lines.append("max_depth_in_subtree: " + " ".join(str(d) for d in max_depth))
        elif algorithm == "centroid":
            parent, level = centroid_decomposition(adj, root)
            for node in range(n):
                node_colors[node] = CENTROID_PALETTE[level[node] % len(CENTROID_PALETTE)]
                extra_labels[node] = f"lvl {level[node]}"
            output_lines.append("Центроидная декомпозиция:")
            output_lines.append("centroid_parent: " + " ".join(str(p + 1 if p != -1 else 0) for p in parent))
            output_lines.append("level: " + " ".join(str(l) for l in level))
        elif algorithm == "hld":
            parent, heavy, head, pos, depth = heavy_light_decomposition(adj, root)
            heads = sorted(set(head))
            head_index = {h: i for i, h in enumerate(heads)}
            for node in range(n):
                node_colors[node] = self._color_scale(head_index[head[node]], 0, max(1, len(heads) - 1))
                extra_labels[node] = f"h{head[node] + 1}"
            for node in range(n):
                if heavy[node] != -1:
                    edge_styles[frozenset((node, heavy[node]))] = {"color": EDGE_HLD_HEAVY_COLOR, "width": 4}
            output_lines.append("Heavy-Light Decomposition:")
            output_lines.append("parent: " + " ".join(str(p + 1 if p != -1 else 0) for p in parent))
            output_lines.append("heavy_child: " + " ".join(str(h + 1 if h != -1 else 0) for h in heavy))
            output_lines.append("head: " + " ".join(str(h + 1) for h in head))
            output_lines.append("pos: " + " ".join(str(p) for p in pos))
            output_lines.append("depth: " + " ".join(str(d) for d in depth))
        else:
            messagebox.showerror("Ошибка", "Неизвестный алгоритм.")
            return

        self._draw(adj, root, node_colors, extra_labels, edge_styles)
        self._set_output(output_lines)


def main():
    sys.setrecursionlimit(MAX_RECURSION_DEPTH)  # Increase if RecursionError appears on deep trees; lower if stack is limited.
    app = TreeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
