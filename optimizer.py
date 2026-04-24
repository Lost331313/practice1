from pulp import *


def solve_optimization(nodes, links, demands):
    """
    Решает задачу оптимизации трафика с помощью PuLP
    """

    # Создаём задачу минимизации
    prob = LpProblem("Network_Optimization", LpMinimize)

    # Список всех каналов
    link_list = [(l["src"], l["dst"]) for l in links]

    # Словарь пропускной способности
    capacity = {(l["src"], l["dst"]): l["capacity"] for l in links}

    # Переменные: x[d, src, dst]
    x = {}
    for d_idx, demand in enumerate(demands):
        for (src, dst) in link_list:
            var_name = f"x_{d_idx}_{src}_{dst}"
            x[(d_idx, src, dst)] = LpVariable(var_name, lowBound=0, cat='Continuous')

    # ЦЕЛЕВАЯ ФУНКЦИЯ: минимизация суммы трафика
    prob += lpSum(x[(d_idx, src, dst)]
                  for d_idx in range(len(demands))
                  for (src, dst) in link_list)

    # ОГРАНИЧЕНИЕ 1: Сохранение потока
    all_nodes = set()
    for n in nodes:
        all_nodes.add(n)
    for l in links:
        all_nodes.add(l["src"])
        all_nodes.add(l["dst"])
    for d in demands:
        all_nodes.add(d["src"])
        all_nodes.add(d["dst"])

    for d_idx, demand in enumerate(demands):
        for node in all_nodes:
            outflow = lpSum(x[(d_idx, src, dst)] for (src, dst) in link_list if src == node)
            inflow = lpSum(x[(d_idx, src, dst)] for (src, dst) in link_list if dst == node)

            if node == demand["src"]:
                prob += (outflow - inflow == demand["volume"])
            elif node == demand["dst"]:
                prob += (outflow - inflow == -demand["volume"])
            else:
                prob += (outflow - inflow == 0)

    # ОГРАНИЧЕНИЕ 2: Пропускная способность каналов
    for (src, dst) in link_list:
        prob += lpSum(x[(d_idx, src, dst)] for d_idx in range(len(demands))) <= capacity[(src, dst)]

    # Решаем задачу
    solver = PULP_CBC_CMD(msg=False)
    result_status = prob.solve(solver)

    # Проверяем результат
    if result_status == 1:  # Optimal
        link_loads = []
        for (src, dst) in link_list:
            load = sum(x[(d_idx, src, dst)].varValue for d_idx in range(len(demands)))
            link_loads.append({
                "src": src,
                "dst": dst,
                "load": load,
                "capacity": capacity[(src, dst)],
                "utilization": load / capacity[(src, dst)] if capacity[(src, dst)] > 0 else 0
            })

        total_cost = sum(link_load['load'] for link_load in link_loads)

        return {
            "status": "optimal",
            "total_cost": total_cost,
            "link_loads": link_loads
        }
    else:
        return {
            "status": "infeasible",
            "message": "Решение не найдено. Увеличьте пропускную способность каналов или проверьте данные."
        }
