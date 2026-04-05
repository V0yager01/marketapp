from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import engine, Base

# Import all models so SQLAlchemy registers them before create_all
import app.modules.auth.models  # noqa: F401
import app.modules.products.models  # noqa: F401
import app.modules.cart.models  # noqa: F401
import app.modules.orders.models  # noqa: F401

from app.modules.auth.router import router as auth_router
from app.modules.products.router import router as products_router
from app.modules.cart.router import router as cart_router
from app.modules.orders.router import router as orders_router
from app.modules.users.router import router as users_router
from app.admin import create_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Market API", lifespan=lifespan)


# SessionMiddleware must come before Admin (sqladmin uses sessions for auth)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(products_router, tags=["products"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(orders_router, tags=["orders"])
app.include_router(users_router, tags=["users"])

create_admin(app)
