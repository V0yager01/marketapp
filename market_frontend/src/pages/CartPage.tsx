import { useNavigate, Link } from 'react-router-dom'
import { useQuery, useQueries, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCart, updateItem, removeItem, clearCart } from '@/api/cart'
import { getProduct } from '@/api/products'
import { createOrder } from '@/api/orders'
import { useAuthStore } from '@/store/authStore'
import { useCartStore } from '@/store/cartStore'
import s from './CartPage.module.css'

export default function CartPage() {
  const navigate = useNavigate()
  const token = useAuthStore((st) => st.token)
  const setCount = useCartStore((st) => st.setCount)
  const queryClient = useQueryClient()

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: getCart,
    enabled: !!token,
  })

  // Fetch product details for each cart item
  const productQueries = useQueries({
    queries: (cart?.items ?? []).map((item) => ({
      queryKey: ['product', item.product_id],
      queryFn: () => getProduct(item.product_id),
      enabled: !!cart,
    })),
  })

  const productMap = Object.fromEntries(
    productQueries
      .filter((q) => q.data)
      .map((q) => [q.data!.id, q.data!])
  )

  const enrichedItems = (cart?.items ?? []).map((item) => ({
    ...item,
    product: productMap[item.product_id] ?? null,
  }))

  const total = enrichedItems.reduce((sum, item) => {
    return sum + (item.product ? Number(item.product.price) * item.quantity : 0)
  }, 0)

  const updateMutation = useMutation({
    mutationFn: ({ product_id, quantity }: { product_id: string; quantity: number }) =>
      updateItem(product_id, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    },
  })

  const removeMutation = useMutation({
    mutationFn: (product_id: string) => removeItem(product_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setCount(Math.max(0, (cart?.items.length ?? 1) - 1))
    },
  })

  const clearMutation = useMutation({
    mutationFn: clearCart,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setCount(0)
    },
  })

  const orderMutation = useMutation({
    mutationFn: createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      setCount(0)
      navigate('/orders')
    },
  })

  if (!token) {
    return (
      <div className={s.page}>
        <div className={s.empty}>
          <div className={s.emptyText}>Войдите, чтобы увидеть корзину</div>
          <button className={s.goBtn} onClick={() => navigate('/login')}>Войти</button>
        </div>
      </div>
    )
  }

  if (isLoading) return <div className={s.loading}>Загрузка...</div>

  if (!cart || cart.items.length === 0) {
    return (
      <div className={s.page}>
        <div className={s.header}>
          <span className={s.title}>Корзина</span>
        </div>
        <div className={s.empty}>
          <div className={s.emptyText}>Корзина пуста</div>
          <button className={s.goBtn} onClick={() => navigate('/catalog')}>В каталог</button>
        </div>
      </div>
    )
  }

  return (
    <div className={s.page}>
      <div className={s.header}>
        <span className={s.title}>Корзина</span>
        <button
          className={s.clearBtn}
          style={{ marginLeft: 'auto' }}
          onClick={() => clearMutation.mutate()}
        >
          Очистить
        </button>
      </div>

      <div className={s.items}>
        {enrichedItems.map((item) => (
          <div key={item.product_id} className={s.item}>
            <div className={s.itemImg}>
              {item.product?.image_url
                ? <img src={item.product.image_url} alt={item.product.name} />
                : '📦'}
            </div>
            <div>
              <div className={s.itemName}>
                {item.product
                  ? <Link to={`/products/${item.product_id}`}>{item.product.name}</Link>
                  : item.product_id}
              </div>
              {item.product && (
                <div className={s.itemPrice}>
                  {Number(item.product.price).toLocaleString('ru-RU')} ₽ × {item.quantity}
                </div>
              )}
            </div>
            <div className={s.qty}>
              <button
                className={s.qtyBtn}
                onClick={() => {
                  if (item.quantity <= 1) removeMutation.mutate(item.product_id)
                  else updateMutation.mutate({ product_id: item.product_id, quantity: item.quantity - 1 })
                }}
              >−</button>
              <div className={s.qtyVal}>{item.quantity}</div>
              <button
                className={s.qtyBtn}
                onClick={() => updateMutation.mutate({ product_id: item.product_id, quantity: item.quantity + 1 })}
                disabled={item.product ? item.quantity >= item.product.stock : false}
              >+</button>
            </div>
            <button className={s.removeBtn} onClick={() => removeMutation.mutate(item.product_id)}>×</button>
          </div>
        ))}
      </div>

      <div className={s.foot}>
        <div>
          <div className={s.totalLabel}>Итого</div>
          <div className={s.total}>{total.toLocaleString('ru-RU')} ₽</div>
        </div>
        <button
          className={s.orderBtn}
          onClick={() => orderMutation.mutate()}
          disabled={orderMutation.isPending}
        >
          {orderMutation.isPending ? 'Оформляем...' : 'Оформить заказ'}
        </button>
      </div>
    </div>
  )
}
