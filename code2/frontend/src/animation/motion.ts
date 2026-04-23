import type { Variants, Transition } from 'framer-motion'
export { useReducedMotion } from 'framer-motion'

const EASE_OUT_EXPO: [number, number, number, number] = [0.22, 1, 0.36, 1]

export const viewTransition: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.22,
      ease: EASE_OUT_EXPO,
      when: 'beforeChildren',
      staggerChildren: 0.04,
    },
  },
  exit: {
    opacity: 0,
    y: -6,
    transition: { duration: 0.14, ease: 'easeIn' },
  },
}

export const fadeUp: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.32, ease: EASE_OUT_EXPO },
  },
  exit: { opacity: 0, y: -6, transition: { duration: 0.12 } },
}

export const stagger: Variants = {
  initial: {},
  animate: {
    transition: { staggerChildren: 0.05, delayChildren: 0.04 },
  },
  exit: {},
}

export const scoreBarSpring: Transition = {
  type: 'spring',
  stiffness: 120,
  damping: 24,
  mass: 0.6,
}

export const rowLayoutSpring: Transition = {
  type: 'spring',
  stiffness: 400,
  damping: 38,
  mass: 0.8,
}

export const rowEnter: Variants = {
  initial: { opacity: 0, x: -10 },
  animate: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.22, ease: EASE_OUT_EXPO },
  },
  exit: {
    opacity: 0,
    x: 12,
    transition: { duration: 0.16 },
  },
}
