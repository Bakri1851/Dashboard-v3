import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { T } from '../../theme/tokens'

interface Props { children: ReactNode }
interface State { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State { return { error } }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 36, fontFamily: T.fMono, color: T.ink0 }}>
          <div style={{ fontSize: 10.5, letterSpacing: 1.4, textTransform: 'uppercase', color: T.ink3 }}>
            Frontend error
          </div>
          <h2 style={{ fontSize: 20, margin: '6px 0 12px' }}>Something broke</h2>
          <pre style={{ fontSize: 12, whiteSpace: 'pre-wrap', color: T.ink1 }}>
            {this.state.error.message}
            {'\n\n'}
            {this.state.error.stack ?? ''}
          </pre>
          <button
            onClick={() => this.setState({ error: null })}
            style={{
              marginTop: 16, padding: '6px 12px',
              border: `1px solid ${T.border}`, color: T.ink1,
              fontFamily: T.fMono, fontSize: 11,
            }}
          >
            reset
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
