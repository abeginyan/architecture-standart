"""Task3: C4 — контекст и контейнеры для MVP «Открытие депозитов онлайн»."""
import os
from diagramkit import Diagram
from c4 import add, legend

OUT = os.path.join(os.path.dirname(__file__), "..", "Task3")


def context():
    d = Diagram("C4 Context — онлайн-депозиты (MVP)", 1650, 960)
    d.text("title", 20, 8, 1500, 28, "C4. Диаграмма контекста: открытие депозитов онлайн (MVP)", size=15, bold=True)
    add(d, "person", "client", 30, 360, 200, 100, "Клиент", "Person", "новый или существующий клиент банка")
    add(d, "person", "ccmgr", 30, 640, 200, 100, "Менеджер кол-центра", "Person", "звонит по заявкам с сайта")
    add(d, "person", "dep", 930, 90, 260, 100, "Менеджер бэк-офиса депозитов", "Person", "обрабатывает заявки, ведёт ставки")
    add(d, "person", "cred", 1330, 360, 260, 100, "Сотрудник отдела кредитования", "Person", "согласует особые ставки")
    add(d, "extended", "site", 420, 90, 280, 110, "Сайт банка", "Software System",
        "новое: список депозитов со ставками и форма заявки")
    add(d, "extended", "ib", 420, 360, 280, 120, "Интернет-банк", "Software System",
        "новое: депозиты, персональные ставки, заявка с подтверждением по СМС")
    add(d, "extended", "abs", 930, 360, 280, 120, "АБС", "Software System",
        "новое: ставки и согласование в системе, приём заявок от интернет-банка")
    add(d, "extended", "cc", 420, 640, 280, 100, "Система кол-центра", "Software System",
        "новое: приём заявок с сайта")
    add(d, "unchanged", "sms", 930, 640, 280, 100, "СМС-шлюз", "Software System", "поддерживает IT-отдел банка")
    add(d, "external", "tel", 1330, 640, 260, 100, "Телеком-оператор", "External System", "отправка СМС клиентам")

    d.edge("client", "site", "UC1, UC2: смотрит ставки,\nоставляет заявку")
    d.edge("client", "ib", "UC4, UC5: смотрит ставки,\nподаёт заявку")
    d.edge("site", "ib", "UC1, UC2: запросы к API\nинтернет-банка (HTTPS)")
    d.edge("ib", "abs", "UC5, UC6: заявки →, ставки и статусы ←\n(через очередь, не напрямую)", bidir=True)
    d.edge("ib", "cc", "UC2: заявка\nс сайта")
    d.edge("ccmgr", "cc", "UC3: обрабатывает заявку")
    d.edge("ccmgr", "client", "UC3: звонит клиенту", dashed=True)
    d.edge("dep", "abs", "UC6, UC8: подтверждает условия,\nведёт ставки")
    d.edge("cred", "abs", "UC7: согласует\nособые ставки")
    d.edge("ib", "sms", "UC5, UC9: код подтверждения\nи уведомления")
    d.edge("sms", "tel", "отправка СМС")
    d.edge("tel", "client", "СМС клиенту", dashed=True, via=[(1460, 880), (12, 880), (12, 410)])
    legend(d, 20, 915, ["person", "extended", "unchanged", "external"])
    d.save(OUT, "C4_Context")


def containers():
    d = Diagram("C4 Container — онлайн-депозиты (MVP)", 2040, 1020)
    d.text("title", 20, 8, 1800, 28, "C4. Диаграмма контейнеров: открытие депозитов онлайн (MVP)", size=15, bold=True)

    # люди
    add(d, "person", "client", 20, 360, 150, 100, "Клиент", "Person")
    add(d, "person", "ccmgr", 1330, 50, 200, 80, "Менеджер кол-центра", "Person")
    add(d, "person", "dep", 1560, 850, 210, 80, "Менеджер бэк-офиса депозитов", "Person")
    add(d, "person", "cred", 1790, 850, 210, 80, "Сотрудник кредитования", "Person")

    # группы
    d.group("g_site", 270, 30, 320, 130, "Сайт банка")
    d.group("g_ib", 270, 215, 1000, 470, "Интернет-банк (расширяется)")
    d.group("g_kafka", 1315, 190, 175, 500, "Платформа обмена")
    d.group("g_abs", 1540, 215, 480, 570, "АБС")
    d.group("g_cc", 940, 30, 330, 130, "Система кол-центра (подрядчик)")

    # сайт и кол-центр
    add(d, "extended", "site", 285, 65, 290, 85, "Frontend сайта", "PHP + React.js",
        "новое: список депозитов, форма заявки")
    add(d, "extended", "cc", 955, 62, 300, 88, "Система кол-центра", "React / Java Spring Boot / PostgreSQL",
        "новое: приём заявок с сайта")
    # интернет-банк
    add(d, "extended", "mono", 285, 250, 245, 120, "Монолит интернет-банка", "ASP.NET MVC, .NET Fw 4.5",
        "новое: страницы депозитов и заявки; сессия клиента, список счетов")
    add(d, "unchanged", "dbib", 285, 420, 245, 90, "БД интернет-банка", "MS SQL", shape="cylinder")
    add(d, "new", "gw", 640, 250, 215, 110, "API Gateway", "YARP / nginx",
        "TLS, проверка токена, балансировка, ограничение частоты запросов")
    add(d, "new", "dsvc", 955, 250, 300, 120, "Сервис депозитов", ".NET 8, REST",
        "каталог депозитов и ставок, заявки, СМС-код подтверждения, статусы")
    add(d, "new", "dbdep", 955, 420, 300, 90, "БД сервиса депозитов", "MS SQL, Always On", shape="cylinder")
    add(d, "new", "notif", 955, 560, 300, 100, "Сервис уведомлений", ".NET 8",
        "формирует и отправляет СМС через шлюз, ведёт журнал отправок")
    # платформа
    add(d, "new", "kafka", 1330, 225, 145, 440, "Kafka", "кластер в двух ЦОД",
        "топики:\ndeposit.application\ndeposit.rates\ndeposit.status\nsms.requested")
    # АБС
    add(d, "new", "adapter", 1565, 255, 430, 115, "Интеграционный адаптер АБС", "Java Spring Boot",
        "читает заявки из Kafka и передаёт в АБС с ограничением скорости; публикует ставки и статусы из таблицы событий")
    add(d, "extended", "oracle", 1565, 430, 430, 150, "БД АБС", "Oracle, PL/SQL",
        "новое: модуль ставок и заявок на депозит, таблица исходящих событий, ролевая модель депозиты / кредиты",
        shape="cylinder")
    add(d, "extended", "delphi", 1565, 650, 430, 100, "Десктоп-клиент АБС", "Delphi",
        "новое: экраны ставок, заявок и согласования особых ставок")
    # внешние
    add(d, "unchanged", "sms", 955, 730, 300, 80, "СМС-шлюз", "поддерживает IT-отдел банка")
    add(d, "external", "tel", 640, 730, 215, 80, "Телеком-оператор", "External System")

    # связи
    d.edge("client", "site", "UC1, UC2")
    d.edge("client", "mono", "UC4, UC5")
    d.edge("site", "gw", "UC1, UC2: REST/JSON")
    d.edge("mono", "gw", "UC4, UC5: REST + токен")
    d.edge("gw", "dsvc", "REST")
    d.edge("dsvc", "dbdep", "SQL")
    d.edge("dsvc", "cc", "UC2")
    d.edge("ccmgr", "cc", "UC3")
    d.edge("dsvc", "kafka", "события", bidir=True)
    d.edge("kafka", "notif", "UC5, UC9")
    d.edge("notif", "sms", "СМС: код и уведомления")
    d.edge("sms", "tel", "отправка СМС")
    d.edge("tel", "client", "СМС клиенту", dashed=True, via=[(130, 770)])
    d.edge("kafka", "adapter", "события", bidir=True)
    d.edge("adapter", "oracle", "PL/SQL, ← таблица событий", bidir=True)
    d.edge("delphi", "oracle", "SQL")
    d.edge("dep", "delphi", "UC6, UC8")
    d.edge("cred", "delphi", "UC7")
    d.edge("mono", "oracle", "", dashed=True, color="#b85450", via=[(410, 190), (1520, 190), (1520, 505)])
    d.edge("mono", "dbib", "SQL")
    legend(d, 20, 960, ["person", "new", "extended", "unchanged", "external"])
    d.line(20, 1005, 70, 1005, dashed=True, color="#b85450", width=2)
    d.text("redn", 80, 993, 1700, 24,
           "Красная пунктирная линия — существующая прямая связь интернет-банка с БД АБС (платежи, текущие счета). В новом процессе депозитов она НЕ используется.",
           size=10, color="#b85450")
    d.save(OUT, "C4_Container")


if __name__ == "__main__":
    context()
    containers()
    print("Task3 диаграммы готовы")
