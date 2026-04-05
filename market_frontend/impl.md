# Реализация фронтенда MARKET

## Стек
- **Vite 5** + **React 18** + **TypeScript**
- **React Router v6** — клиентская маршрутизация
- **Zustand** — глобальное состояние (токен авторизации, счётчик корзины)
- **TanStack Query** — запросы к API, кэш, автоинвалидация
- **Axios** — HTTP-клиент с интерцептором Bearer-токена
- **CSS Modules** — стилизация по дизайну concept3 (black & white, sharp corners)

## Что реализовано

### API-слой (`src/api/`)
- `client.ts` — axios с baseURL `/api` и интерцептором `Authorization: Bearer`
- `auth.ts` — `register()`, `login()`
- `products.ts` — `listProducts()`, `getProduct()`, `listCategories()`
- `cart.ts` — `getCart()`, `addItem()`, `updateItem()`, `removeItem()`, `clearCart()`
- `orders.ts` — `createOrder()`, `listOrders()`, `getOrder()`, `cancelOrder()`

### Хранилища (`src/store/`)
- `authStore.ts` — токен в `localStorage`, метод `logout()`
- `cartStore.ts` — счётчик позиций в навбаре

### Компоненты (`src/components/`)
- `layout/Nav.tsx` — sticky навбар: лого, ссылки, поиск (переход в каталог), кнопки вход/выход/заказы, иконка корзины с badge
- `layout/Footer.tsx` — ссылки, копирайт
- `ui/Marquee.tsx` — бегущая строка с CSS-анимацией (дублирование для seamless loop)
- `product/ProductCard.tsx` — карточка товара с кнопкой «+», hover-эффект, клик → страница товара
- `ProtectedRoute.tsx` — редирект на `/login` с сохранением `returnTo`

### Страницы (`src/pages/`)
| Страница | Маршрут | Описание |
|----------|---------|----------|
| `HomePage` | `/` | Hero, Marquee, сетка категорий (API), фильтр-табы + 4 карточки товаров, блок фич |
| `CatalogPage` | `/catalog` | Сайдбар с категориями, поиск, пагинация offset/limit |
| `ProductPage` | `/products/:id` | Фото/эмодзи, название, описание, цена, наличие, кнопка «В корзину» |
| `CartPage` | `/cart` | Список с +/− / удалить / очистить, итого, кнопка «Оформить заказ» → POST `/orders` |
| `LoginPage` | `/login` | Форма входа, токен → authStore, редирект на `returnTo` |
| `RegisterPage` | `/register` | Форма регистрации (username, email, password) |
| `OrdersPage` | `/orders` | Таблица заказов (id, дата, сумма, статус) |
| `OrderDetailPage` | `/orders/:id` | Позиции заказа, итого, кнопка «Отменить» (если статус позволяет) |

### Инфраструктура
- `vite.config.ts` — proxy `/api → http://127.0.0.1:8000`, alias `@` → `src`
- `tsconfig.app.json` — paths `@/*`
- `Dockerfile` — multi-stage: node build → nginx serve
- `nginx.conf` — SPA fallback + proxy `/api/` → backend

## Запуск
```bash
cd market_frontend
npm run dev      # dev-сервер http://localhost:5173
npm run build    # production build в dist/
```
