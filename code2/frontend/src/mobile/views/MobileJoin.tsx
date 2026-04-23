import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { stagger, fadeUp } from '../../animation/motion'

interface Props {
  name: string
  code: string
  error: string | null
  notice: string | null
  busy: boolean
  onNameChange: (v: string) => void
  onCodeChange: (v: string) => void
  onJoin: () => void
}

export function MobileJoin({
  name,
  code,
  error,
  notice,
  busy,
  onNameChange,
  onCodeChange,
  onJoin,
}: Props) {
  const [focus, setFocus] = useState<'name' | 'code' | null>(null)
  const codeChars = Array.from({ length: 6 }, (_, i) => code[i] ?? '')

  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '30px 22px' }}
    >
      <motion.div variants={fadeUp} style={{ textAlign: 'center' }}>
        <div
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          Lab Assistant
        </div>
        <div
          style={{
            fontFamily: T.fSerif,
            fontSize: 30,
            color: T.ink,
            marginTop: 6,
            lineHeight: 1,
            letterSpacing: 0.2,
          }}
        >
          Join Session
        </div>
      </motion.div>

      <motion.div
        variants={fadeUp}
        style={{ marginTop: 24, height: 1, background: T.line, transformOrigin: 'center' }}
      />

      <AnimatePresence initial={false}>
        {notice && (
          <motion.div
            key="notice"
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            style={{
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                padding: '10px 12px',
                background: T.accentSoft,
                border: `1px solid ${T.accent}`,
                fontFamily: T.fMono,
                fontSize: 10.5,
                color: T.ink2,
                lineHeight: 1.5,
              }}
            >
              {notice}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div variants={fadeUp} style={{ marginTop: 20 }}>
        <label
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
          }}
        >
          Your Name
        </label>
        <motion.input
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          onFocus={() => setFocus('name')}
          onBlur={() => setFocus(null)}
          placeholder="e.g. Alice"
          maxLength={40}
          animate={{ borderColor: focus === 'name' ? T.accent : T.line2 }}
          transition={{ duration: 0.2 }}
          style={{
            marginTop: 6,
            width: '100%',
            padding: '11px 12px',
            background: T.card,
            color: T.ink,
            border: `1px solid ${T.line2}`,
            fontFamily: T.fSans,
            fontSize: 14,
            borderRadius: 0,
            outline: 'none',
          }}
        />
      </motion.div>

      <motion.div variants={fadeUp} style={{ marginTop: 16 }}>
        <label
          style={{
            fontFamily: T.fMono,
            fontSize: 10,
            color: T.ink3,
            letterSpacing: 1.3,
            textTransform: 'uppercase',
          }}
        >
          Session Code
        </label>
        <motion.input
          value={code}
          onChange={(e) => onCodeChange(e.target.value.toUpperCase().slice(0, 6))}
          onFocus={() => setFocus('code')}
          onBlur={() => setFocus(null)}
          placeholder="A3X7K2"
          maxLength={6}
          autoCapitalize="characters"
          autoCorrect="off"
          spellCheck={false}
          animate={{ borderColor: focus === 'code' ? T.accent : T.line2 }}
          transition={{ duration: 0.2 }}
          style={{
            marginTop: 6,
            width: '100%',
            padding: '11px 12px',
            background: T.card,
            color: T.ink,
            border: `1px solid ${T.line2}`,
            fontFamily: T.fMono,
            fontSize: 22,
            letterSpacing: 8,
            borderRadius: 0,
            outline: 'none',
            textAlign: 'center',
          }}
        />
        {/* Character slot preview — lights up as user types */}
        <div
          style={{
            marginTop: 8,
            display: 'flex',
            gap: 4,
            justifyContent: 'center',
          }}
        >
          {codeChars.map((ch, i) => (
            <motion.div
              key={i}
              animate={{
                borderColor: ch ? T.accent : T.line2,
                color: ch ? T.accent : T.ink3,
                scale: ch ? 1 : 0.9,
              }}
              transition={{ type: 'spring', stiffness: 400, damping: 28 }}
              style={{
                width: 8,
                height: 2,
                borderBottom: `2px solid ${T.line2}`,
              }}
            />
          ))}
        </div>
        <div
          style={{
            marginTop: 6,
            fontFamily: T.fMono,
            fontSize: 9.5,
            color: T.ink3,
            letterSpacing: 0.5,
            textAlign: 'center',
          }}
        >
          6 characters · provided by instructor
        </div>
      </motion.div>

      <AnimatePresence initial={false}>
        {error && (
          <motion.div
            key="error"
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: 'auto', marginTop: 14 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            transition={{ duration: 0.22 }}
            style={{ overflow: 'hidden' }}
          >
            <motion.div
              initial={{ x: 0 }}
              animate={{ x: [0, -4, 4, -3, 3, 0] }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              style={{
                padding: '8px 10px',
                background: T.bg2,
                border: `1px solid ${T.danger}`,
                fontFamily: T.fMono,
                fontSize: 10.5,
                color: T.danger,
              }}
            >
              ⚠ {error}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        variants={fadeUp}
        onClick={onJoin}
        disabled={busy}
        whileHover={busy ? undefined : { filter: 'brightness(1.15)' }}
        whileTap={busy ? undefined : { scale: 0.97 }}
        style={{
          marginTop: 22,
          width: '100%',
          padding: '12px 0',
          background: T.ink,
          color: T.bg,
          border: 'none',
          fontFamily: T.fMono,
          fontSize: 12,
          letterSpacing: 2,
          textTransform: 'uppercase',
          cursor: busy ? 'wait' : 'pointer',
          fontWeight: 500,
          opacity: busy ? 0.6 : 1,
        }}
      >
        {busy ? 'Joining…' : 'Join Session →'}
      </motion.button>

      <motion.div
        variants={fadeUp}
        style={{
          marginTop: 28,
          padding: '12px 14px',
          background: T.bg2,
          border: `1px dashed ${T.line2}`,
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          lineHeight: 1.55,
        }}
      >
        Your session persists across refresh via{' '}
        <span style={{ color: T.ink2 }}>?aid=…</span> in the URL.
      </motion.div>
    </motion.div>
  )
}
