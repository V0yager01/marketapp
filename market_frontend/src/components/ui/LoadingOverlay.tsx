import { useLoadingStore } from '@/store/loadingStore'
import s from './LoadingOverlay.module.css'

export default function LoadingOverlay() {
  const count = useLoadingStore((st) => st.count)
  const visible = count > 0

  return (
    <div className={`${s.overlay}${visible ? ' ' + s.visible : ''}`}>
      <div className={s.blur} />
      <div className={s.spinner} />
    </div>
  )
}
