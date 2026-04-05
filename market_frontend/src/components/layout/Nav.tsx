import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { useCartStore } from '@/store/cartStore'
import s from './Nav.module.css'

export default function Nav() {
  const [search, setSearch] = useState('')
  const navigate = useNavigate()
  const token = useAuthStore((st) => st.token)
  const logout = useAuthStore((st) => st.logout)
  const cartCount = useCartStore((st) => st.count)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (search.trim()) navigate(`/catalog?search=${encodeURIComponent(search.trim())}`)
  }

  return (
    <nav className={s.nav}>
      <NavLink to="/" className={s.logo}>MARKET</NavLink>
      <div className={s.navLinks}>
        <NavLink to="/catalog" className={({ isActive }) => isActive ? s.active : ''}>
          Каталог
        </NavLink>
        <NavLink to="/catalog?sort=new" className={({ isActive }) => isActive ? s.active : ''}>
          Новинки
        </NavLink>
        <NavLink to="/catalog?sort=discount" className={({ isActive }) => isActive ? s.active : ''}>
          Акции
        </NavLink>
      </div>
      <div className={s.spacer} />
      <form className={s.search} onSubmit={handleSearch}>
        <input
          placeholder="Поиск товаров..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button type="submit" className={s.searchBtn}>⌕</button>
      </form>
      <div className={s.navRight}>
        {token ? (
          <>
            <NavLink to="/orders">
              <button className={s.btnGhost}>Заказы</button>
            </NavLink>
            <button className={s.userBtn} onClick={() => { logout(); navigate('/') }}>
              Выйти
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">
              <button className={s.btnGhost}>Войти</button>
            </NavLink>
            <NavLink to="/register">
              <button className={s.btnSolid}>Регистрация</button>
            </NavLink>
          </>
        )}
        <NavLink to="/cart">
          <button className={s.cartBtn}>
            🛒
            {cartCount > 0 && <span className={s.cartNum}>{cartCount}</span>}
          </button>
        </NavLink>
      </div>
    </nav>
  )
}
