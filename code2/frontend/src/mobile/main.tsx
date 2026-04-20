import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider } from '../theme/ThemeContext'
import '../theme/global.css'
import { MobileApp } from './MobileApp'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <MobileApp />
    </ThemeProvider>
  </StrictMode>
)
