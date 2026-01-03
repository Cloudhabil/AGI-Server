import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & { tone?: 'default' | 'primary' | 'danger' | 'ghost'; size?: 'sm' | 'md' }

export default function Button({ tone = 'default', size = 'sm', className = '', ...rest }: Props) {
  const tones: Record<string, string> = {
    default: 'border bg-white hover:bg-slate-50 text-slate-900',
    primary: 'bg-black text-white hover:bg-slate-800 border border-black',
    danger: 'bg-red-600 text-white hover:bg-red-700 border border-red-700',
    ghost: 'border border-slate-300 bg-transparent hover:bg-slate-50',
  }
  const sizes: Record<string, string> = { sm: 'px-2 py-1 text-xs rounded-md', md: 'px-3 py-1.5 text-sm rounded-lg' }
  return <button className={`${sizes[size]} ${tones[tone]} ${className}`} {...rest} />
}

