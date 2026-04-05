import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listCategories, listProducts } from '@/api/products'
import Marquee from '@/components/ui/Marquee'
import ProductCard from '@/components/product/ProductCard'
import s from './HomePage.module.css'

const CATEGORY_ICONS: Record<string, string> = {
  'Электроника': '📱',
  'Одежда': '👗',
  'Дом и сад': '🏠',
  'Спорт': '⚽',
  'Книги': '📚',
  'Красота': '💄',
}

type Tab = 'popular' | 'new' | 'discount'

export default function HomePage() {
  const [tab, setTab] = useState<Tab>('popular')
  const navigate = useNavigate()

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: listCategories,
  })

  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products', 'home', tab],
    queryFn: () => listProducts({ limit: 8 }),
  })

  const products = productsData?.items ?? []

  return (
    <>
      {/* HERO */}
      <div className={s.hero}>
        <div className={s.heroMain}>
          <div>
            <div className={s.kicker}>Весна — Лето 2026</div>
            <div className={s.h1}>
              НОВЫЕ<br />
              <span className={s.outline}>СТИЛИ</span><br />
              ЖДУТ ВАС
            </div>
            <div className={s.line} />
            <div className={s.desc}>
              Тысячи товаров в одном месте. Минимум лишнего — максимум удобства.
              Быстрый поиск, честные цены, доставка за 24 часа.
            </div>
            <div className={s.actions}>
              <button className={s.btnWhite} onClick={() => navigate('/catalog')}>
                Смотреть каталог
              </button>
              <button className={s.btnOutline} onClick={() => navigate('/catalog')}>
                Новинки →
              </button>
            </div>
          </div>
          <div className={s.meta}>
            <div><div className={s.metaVal}>12K+</div><div className={s.metaLabel}>Товаров</div></div>
            <div><div className={s.metaVal}>4.9</div><div className={s.metaLabel}>Рейтинг</div></div>
            <div><div className={s.metaVal}>24ч</div><div className={s.metaLabel}>Доставка</div></div>
            <div><div className={s.metaVal}>30д</div><div className={s.metaLabel}>Возврат</div></div>
          </div>
        </div>
        <div className={s.heroSide}>
          <div className={s.tile} onClick={() => navigate('/catalog')}>
            <div className={s.tileNum}>01</div>
            <div className={s.tileLabel}>Горячая акция</div>
            <div className={s.tileTitle}>Электроника<br />до −40%</div>
            <div className={s.tileArrow}>→</div>
          </div>
          <div className={s.tile} onClick={() => navigate('/catalog')}>
            <div className={s.tileNum}>02</div>
            <div className={s.tileLabel}>Новая коллекция</div>
            <div className={s.tileTitle}>Весенняя<br />одежда 2026</div>
            <div className={s.tileArrow}>→</div>
          </div>
        </div>
      </div>

      {/* MARQUEE */}
      <Marquee />

      {/* CATEGORIES */}
      <div className={s.section}>
        <div className={s.sectionHead}>
          <span className={s.sectionNum}>01</span>
          <span className={s.sectionTitle}>Категории</span>
          <Link to="/catalog" className={s.sectionMore}>Все категории</Link>
        </div>
        <div className={s.catGrid}>
          {(categories ?? []).map((cat) => (
            <div
              key={cat.id}
              className={s.catItem}
              onClick={() => navigate(`/catalog?category_id=${cat.id}`)}
            >
              <div className={s.catIconWrap}>
                {CATEGORY_ICONS[cat.name] ?? '📦'}
              </div>
              <div className={s.catName}>{cat.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* PRODUCTS */}
      <div className={s.section} style={{ marginBottom: 0 }}>
        <div className={s.sectionHead}>
          <span className={s.sectionNum}>02</span>
          <span className={s.sectionTitle}>Товары</span>
          <Link to="/catalog" className={s.sectionMore}>Смотреть все</Link>
        </div>
        <div className={s.filterTabs}>
          {(['popular', 'new', 'discount'] as Tab[]).map((t) => (
            <div
              key={t}
              className={`${s.tab}${tab === t ? ' ' + s.active : ''}`}
              onClick={() => setTab(t)}
            >
              {t === 'popular' ? 'Популярное' : t === 'new' ? 'Новинки' : 'Со скидкой'}
            </div>
          ))}
        </div>
        {isLoading ? (
          <div className={s.loading}>Загрузка...</div>
        ) : (
          <div className={s.productGrid}>
            {products.slice(0, 4).map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </div>

      {/* FEATURES */}
      <div className={s.features}>
        {[
          { icon: '✈', title: 'Быстрая доставка', text: 'Бесплатно от 2 000 ₽. Доставим за 24 часа.' },
          { icon: '↩', title: 'Возврат 30 дней', text: 'Вернём деньги без лишних вопросов.' },
          { icon: '✻', title: 'Оригинальные товары', text: 'Работаем только с проверенными поставщиками.' },
          { icon: '⦿', title: 'Поддержка 24/7', text: 'Чат, телефон, email — всегда на связи.' },
        ].map((f) => (
          <div key={f.title} className={s.feature}>
            <div className={s.featureIcon}>{f.icon}</div>
            <div className={s.featureTitle}>{f.title}</div>
            <div className={s.featureText}>{f.text}</div>
          </div>
        ))}
      </div>
    </>
  )
}
