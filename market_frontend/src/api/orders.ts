import client from './client'

export interface OrderItem {
  id: string
  product_id: string
  quantity: number
  price_at_order: number
}

export interface Order {
  id: string
  user_id: string
  status: string
  total_price: number | null
  created_at: string
  items: OrderItem[]
}

export interface OrderListResponse {
  items: Order[]
  total: number
  offset: number
  limit: number
}

export const createOrder = () =>
  client.post<Order>('/orders').then((r) => r.data)

export const listOrders = () =>
  client.get<OrderListResponse>('/orders').then((r) => r.data)

export const getOrder = (id: string) =>
  client.get<Order>(`/orders/${id}`).then((r) => r.data)

export const cancelOrder = (id: string) =>
  client.patch<Order>(`/orders/${id}/cancel`).then((r) => r.data)
