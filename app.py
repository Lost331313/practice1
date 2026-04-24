import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from optimizer import solve_optimization

# Настройка страницы
st.set_page_config(layout="wide", page_title="Оптимизация сети")
st.title("🌐 Сервис минимизации полосы пропускания")
st.markdown("---")

# Инициализация хранилища
if 'nodes' not in st.session_state:
    st.session_state.nodes = {}
if 'links' not in st.session_state:
    st.session_state.links = []
if 'demands' not in st.session_state:
    st.session_state.demands = []
if 'result' not in st.session_state:
    st.session_state.result = None

# ========== БОКОВАЯ ПАНЕЛЬ ДЛЯ ВВОДА ==========
with st.sidebar:
    st.header("📝 Редактор сети")

    # === Добавление узла ===
    st.subheader("➕ Узел")
    col1, col2 = st.columns(2)
    with col1:
        node_id = st.number_input("ID узла", min_value=1, step=1, key="node_id")
    with col2:
        node_x = st.number_input("X", value=100, key="node_x")
        node_y = st.number_input("Y", value=200, key="node_y")

    if st.button("➕ Добавить узел", use_container_width=True):
        if node_id in st.session_state.nodes:
            st.error(f"Узел {node_id} уже существует!")
        else:
            st.session_state.nodes[node_id] = {"x": node_x, "y": node_y}
            st.success(f"Узел {node_id} добавлен")
            st.rerun()

    st.markdown("---")

    # === Добавление связи ===
    st.subheader("🔗 Связь")
    col1, col2 = st.columns(2)
    with col1:
        link_src = st.number_input("От узла", min_value=1, step=1, key="link_src")
    with col2:
        link_dst = st.number_input("К узлу", min_value=1, step=1, key="link_dst")

    link_cap = st.number_input("Пропускная способность", min_value=1, value=100, key="link_cap")

    if st.button("➕ Добавить связь", use_container_width=True):
        if link_src not in st.session_state.nodes:
            st.error(f"Узел {link_src} не существует!")
        elif link_dst not in st.session_state.nodes:
            st.error(f"Узел {link_dst} не существует!")
        else:
            st.session_state.links.append({"src": link_src, "dst": link_dst, "capacity": link_cap})
            st.success(f"Связь {link_src}→{link_dst} добавлена")
            st.rerun()

    st.markdown("---")

    # === Добавление требования ===
    st.subheader("📦 Требование (трафик)")
    col1, col2 = st.columns(2)
    with col1:
        dem_src = st.number_input("Источник", min_value=1, step=1, key="dem_src")
    with col2:
        dem_dst = st.number_input("Назначение", min_value=1, step=1, key="dem_dst")

    dem_vol = st.number_input("Объём трафика", min_value=1, value=10, key="dem_vol")

    if st.button("➕ Добавить требование", use_container_width=True):
        if dem_src not in st.session_state.nodes:
            st.error(f"Узел {dem_src} не существует!")
        elif dem_dst not in st.session_state.nodes:
            st.error(f"Узел {dem_dst} не существует!")
        else:
            st.session_state.demands.append({"src": dem_src, "dst": dem_dst, "volume": dem_vol})
            st.success(f"Требование {dem_src}→{dem_dst} (объём {dem_vol}) добавлено")
            st.rerun()

    st.markdown("---")

    # === Кнопка сброса ===
    if st.button("🗑️ Очистить всё", use_container_width=True):
        st.session_state.nodes = {}
        st.session_state.links = []
        st.session_state.demands = []
        st.session_state.result = None
        st.success("Всё очищено!")
        st.rerun()

    # === Отображение текущих данных ===
    st.markdown("---")
    st.subheader("📋 Текущие данные")

    st.write(f"**Узлы:** {len(st.session_state.nodes)}")
    st.write(f"**Связи:** {len(st.session_state.links)}")
    st.write(f"**Требования:** {len(st.session_state.demands)}")

    if st.button("Показать детали"):
        if st.session_state.nodes:
            st.json(st.session_state.nodes)
        if st.session_state.links:
            st.json(st.session_state.links)
        if st.session_state.demands:
            st.json(st.session_state.demands)

# ========== ОСНОВНАЯ ОБЛАСТЬ ==========`
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🗺️ Визуализация сети")

    # Кнопка запуска оптимизации
    if st.button("🚀 ЗАПУСТИТЬ ОПТИМИЗАЦИЮ", type="primary", use_container_width=True):
        if len(st.session_state.nodes) < 2:
            st.error("❌ Добавьте хотя бы 2 узла")
        elif len(st.session_state.links) == 0:
            st.error("❌ Добавьте хотя бы одну связь")
        elif len(st.session_state.demands) == 0:
            st.error("❌ Добавьте хотя бы одно требование")
        else:
            with st.spinner("🔄 Решаю задачу оптимизации..."):
                result = solve_optimization(
                    st.session_state.nodes,
                    st.session_state.links,
                    st.session_state.demands
                )
                st.session_state.result = result
                st.rerun()

    # Рисуем граф, если есть результат
    if st.session_state.result:
        result = st.session_state.result

        if result["status"] == "optimal":
            # Создаём граф с Plotly
            fig = go.Figure()

            # Добавляем узлы
            node_ids = list(st.session_state.nodes.keys())
            node_x = [st.session_state.nodes[n]["x"] for n in node_ids]
            node_y = [st.session_state.nodes[n]["y"] for n in node_ids]
            node_labels = [str(n) for n in node_ids]

            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(size=35, color='#4B8BBE', line=dict(width=2, color='white')),
                text=node_labels,
                textposition="middle center",
                textfont=dict(size=14, color='white'),
                name="Узлы",
                hoverinfo='text',
                hovertext=[f"Узел {n}" for n in node_ids]
            ))

            # Добавляем рёбра
            for link in st.session_state.links:
                src = link["src"]
                dst = link["dst"]
                cap = link["capacity"]

                if src in st.session_state.nodes and dst in st.session_state.nodes:
                    # Находим загрузку из результата
                    load_data = next(
                        (l for l in result["link_loads"] if l["src"] == src and l["dst"] == dst),
                        None
                    )

                    if load_data:
                        utilization = load_data["utilization"]
                        if utilization > 0.9:
                            color = "red"
                            width_val = 6
                        elif utilization > 0.5:
                            color = "orange"
                            width_val = 4
                        else:
                            color = "green"
                            width_val = 2

                        hover_text = f"📡 {src} → {dst}<br>📊 Загрузка: {load_data['load']:.1f} / {cap}<br>📈 Использование: {utilization * 100:.1f}%"
                    else:
                        color = "gray"
                        width_val = 2
                        hover_text = f"🔗 {src} → {dst}<br>Ёмкость: {cap}"

                    fig.add_trace(go.Scatter(
                        x=[st.session_state.nodes[src]["x"], st.session_state.nodes[dst]["x"]],
                        y=[st.session_state.nodes[src]["y"], st.session_state.nodes[dst]["y"]],
                        mode='lines',
                        line=dict(color=color, width=width_val),
                        hoverinfo='text',
                        text=hover_text,
                        showlegend=False
                    ))

            fig.update_layout(
                title="🎨 Сеть с цветовой индикацией загрузки",
                showlegend=False,
                height=500,
                xaxis_title="Координата X",
                yaxis_title="Координата Y",
                plot_bgcolor='#f0f2f6',
                hovermode='closest'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Вывод статистики
            st.success(f"✅ **Статус:** OPTIMAL | **Суммарный трафик:** {result['total_cost']:.2f}")

            # Таблица загрузки каналов
            st.subheader("📊 Загрузка каналов")
            df = pd.DataFrame(result["link_loads"])
            df["utilization_pct"] = (df["utilization"] * 100).round(1)
            df = df[["src", "dst", "load", "capacity", "utilization_pct"]]
            df.columns = ["От", "К", "Трафик", "Ёмкость", "Загрузка %"]
            st.dataframe(df, use_container_width=True)

        else:
            st.error(f"❌ {result['message']}")
    else:
        st.info("💡 Добавьте узлы, связи и требования, затем нажмите 'ЗАПУСТИТЬ ОПТИМИЗАЦИЮ'")

with col2:
    st.header("📋 Требования")
    if st.session_state.demands:
        df_demands = pd.DataFrame(st.session_state.demands)
        st.dataframe(df_demands, use_container_width=True)

        total_traffic = sum(d["volume"] for d in st.session_state.demands)
        st.metric("📊 Суммарный трафик", f"{total_traffic}")
    else:
        st.info("Нет добавленных требований")

    st.markdown("---")
    st.header("🔗 Связи")
    if st.session_state.links:
        df_links = pd.DataFrame(st.session_state.links)
        st.dataframe(df_links, use_container_width=True)
    else:
        st.info("Нет добавленных связей")
