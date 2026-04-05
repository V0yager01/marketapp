import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listOrders } from '@/api/orders'
import { useAuthStore } from '@/store/authStore'
import s from './OrdersPage.module.css'

const STATUS_LABELS: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждён',
  processing: 'Обрабатывается',
  shipped: 'Отправлен',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
}

export default function OrdersPage() {
  const token = useAuthStore((st) => st.token)
  const navigate = useNavigate()

  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: listOrders,
    enabled: !!token,
  })

  if (!token) {
    navigate('/login', { state: { from: '/orders' } })
    return null
  }

  if (isLoading) return <div className={s.loading}>Загрузка...</div>

  const orders = ordersData?.items ?? []

  return (
    <div className={s.page}>
      <div className={s.header}>
        <span className={s.title}>Мои заказы</span>
      </div>

      {orders.length === 0 ? (
        <div className={s.empty}>Заказов пока нет</div>
      ) : (
        <div className={s.list}>
          {orders.map((order) => (
            <Link key={order.id} to={`/orders/${order.id}`} className={s.orderRow}>
              <div className={s.orderId}>#{order.id.slice(0, 8)}</div>
              <div className={s.orderDate}>
                {new Date(order.created_at).toLocaleDateString('ru-RU', {
                  day: 'numeric', month: 'long', year: 'numeric',
                })}
              </div>
              <div className={s.orderTotal}>
                {order.total_price != null
                  ? `${Number(order.total_price).toLocaleString('ru-RU')} ₽`
                  : '—'}
              </div>
              <div className={`${s.status} ${s[order.status] ?? ''}`}>
                {STATUS_LABELS[order.status] ?? order.status}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
