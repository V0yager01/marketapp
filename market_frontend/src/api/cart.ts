import client from './client'

export interface CartItem {
  id: string // UUID
  product_id: string // UUID
  quantity: number
}

export interface Cart {
  id: string
  user_id: string
  items: CartItem[]
}

export const getCart = () =>
  client.get<Cart>('/cart').then((r) => r.data)

export const addItem = (product_id: string, quantity = 1) =>
  client.post<CartItem>('/cart/items', { product_id, quantity }).then((r) => r.data)

export const updateItem = (product_id: string, quantity: number) =>
  client.put<CartItem>(`/cart/items/${product_id}`, { product_id, quantity }).then((r) => r.data)

export const removeItem = (product_id: string) =>
  client.delete(`/cart/items/${product_id}`)

export const clearCart = () =>
  client.delete('/cart')
