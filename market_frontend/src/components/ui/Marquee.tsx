import s from './Marquee.module.css'

const items = [
  { text: 'Бесплатная доставка от 2 000 ₽', accent: true },
  { text: 'Возврат 30 дней', accent: false },
  { text: 'Новинки каждую неделю', accent: true },
  { text: 'Безопасная оплата', accent: false },
  { text: 'Поддержка 24/7', accent: true },
  { text: 'Оригинальные товары', accent: false },
]

const doubled = [...items, ...items]

export default function Marquee() {
  return (
    <div className={s.wrap}>
      <div className={s.track}>
        {doubled.map((item, i) => (
          <span key={i} className={`${s.item}${item.accent ? ' ' + s.accent : ''}`}>
            {item.text}
          </span>
        ))}
      </div>
    </div>
  )
}
