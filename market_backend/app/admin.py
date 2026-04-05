from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from jose import jwt, JWTError

from app.config import settings
from app.db import AsyncSessionLocal, engine
from app.modules.auth.models import User
from app.modules.products.models import Category, Product
from app.modules.cart.models import Cart, CartItem
from app.modules.orders.models import Order, OrderItem
from app.modules.auth.repos import UserRepo
from app.modules.auth.use_cases import verify_password, create_access_token


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        if not email or not password:
            return False

        async with AsyncSessionLocal() as session:
            repo = UserRepo(session)
            user = await repo.get_by_email(str(email))
            if not user or user.role != "admin":
                return False
            if not verify_password(str(password), user.hashed_password):
                return False
            token = create_access_token(str(user.id), user.role)
            request.session["admin_token"] = token
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")
        if not token:
            return False
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            role = payload.get("role")
            return role == "admin"
        except JWTError:
            return False


# ── Model views ────────────────────────────────────────────────────────────────

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"

    column_list = [User.id, User.email, User.role, User.created_at]
    column_searchable_list = [User.email]
    column_sortable_list = [User.email, User.role, User.created_at]

    form_columns = [User.email, User.role]
    # hashed_password excluded from form — manage via API


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-tags"

    column_list = [Category.id, Category.name]
    column_searchable_list = [Category.name]
    column_sortable_list = [Category.name]

    form_columns = [Category.name]


class ProductAdmin(ModelView, model=Product):
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-box"

    column_list = [Product.id, Product.name, Product.category, Product.price, Product.stock, Product.created_at]
    column_searchable_list = [Product.name]
    column_sortable_list = [Product.name, Product.price, Product.stock, Product.created_at]
    column_details_list = [
        Product.id, Product.name, Product.description,
        Product.category, Product.price, Product.stock,
        Product.image_url, Product.created_at,
    ]

    form_columns = [
        Product.name, Product.description, Product.category,
        Product.price, Product.stock, Product.image_url,
    ]


class OrderAdmin(ModelView, model=Order):
    name = "Заказ"
    name_plural = "Заказы"
    icon = "fa-solid fa-receipt"

    column_list = [Order.id, Order.user, Order.status, Order.total_price, Order.created_at]
    column_sortable_list = [Order.status, Order.total_price, Order.created_at]
    column_details_list = [
        Order.id, Order.user, Order.status,
        Order.total_price, Order.items, Order.created_at,
    ]

    # Admins can change status inline
    form_columns = [Order.status]


class OrderItemAdmin(ModelView, model=OrderItem):
    name = "Позиция заказа"
    name_plural = "Позиции заказов"
    icon = "fa-solid fa-list"

    can_create = False
    can_delete = False

    column_list = [
        OrderItem.id, OrderItem.order_id, OrderItem.product,
        OrderItem.quantity, OrderItem.price_at_order,
    ]
    column_sortable_list = [OrderItem.quantity, OrderItem.price_at_order]

    form_columns = [OrderItem.quantity]


class CartAdmin(ModelView, model=Cart):
    name = "Корзина"
    name_plural = "Корзины"
    icon = "fa-solid fa-cart-shopping"

    can_create = False
    can_delete = False

    column_list = [Cart.id, Cart.user, Cart.created_at]


class CartItemAdmin(ModelView, model=CartItem):
    name = "Позиция корзины"
    name_plural = "Позиции корзин"
    icon = "fa-solid fa-cart-plus"

    can_create = False
    can_delete = False

    column_list = [CartItem.id, CartItem.cart_id, CartItem.product, CartItem.quantity]


def create_admin(app) -> Admin:
    authentication_backend = AdminAuth(secret_key=settings.secret_key)
    admin = Admin(
        app,
        engine,
        title="Market Admin",
        authentication_backend=authentication_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(CartAdmin)
    admin.add_view(CartItemAdmin)

    return admin
