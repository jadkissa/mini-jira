import type { ReactNode } from 'react'

export function Dialog({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="overlay">
      <div className="window dialog">
        <div className="titlebar">
          <span>{title}</span>
        </div>
        <div className="client">{children}</div>
      </div>
    </div>
  )
}
