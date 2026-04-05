import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listCategories, listProducts } from '@/api/products'
import ProductCard from '@/components/product/ProductCard'
import s from './CatalogPage.module.css'

const LIMIT = 12

export default function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchInput, setSearchInput] = useState(searchParams.get('search') ?? '')
  const [page, setPage] = useState(0)

  const categoryId = searchParams.get('category_id')
    ? Number(searchParams.get('category_id'))
    : undefined
  const search = searchParams.get('search') ?? undefined

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: listCategories,
  })

  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products', categoryId, search, page],
    queryFn: () =>
      listProducts({ category_id: categoryId, search, offset: page * LIMIT, limit: LIMIT }),
  })

  const products = productsData?.items ?? []
  const hasMore = products.length === LIMIT

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(0)
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (searchInput.trim()) next.set('search', searchInput.trim())
      else next.delete('search')
      return next
    })
  }

  const selectCategory = (id?: number) => {
    setPage(0)
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (id) next.set('category_id', String(id))
      else next.delete('category_id')
      return next
    })
  }

  return (
    <div className={s.page}>
      <div className={s.header}>
        <span className={s.title}>Каталог</span>
        <form className={s.searchBar} onSubmit={handleSearch}>
          <input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Поиск..."
          />
          <button type="submit">⌕</button>
        </form>
      </div>

      <div className={s.layout}>
        <aside className={s.sidebar}>
          <div className={s.sidebarTitle}>Категории</div>
          <ul className={s.catList}>
            <li
              className={!categoryId ? s.active : ''}
              onClick={() => selectCategory(undefined)}
            >
              Все товары
            </li>
            {(categories ?? []).map((cat) => (
              <li
                key={cat.id}
                className={categoryId === cat.id ? s.active : ''}
                onClick={() => selectCategory(cat.id)}
              >
                {cat.name}
              </li>
            ))}
          </ul>
        </aside>

        <div>
          <div className={s.grid}>
            {isLoading && <div className={s.loading}>Загрузка...</div>}
            {!isLoading && products.length === 0 && (
              <div className={s.empty}>Ничего не найдено</div>
            )}
            {products.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>

          {(page > 0 || hasMore) && (
            <div className={s.pagination}>
              <button
                className={s.pageBtn}
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 0}
              >
                ←
              </button>
              <button className={`${s.pageBtn} ${s.active}`}>{page + 1}</button>
              <button
                className={s.pageBtn}
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasMore}
              >
                →
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
