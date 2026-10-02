"""Общие стили для диаграмм C4 (чтобы все диаграммы выглядели одинаково)."""

STYLES = {
    "person":    dict(fill="#08427B", stroke="#073b6f", color="#ffffff"),
    "new":       dict(fill="#2d9c5a", stroke="#1f7a45", color="#ffffff"),   # новый компонент MVP
    "extended":  dict(fill="#438DD5", stroke="#2e6295", color="#ffffff"),   # существующий, дорабатывается
    "unchanged": dict(fill="#8c8c8c", stroke="#666666", color="#ffffff"),   # существующий, без изменений
    "external":  dict(fill="#e6e6e6", stroke="#999999", color="#000000", dashed=True),  # внешняя система
}


def add(d, kind, id, x, y, w, h, title, tech="", desc="", shape="rect", size=11):
    """Блок в стиле C4: жирное название, [технология], описание."""
    lines = [title]
    if tech:
        lines.append("[" + tech + "]")
    if desc:
        lines.append(desc)
    st = dict(STYLES[kind])
    return d.box(id, x, y, w, h, "\n".join(lines), bold_first=True, size=size, shape=shape, **st)


def legend(d, x, y, items=None):
    """Легенда по цветам. items — список ключей из STYLES."""
    names = {
        "person": "Человек",
        "new": "Новый компонент MVP",
        "extended": "Существующий, дорабатывается",
        "unchanged": "Существующий, без изменений",
        "external": "Внешняя система",
    }
    items = items or ["person", "new", "extended", "unchanged", "external"]
    d.text("lg_t", x, y, 120, 22, "Легенда:", size=11, bold=True)
    for i, k in enumerate(items):
        st = dict(STYLES[k])
        d.box("lg_" + k, x + 90 + i * 215, y, 205, 26, names[k], size=10, **st)
