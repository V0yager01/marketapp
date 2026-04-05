import { Link } from 'react-router-dom'
import s from './Footer.module.css'

export default function Footer() {
  return (
    <footer className={s.footer}>
      <Link to="/" className={s.logo}>MARKET</Link>
      <Link to="/catalog">Каталог</Link>
      <Link to="/catalog">Доставка</Link>
      <Link to="/catalog">Возврат</Link>
      <Link to="/catalog">О нас</Link>
      <Link to="/catalog">Контакты</Link>
      <span className={s.copy}>© 2026 Market</span>
    </footer>
  )
}
