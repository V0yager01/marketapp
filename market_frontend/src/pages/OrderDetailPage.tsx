import { Link, useParams } from 'react-router-dom'
import { useQuery, useQueries, useMutation, useQueryClient } from '@tanstack/react-query'
import { getOrder, cancelOrder } from '@/api/orders'
import { getProduct } from '@/api/products'
import s from './OrderDetailPage.module.css'

const STATUS_LABELS: Record<string, string> = {
  pending: 'Ожидает',
  confirmed: 'Подтверждён',
  processing: 'Обрабатывается',
  shipped: 'Отправлен',
  delivered: 'Доставлен',
  cancelled: 'Отменён',
}

const CANCELLABLE = ['pending', 'confirmed']

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data: order, isLoading } = useQuery({
    queryKey: ['order', id],
    queryFn: () => getOrder(id!),
    enabled: !!id,
  })

  // Fetch product details for each order item
  const productQueries = useQueries({
    queries: (order?.items ?? []).map((item) => ({
      queryKey: ['product', item.product_id],
      queryFn: () => getProduct(item.product_id),
      enabled: !!order,
    })),
  })

  const productMap = Object.fromEntries(
    productQueries.filter((q) => q.data).map((q) => [q.data!.id, q.data!])
  )

  const cancelMutation = useMutation({
    mutationFn: () => cancelOrder(id!),
    onSuccess: (data) => {
      queryClient.setQueryData(['order', id], data)
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    },
  })

  if (isLoading) return <div className={s.loading}>Загрузка...</div>
  if (!order) return <div className={s.loading}>Заказ не найден</div>

  return (
    <div className={s.page}>
      <div className={s.header}>
        <Link to="/orders" className={s.back}>← Назад</Link>
        <span className={s.title}>Заказ #{order.id.slice(0, 8)}</span>
        <div className={`${s.status} ${s[order.status] ?? ''}`}>
          {STATUS_LABELS[order.status] ?? order.status}
        </div>
      </div>

      <div className={s.items}>
        {order.items.map((item) => {
          const product = productMap[item.product_id]
          return (
            <div key={item.id} className={s.item}>
              <div className={s.itemImg}>
                {product?.image_url
                  ? <img src={product.image_url} alt={product.name} />
                  : '📦'}
              </div>
              <div>
                {product ? (
                  <Link to={`/products/${item.product_id}`} className={s.itemName}>
                    {product.name}
                  </Link>
                ) : (
                  <div className={s.itemName}>{item.product_id.slice(0, 8)}...</div>
                )}
                <div className={s.itemQty}>
                  {item.quantity} шт. × {Number(item.price_at_order).toLocaleString('ru-RU')} ₽
                </div>
              </div>
              <div className={s.itemPrice}>
                {(item.quantity * Number(item.price_at_order)).toLocaleString('ru-RU')} ₽
              </div>
            </div>
          )
        })}
      </div>

      <div className={s.foot}>
        <div>
          <div className={s.totalLabel}>Итого</div>
          <div className={s.total}>
            {order.total_price != null
              ? `${Number(order.total_price).toLocaleString('ru-RU')} ₽`
              : '—'}
          </div>
        </div>
        {CANCELLABLE.includes(order.status) && (
          <button
            className={s.cancelBtn}
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
          >
            {cancelMutation.isPending ? 'Отменяем...' : 'Отменить заказ'}
          </button>
        )}
      </div>
    </div>
  )
}
