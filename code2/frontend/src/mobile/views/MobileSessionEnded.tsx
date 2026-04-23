import { motion } from 'framer-motion'
import { T } from '../../theme/tokens'
import { stagger, fadeUp } from '../../animation/motion'

/** Shown when the instructor has not started a lab session. */
export function MobileSessionEnded() {
  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      style={{ padding: '40px 22px', textAlign: 'center' }}
    >
      <motion.div
        variants={fadeUp}
        style={{
          fontFamily: T.fMono,
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 2,
          textTransform: 'uppercase',
        }}
      >
        Lab Assistant Portal
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.6 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 22, delay: 0.15 }}
        style={{
          margin: '44px auto 0',
          width: 74,
          height: 74,
          border: `1.5px solid ${T.danger}`,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
      >
        {/* Concentric dashed ring — slow rotation for subtle "alive" feel */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
          style={{
            position: 'absolute',
            inset: 6,
            border: `1px dashed ${T.danger}`,
            borderRadius: '50%',
            opacity: 0.55,
          }}
        />
        {/* Outer breathing halo */}
        <motion.div
          animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0, 0.4] }}
          transition={{ duration: 2.6, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute',
            inset: -6,
            border: `1px solid ${T.danger}`,
            borderRadius: '50%',
            pointerEvents: 'none',
          }}
        />
        <span style={{ fontFamily: T.fMono, fontSize: 26, color: T.danger }}>✕</span>
      </motion.div>

      <motion.div
        variants={fadeUp}
        style={{
          marginTop: 22,
          fontFamily: T.fSerif,
          fontSize: 22,
          color: T.danger,
          letterSpacing: 1,
          textTransform: 'uppercase',
          lineHeight: 1.15,
        }}
      >
        No Active Session
      </motion.div>

      <motion.div
        variants={fadeUp}
        style={{
          marginTop: 14,
          maxWidth: 260,
          margin: '14px auto 0',
          fontFamily: T.fSans,
          fontSize: 13,
          color: T.ink2,
          lineHeight: 1.55,
        }}
      >
        Ask your instructor to start a lab session — this portal will refresh automatically.
      </motion.div>

      <motion.div
        variants={fadeUp}
        style={{
          marginTop: 32,
          padding: '12px 14px',
          background: T.bg2,
          border: `1px dashed ${T.line2}`,
          fontFamily: T.fMono,
          fontSize: 10.5,
          color: T.ink3,
          textAlign: 'left',
          lineHeight: 1.55,
        }}
      >
        <motion.span
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          style={{ color: T.ink2, display: 'inline-block' }}
        >
          polling
        </motion.span>{' '}
        · every 5s
      </motion.div>
    </motion.div>
  )
}
