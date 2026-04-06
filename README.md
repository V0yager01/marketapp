# Online Marketplace — Docker Swarm Отказоустойчивый Кластер

Проект реализует веб-приложение онлайн-магазина с автоматическим восстановлением при отказе нод в Docker Swarm кластере.

---

## Содержание

1. [Стек технологий](#стек-технологий)
2. [Требования](#требования)
3. [Структура проекта](#структура-проекта)
4. [Быстрый старт (локально)](#быстрый-старт-локально)
5. [Архитектура стека](#архитектура-стека)
6. [Docker Swarm кластер](#docker-swarm-кластер)
7. [Конфигурация сети](#конфигурация-сети)
8. [Политика размещения реплик](#политика-размещения-реплик)
9. [Тестирование отказоустойчивости](#тестирование-отказоустойчивости)
10. [Демонстрация отказа ноды](#демонстрация-отказа-ноды)
11. [Команды для управления](#команды-для-управления)

---

## Стек технологий

| Компонент    | Технология        | Версия      |
|--------------|-------------------|------------|
| Backend      | FastAPI + Uvicorn | 0.115.0    |
| Frontend     | React + Vite      | 5.1.3      |
| База данных  | PostgreSQL        | 16 Alpine  |
| Оркестрация  | Docker Swarm      | 24+        |
| Сеть         | Overlay (VXLAN)   | встроенная |

---

## Требования

### Для локальной разработки
- Docker Desktop 4.25+ или Docker Engine 24+
- Docker Compose v2
- Git

### Для Docker Swarm кластера
- 2+ ВМ / серверов с Ubuntu 22.04 LTS / Debian 12
- Docker Engine 24+
- Открытые порты между нодами:
  - **2377/tcp** — Swarm management API (только manager)
  - **7946/tcp, 7946/udp** — Node discovery
  - **4789/udp** — Overlay network (VXLAN)
  - **80/tcp** — HTTP (frontend)
  - **22/tcp** — SSH

---

## Структура проекта

```
marketapp/
├── market_backend/
│   ├── app/
│   │   ├── main.py              # FastAPI приложение
│   │   ├── models.py            # SQLAlchemy модели
│   │   ├── schemas.py           # Pydantic схемы
│   │   ├── database.py          # Конфиг БД
│   │   └── static/uploads/      # Хранилище файлов
│   ├── migrations/              # Alembic миграции БД
│   ├── Dockerfile               # Image backend
│   ├── requirements.txt          # Python зависимости
│   └── .env.example             # Переменные окружения
│
├── market_frontend/
│   ├── src/
│   │   ├── App.tsx              # Главный компонент
│   │   ├── components/          # React компоненты
│   │   └── pages/               # Страницы приложения
│   ├── dist/                    # Собранная статика
│   ├── Dockerfile               # Image frontend (nginx)
│   ├── nginx.conf               # Конфиг nginx SPA + proxy
│   ├── package.json             # Node.js зависимости
│   └── vite.config.ts           # Конфиг сборки
│
├── docker-compose.yml           # Для локальной разработки
├── docker-compose.swarm.yml     # Для Docker Swarm
├── .env.example                 # Переменные (копировать в .env)
├── .gitignore
└── README.md                    # Этот файл
```

---

## Быстрый старт (локально)

### 1. Клонирование и настройка

```bash
# Клонировать репозиторий
git clone https://github.com/your-user/marketapp.git
cd marketapp

# Создать .env файл
cp .env.example .env

# Отредактировать .env (опционально)
nano .env
```

### 2. Запуск Docker Compose

```bash
# Собрать и запустить контейнеры
docker compose up --build -d

# Проверить статус
docker compose ps

# Посмотреть логи
docker compose logs -f backend
```

### 3. Проверка работоспособности

```bash
# Frontend
curl http://localhost

# Backend API
curl http://localhost:8000/docs

# API категории
curl http://localhost/api/categories
```

### 4. Остановка

```bash
# Остановить контейнеры
docker compose down

# Остановить и удалить volumes (осторожно!)
docker compose down -v
```

---

## Архитектура стека

### Компоненты и их роли

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                            │
│                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐   │
│  │   Frontend   │     │   Backend    │     │     DB     │   │
│  │   (nginx)    │────▶│   (FastAPI)  │────▶│(PostgreSQL)│   │
│  │   Port 80    │     │  Port 8000   │     │ Port 5432  │   │
│  └──────────────┘     └──────────────┘     └────────────┘   │
│         │                    │                      │         │
│         └────────────────────┼──────────────────────┘         │
│              Bridge Network (app_net)                         │
└─────────────────────────────────────────────────────────────┘
```

### Поток данных

1. **Пользователь** → браузер запрашивает `http://localhost`
2. **Frontend (nginx)** → раздаёт статику React (dist) на порт 80
3. **API запросы** → из JS кода идут на `/api/*`
4. **Nginx proxy** → перенаправляет на `http://backend:8000`
5. **Backend (FastAPI)** → обрабатывает запросы, работает с БД
6. **PostgreSQL** → хранит товары, заказы, пользователей

---

## Docker Swarm кластер

### Схема архитектуры

```
╔═══════════════════════════════════════════════════════════════════╗
║           Docker Swarm Cluster (2 ноды)                          ║
║                                                                   ║
║  ┌──────────────────────────┐  ┌──────────────────────────┐      ║
║  │   manager-1              │  │   worker-1               │      ║
║  │   (Manager / Raft)       │  │   (Worker)               │      ║
║  │                          │  │                          │      ║
║  │ • PostgreSQL (volume)    │  │ • backend (1 реплика)    │      ║
║  │ • backend (1 реплика)    │  │ • frontend (1 реплика)   │      ║
║  │ • frontend (1 реплика)   │  │                          │      ║
║  │                          │  │                          │      ║
║  └───────────────┬──────────┘  └────────────┬─────────────┘      ║
║                  │ 2377/tcp                │                    ║
║                  │ 7946/tcp/udp            │                    ║
║                  │ 4789/udp                │                    ║
║                  └──────────────┬──────────┘                     ║
║               Overlay Network (VXLAN)                            ║
║                    app_net                                       ║
╚═══════════════════════════════════════════════════════════════════╝
```

### IP-адреса примера

| Роль       | Hostname   | IP            | MAC Address        |
|-----------|------------|---------------|--------------------|
| Manager   | manager-1  | 192.168.1.10  | 08:00:27:XX:XX:XX |
| Worker    | worker-1   | 192.168.1.11  | 08:00:27:XX:XX:XX |

---

## Конфигурация сети

### Overlay Network

```yaml
networks:
  app_net:
    driver: overlay        # VXLAN — виртуальная сеть между нодами
    attachable: true       # Возможно подключать контейнеры snapshotted
```

**Особенности:**
- **VXLAN инкапсуляция** — трафик между нодами через VXLAN туннели
- **Service Discovery** — встроенный DNS Swarm резолвит `backend`, `db` по имени сервиса
- **Load Balancing** — встроенный балансировщик в каждом контейнере (embedded DNS load balancer)
- **Ingress Routing Mesh** — входящие запросы на любую ноду маршрутизируются на любую реплику

### Порты публикации

```yaml
services:
  frontend:
    ports:
      - "80:80"           # Swarm routing mesh: 80 на любой ноде → реплика frontend
```

**Ingress Routing Mesh работает так:**
- Клиент подключается к порту 80 на **любой** ноде (даже если frontend там не запущен)
- Swarm автоматически маршрутизирует трафик к любой здоровой реплике frontend
- Достигается высокая доступность без необходимости знать точное расположение контейнера

---

## Политика размещения реплик

### Database (PostgreSQL)

```yaml
db:
  deploy:
    replicas: 1
    placement:
      constraints:
        - node.role == manager    # ✓ ВСЕГДА на менеджере
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 3
```

**Причина:** volume `pg_data` хранит данные на manager-е. При отказе manager-а данные на этой ноде недоступны до восстановления.

> **Лучшая практика для production:** использовать external storage (NFS, CloudStorage) и запускать БД на любой ноде.

### Backend (FastAPI)

```yaml
backend:
  deploy:
    replicas: 2                   # 2 копии приложения (по одной на каждую ноду)
    placement:
      preferences:
        - spread: node.id         # ✓ Распределить по разным нодам
    update_config:
      parallelism: 1              # Обновляем по 1 реплике
      delay: 10s                  # Пауза между обновлениями
      failure_action: rollback    # Откатить при ошибке
    restart_policy:
      condition: on-failure
      delay: 5s
      max_attempts: 5
```

**Стратегия:**
- **spread: node.id** — Swarm scheduler распределяет реплики поровну по нодам (на 2-узловом кластере: по 1 реплике на каждую ноду)
- **parallelism: 1** — rolling update: одна реплика обновляется, остальные обслуживают запросы
- **failure_action: rollback** — если новая версия падает, откатиться на старую

### Frontend (nginx)

```yaml
frontend:
  deploy:
    replicas: 2                   # 2 копии
    placement:
      preferences:
        - spread: node.id         # ✓ Распределить по разным нодам
```

**Расположение реплик при запуске на 2-узловом кластере:**
- Реплика 1 → manager-1
- Реплика 2 → worker-1

---

## Инициализация Docker Swarm

### Шаг 1. На Manager-1

```bash
# SSH на manager-1
ssh user@192.168.1.10

# Инициализировать Swarm
docker swarm init --advertise-addr 192.168.1.10

# Выведет что-то типа:
# Swarm initialized: current node (abc123...) is now a manager.
# 
# To add a worker to this swarm, run the following command:
#
#     docker swarm join --token SWMTKN-1-5e... 192.168.1.10:2377
```

### Шаг 2. На Worker-1

```bash
# SSH на worker-1
ssh user@192.168.1.11

# Присоединить к Swarm
docker swarm join --token SWMTKN-1-5e... 192.168.1.10:2377

# Проверка (выведет "This node joined a swarm as a worker")
```

### Шаг 3. Проверка статуса

```bash
# На manager-1 — список нод
docker node ls

# Результат:
# ID                            HOSTNAME    STATUS    AVAILABILITY   MANAGER STATUS
# abcd1234 *                    manager-1   Ready     Active         Leader
# efgh5678                       worker-1    Ready     Active
```

---

## Развёртывание Swarm Stack

### Подготовка образов

**Вариант A: Docker Registry (рекомендован)**

```bash
# На manager-1: поднять локальный registry
docker service create \
  --name registry \
  --publish 5000:5000 \
  --constraint=node.role==manager \
  registry:2

# Собрать образы и запушить
docker build -t 192.168.1.10:5000/market-backend:latest ./market_backend
docker push 192.168.1.10:5000/market-backend:latest

docker build -t 192.168.1.10:5000/market-frontend:latest ./market_frontend
docker push 192.168.1.10:5000/market-frontend:latest
```

**Вариант B: Build локально на каждой ноде (для курсового проекта)**

```bash
# На каждой ноде (manager-1, worker-1, worker-2)
git clone https://github.com/your-user/marketapp.git /opt/marketapp
cd /opt/marketapp

docker build -t market-backend:latest ./market_backend
docker build -t market-frontend:latest ./market_frontend
```

### Деплой Stack

```bash
# На manager-1
cd /opt/marketapp

# Загрузить переменные окружения
export $(cat .env | xargs)

# Развернуть стек
docker stack deploy -c docker-compose.swarm.yml market

# Проверить развёртывание
docker stack services market

# Результат:
# NAME              MODE       REPLICAS   IMAGE
# market_backend    replicated 3/3        market-backend:latest
# market_db         replicated 1/1        postgres:16-alpine
# market_frontend   replicated 2/2        market-frontend:latest
```

---

## Тестирование отказоустойчивости

### Предварительные проверки

```bash
# На manager-1 — проверить что все сервисы работают
docker stack services market
docker service ps market_backend
docker service ps market_frontend

# Проверить доступность
curl http://192.168.1.10
curl http://192.168.1.10/api/categories

# В браузере открыть http://192.168.1.10 — магазин должен работать
```

### Тестовый сценарий 1: Graceful Drain (корректный вывод ноды)

```bash
# На manager-1 — перевести worker-1 в режим drain
docker node update --availability drain worker-1

# Наблюдать за перемещением контейнеров
watch docker service ps market_backend

# Через 10-30 сек контейнеры на worker-1 перейдут:
# worker-1 → Shutdown → новые поднимутся на manager-1 и worker-2
```

**Ожидаемый результат:**
- Контейнеры gracefully завершают работу
- Новые реплики поднимаются на оставшихся нодах
- Сайт продолжает работать без простоев
- Балансировщик (Ingress routing mesh) перенаправляет трафик

### Тестовый сценарий 2: Жёсткий отказ (имитация сбоя)

```bash
# На manager-1 — просто перелистать ноду
# Способ 1: физическое выключение
ssh user@192.168.1.11 "sudo poweroff"

# Способ 2: в облачной панели выключить VM

# Способ 3: подавить сетевой трафик (для тестирования)
sudo iptables -D INPUT -s 192.168.1.11 -j DROP
```

**Наблюдение (на manager-1):**

```bash
# Через 10-20 сек Swarm заметит, что worker-1 мертв
docker node ls

# Результат:
# ID                HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS
# ...
# efgh5678          worker-1   Down      Active          
# ...

# Сервисы начнут переупаковываться
docker service ps market_backend

# Статус контейнеров:
# ID      NAME              IMAGE   NODE       DESIRED STATE   CURRENT STATE
# xxx     market_backend.1  ...     worker-1   Running         Shutdown
# yyy     market_backend.4  ...     manager-1  Running         Running
# ...
```

### Логирование процесса

```bash
# Смотреть события Swarm в реальном времени
docker events --filter type=service --filter type=container

# Логи конкретного сервиса
docker service logs market_backend -f

# Инспектировать ноду
docker node inspect worker-1 --pretty
```

---

## Демонстрация отказа ноды

### Что выключали

**Сценарий:** Graceful drain worker-1 (или жёсткий сбой VM)

```bash
# Graceful drain
docker node update --availability drain worker-1

# Или жёсткое выключение
# sudo poweroff на worker-1
```

### Что наблюдали

#### Шаг 1: До отказа

```
docker service ps market_backend
ID            NAME          IMAGE    NODE        DESIRED   CURRENT STATE
abc1234       market_backend.1  ...   manager-1   Running   Running
def5678       market_backend.2  ...   worker-1    Running   Running

curl http://192.168.1.10/api/categories
# HTTP 200, категории загружаются за 50-100ms
```

#### Шаг 2: Момент отказа (t=0s)

```bash
# Выключаем worker-1
docker node update --availability drain worker-1
```

#### Шаг 3: Перехвата (t=5-10s)

```
docker service ps market_backend
ID            NAME                IMAGE    NODE        DESIRED   CURRENT STATE
abc1234       market_backend.1    ...      manager-1   Running   Running
def5678       market_backend.2    ...      worker-1    Running   Shutdown ← выходит
ghi9012       market_backend.3    ...      manager-1   Running   Starting ← новая реплика

curl http://192.168.1.10/api/categories
# HTTP 200 — сайт продолжает работать
```

#### Шаг 4: Восстановление (t=20-30s)

```
docker service ps market_backend
ID            NAME             IMAGE    NODE       DESIRED   CURRENT STATE
abc1234       market_backend.1   ...     manager-1  Running   Running
ghi9012       market_backend.3   ...     manager-1  Running   Running ← новая реплика

curl http://192.168.1.10/api/categories
# HTTP 200, latency ~100ms, полная функциональность

# В браузере: http://192.168.1.10 загружается нормально
# Корзина работает, товары загружаются, никакого отката
```

### Таблица событий при отказе

| Время | Событие | Что происходит |
|-------|---------|---------------|
| 0s    | drain worker-1 | Swarm помечает ноду как draining |
| 2-3s  | graceful shutdown | Контейнеры на worker-1 получают SIGTERM |
| 5-10s | scheduler запускается | Swarm запускает новые реплики на оставшихся нодах |
| 10-15s | new replicas starting | Новые контейнеры инициализируются, БД миграции выполняются |
| 15-20s | load balancing | Ingress routing mesh перенаправляет трафик |
| 20-30s | полное восстановление | Все реплики Running, latency вернулась к норме |

### Данные при отказе

**Важно:** Данные **НЕ теряются**:
- PostgreSQL volume (`pg_data`) находится на **manager-1** (constraint в compose)
- При отказе worker-1 данные остаются целы на manager-1
- Новые реплики подключаются к той же БД и получают свежие данные

```bash
# Проверить целостность данных
docker exec <db_container_id> psql -U postgres -d marketdb \
  -c "SELECT COUNT(*) FROM products;"

# Результат: количество товаров не изменилось при отказе
```

---

## Manifest Docker Compose Swarm

### docker-compose.swarm.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-marketdb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-marketdb}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  backend:
    image: market-backend:latest
    # Альтернатива: image: 192.168.1.10:5000/market-backend:latest
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@db:5432/${POSTGRES_DB:-marketdb}
      SECRET_KEY: ${SECRET_KEY:-changeme-secret-key}
    volumes:
      - uploads:/app/app/static/uploads
    networks:
      - app_net
    deploy:
      replicas: 2
      placement:
        preferences:
          - spread: node.id
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5

  frontend:
    image: market-frontend:latest
    # Альтернатива: image: 192.168.1.10:5000/market-frontend:latest
    ports:
      - "80:80"
    networks:
      - app_net
    deploy:
      replicas: 2
      placement:
        preferences:
          - spread: node.id
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5

volumes:
  postgres_data:
  uploads:

networks:
  app_net:
    driver: overlay
    attachable: true
```

---

## Команды для управления

### Статус и мониторинг

```bash
# Список нод в кластере
docker node ls

# Статус всех сервисов в стеке
docker stack services market

# Задачи (контейнеры) конкретного сервиса
docker service ps market_backend
docker service ps market_frontend

# Детальная информация о ноде
docker node inspect manager-1 --pretty

# Логи сервиса
docker service logs market_backend -f
docker service logs market_frontend -f

# События Swarm
docker events --filter type=service --filter type=container
```

### Управление нодами

```bash
# Вывести ноду из ротации (graceful drain)
docker node update --availability drain worker-1

# Вернуть ноду в строй
docker node update --availability active worker-1

# Удалить ноду из кластера (на manager)
docker node rm -f worker-1

# Повысить worker до manager
docker node promote worker-1

# Понизить manager до worker
docker node demote manager-2
```

### Масштабирование и обновление

```bash
# Масштабировать сервис
docker service scale market_backend=5

# Обновить образ (rolling update)
docker service update --image market-backend:v2.0 market_backend

# Проверить статус обновления
watch docker service ps market_backend

# Откатить обновление
docker service rollback market_backend
```

### Управление стеком

```bash
# Развернуть/обновить стек
docker stack deploy -c docker-compose.swarm.yml market

# Удалить стек (volumes остаются)
docker stack rm market

# Список сервисов в стеке
docker stack services market

# Опции сервиса
docker service inspect market_backend --pretty
```

### Отладка и диагностика

```bash
# Внутри контейнера backend
docker exec -it <container_id> bash

# Проверить подключение к БД
docker exec <container_id> psql -U postgres -c "SELECT version();"

# Проверить DNS resolve
docker exec <container_id> ping db

# Размер volume
du -sh /var/lib/docker/volumes/market_postgres_data

# Логи Docker daemon
journalctl -u docker -n 100 -f
```

---

## Заключение

### Ключевые выводы

1. **Отказоустойчивость:** кластер из 2 нод выдерживает отказ worker ноды без потери доступности
2. **Автоматическое восстановление:** Swarm scheduler автоматически перезапускает контейнеры на manager ноде
3. **Rolling updates:** можно обновлять приложение без простоев (по одной реплике за раз)
4. **Высокая доступность:** использование Ingress routing mesh обеспечивает балансировку трафика
5. **Сохранение данных:** database volume на manager-е обеспечивает сохранение данных

### Для защиты проекта

✓ **URL магазина:** `http://<your-swarm-ip>`  
✓ **Репозиторий:** GitHub с кодом + инструкции в README  
✓ **Отчёт по Swarm:**  
  - Схема нод (выше)  
  - Manifest docker-compose.swarm.yml (выше)  
  - Демонстрация отказа: скриншоты `docker service ps` до/во время/после отказа  
  - Проверка доступности: `curl` запросы продолжают работать  
