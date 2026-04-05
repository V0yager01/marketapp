import { useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProduct } from '@/api/products'
import { addItem } from '@/api/cart'
import { useAuthStore } from '@/store/authStore'
import { useCartStore } from '@/store/cartStore'
import s from './ProductPage.module.css'

export default function ProductPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const token = useAuthStore((st) => st.token)
  const increment = useCartStore((st) => st.increment)
  const queryClient = useQueryClient()
  const [inCart, setInCart] = useState(false)

  const { data: product, isLoading, isError } = useQuery({
    queryKey: ['product', id],
    queryFn: () => getProduct(id!),
    enabled: !!id,
  })

  const mutation = useMutation({
    mutationFn: () => addItem(id!),
    onSuccess: () => {
      increment()
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setInCart(true)
    },
  })

  const handleAdd = () => {
    if (!token) { navigate('/login'); return }
    if (inCart) { navigate('/cart'); return }
    mutation.mutate()
  }

  if (isLoading) return <div className={s.loading}>Загрузка...</div>
  if (isError || !product) return <div className={s.error}>Товар не найден</div>

  return (
    <div className={s.page}>
      <div className={s.breadcrumb}>
        <Link to="/">Главная</Link>
        <span>/</span>
        <Link to="/catalog">Каталог</Link>
        {product.category && (
          <>
            <span>/</span>
            <Link to={`/catalog?category_id=${product.category.id}`}>{product.category.name}</Link>
          </>
        )}
        <span>/</span>
        <span>{product.name}</span>
      </div>

      <div className={s.layout}>
        <div className={s.imgWrap}>
          {product.image_url
            ? <img src={product.image_url} alt={product.name} />
            : '📦'}
        </div>

        <div className={s.info}>
          {product.category && (
            <div className={s.category}>{product.category.name}</div>
          )}
          <div className={s.name}>{product.name}</div>
          {product.description && (
            <div className={s.desc}>{product.description}</div>
          )}
          <div className={s.price}>{Number(product.price).toLocaleString('ru-RU')} ₽</div>
          <div className={`${s.stock}${product.stock > 0 ? ' ' + s.inStock : ''}`}>
            {product.stock > 0 ? `В наличии: ${product.stock} шт.` : 'Нет в наличии'}
          </div>
          <button
            className={`${s.addBtn}${inCart ? ' ' + s.inCart : ''}`}
            onClick={handleAdd}
            disabled={product.stock === 0}
          >
            {inCart ? '✓ Уже в корзине — перейти' : 'В корзину'}
          </button>
        </div>
      </div>
    </div>
  )
}
