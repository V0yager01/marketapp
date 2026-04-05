import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { addItem } from '@/api/cart'
import { useAuthStore } from '@/store/authStore'
import { useCartStore } from '@/store/cartStore'
import type { Product } from '@/api/products'
import s from './ProductCard.module.css'

const CATEGORY_ICONS: Record<string, string> = {
  'Электроника': '📱',
  'Одежда': '👗',
  'Дом и сад': '🏠',
  'Спорт': '⚽',
  'Книги': '📚',
  'Красота': '💄',
}

interface Props {
  product: Product
}

export default function ProductCard({ product }: Props) {
  const [added, setAdded] = useState(false)
  const navigate = useNavigate()
  const token = useAuthStore((st) => st.token)
  const increment = useCartStore((st) => st.increment)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => addItem(product.id),
    onSuccess: () => {
      increment()
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setAdded(true)
      setTimeout(() => setAdded(false), 1200)
    },
  })

  const handleAdd = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!token) { navigate('/login'); return }
    mutation.mutate()
  }

  const icon = product.category?.name
    ? (CATEGORY_ICONS[product.category.name] ?? '📦')
    : '📦'

  return (
    <div className={s.card} onClick={() => navigate(`/products/${product.id}`)}>
      <div className={s.imgWrap}>
        <div className={s.imgInner}>
          {product.image_url
            ? <img src={product.image_url} alt={product.name} />
            : icon}
        </div>
      </div>
      <div className={s.body}>
        {product.category && (
          <div className={s.category}>{product.category.name}</div>
        )}
        <div className={s.name}>{product.name}</div>
        {product.description && (
          <div className={s.desc}>{product.description}</div>
        )}
        <div className={s.foot}>
          <div className={s.price}>{Number(product.price).toLocaleString('ru-RU')} ₽</div>
          <button className={s.addBtn} onClick={handleAdd}>
            {added ? '✓' : '+'}
          </button>
        </div>
      </div>
    </div>
  )
}
