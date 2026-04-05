import client from './client'

export interface Category {
  id: number
  name: string
}

export interface Product {
  id: string // UUID
  name: string
  description: string | null
  price: number
  stock: number
  image_url: string | null
  category: Category | null
}

export interface ProductListResponse {
  items: Product[]
  total: number
  offset: number
  limit: number
}

export interface ProductsParams {
  category_id?: number
  search?: string
  offset?: number
  limit?: number
}

export const listCategories = () =>
  client.get<Category[]>('/categories').then((r) => r.data)

export const listProducts = (params?: ProductsParams) =>
  client.get<ProductListResponse>('/products', { params }).then((r) => r.data)

export const getProduct = (id: string) =>
  client.get<Product>(`/products/${id}`).then((r) => r.data)
