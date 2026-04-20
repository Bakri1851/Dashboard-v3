/** Frontend mirror of code2/backend/schemas.py Pydantic models. */

export interface LevelBucket {
  label: string
  count: number
}

export interface LiveDataResponse {
  records: number
  last_updated: string
  unique_students: number
  unique_questions: number
  unique_modules: number
  mean_incorrectness: number
  struggle_buckets: LevelBucket[]
  difficulty_buckets: LevelBucket[]
  timeline_24h: number[]
  error: string | null
}

export interface StudentStruggle {
  id: string
  level: string
  score: number
  submissions: number
  recent: number
  trend: number
}

export interface QuestionDifficulty {
  id: string
  level: string
  score: number
  students: number
  avgAttempts: number
  module: string
}

export interface ScoreComponent {
  key: string
  label: string
  value: number
  weight: number
}

export interface StudentQuestionRow {
  question: string
  attempts: number
  difficulty: string
  last_incorrectness: number | null
}

export interface StudentRecentRow {
  timestamp: string
  question: string
  answer: string
  incorrectness: number
}

export interface StudentDetail {
  id: string
  level: string
  score: number
  submissions: number
  recent: number
  trend: number
  mean_incorrectness: number
  time_active_min: number
  retry_rate: number
  components: ScoreComponent[]
  trajectory: number[]
  top_questions: StudentQuestionRow[]
  recent_submissions: StudentRecentRow[]
}

export interface MistakeCluster {
  label: string
  count: number
  percent_of_wrong: number
  example_answers: string[]
}

export interface QuestionRecentAttempt {
  timestamp: string
  user: string
  answer: string
  incorrectness: number
}

export interface QuestionStudentRow {
  id: string
  attempts: number
  mean_incorrectness: number
  struggle_level: string
  struggle_score: number
}

export interface QuestionDetail {
  id: string
  level: string
  score: number
  module: string
  students: number
  avg_attempts: number
  incorrect_rate: number
  first_fail_rate: number
  mistake_clusters: MistakeCluster[]
  recent_attempts: QuestionRecentAttempt[]
  top_strugglers: QuestionStudentRow[]
}

export interface SavedSession {
  id: string
  name: string
  start_time: string | null
  end_time: string | null
  duration_minutes: number | null
  students: number | null
  flagged: number | null
  module_filter: string | null
}

export interface StruggleWeights {
  n: number; t: number; i: number; r: number; a: number; d: number; rep: number
}

export interface DifficultyWeights {
  c: number; t: number; a: number; f: number; p: number
}

export interface BKTParameters {
  p_init: number; p_learn: number; p_guess: number; p_slip: number; mastery_threshold: number
}

export interface Thresholds {
  struggle: [number, number, string, string][]
  difficulty: [number, number, string, string][]
}

export interface RuntimeSettings {
  sounds_enabled: boolean
  auto_refresh: boolean
  refresh_interval: number
  smoothing_enabled: boolean
  cf_enabled: boolean
  cf_threshold: number
  struggle_model: 'baseline' | 'improved' | string
  difficulty_model: 'baseline' | 'irt' | string
  bkt: BKTParameters
}

export interface Settings {
  cache_ttl: number
  correct_threshold: number
  smoothing_alpha: number
  struggle_weights: StruggleWeights
  difficulty_weights: DifficultyWeights
  thresholds: Thresholds
  bkt: BKTParameters
  leaderboard_max_items: number
  runtime: RuntimeSettings
}

export interface ModuleBreakdown {
  module: string
  submissions: number
  unique_students: number
}

export interface TopQuestionRow {
  question: string
  module: string
  attempts: number
  unique_students: number
  avg_attempts: number
}

export interface UserActivityRow {
  user: string
  submissions: number
  unique_questions: number
  first_submission: string | null
  last_submission: string | null
}

export interface WeekActivityCell {
  week_label: string
  day_index: number
  day_label: string
  count: number
}

export interface AnalysisStats {
  total_records: number
  unique_students: number
  unique_questions: number
  modules: number
  peak_hour: number
  peak_hour_count: number
  avg_attempts_per_question: number
  avg_session_minutes: number
  module_breakdown: ModuleBreakdown[]
  timeline_24h: number[]
  top_questions: TopQuestionRow[]
  user_activity: UserActivityRow[]
  activity_by_week: WeekActivityCell[]
}

export interface ModelRow {
  id: string
  level: string
  score: number
}

export interface ModelCompareResponse {
  baseline: ModelRow[]
  improved: ModelRow[]
  spearman_rho: number | null
  top10_overlap: number | null
}

export interface LabAssistant {
  id: string
  name: string
  joined_at: string
  assigned_student: string | null
}

export interface LabAssignment {
  student_id: string
  assistant_id: string
  status: 'helping' | 'helped' | string
  assigned_at: string
  helped_at: string | null
}

export interface LabState {
  session_code: string | null
  session_active: boolean
  session_start: string | null
  generated_at: string
  allow_self_allocation: boolean
  lab_assistants: LabAssistant[]
  assignments: LabAssignment[]
}

export interface JoinResult {
  ok: boolean
  assistant_id: string | null
  error: string | null
}

export interface StrugglingQuestionRow {
  question: string
  avg_incorrectness: number
}

export interface RagSuggestions {
  audience: 'student' | 'question' | string
  subject_id: string
  bullets: string[]
  session_id: string | null
}

export interface AcademicPeriod {
  label: string
  start_date: string
  end_date: string
}

export interface FilterPresetMeta {
  id: string
  label: string
  needs_custom: boolean
}

export interface CFElevatedStudent {
  id: string
  level: string
  baseline_score: number
  cf_score: number
  delta: number
}

export interface CFDiagnostics {
  threshold: number
  k: number
  n_flagged_parametric: number
  n_elevated_cf: number
  fallback: boolean
  reason: string | null
  elevated_students: CFElevatedStudent[]
}

export interface SimilarStudent {
  id: string
  level: string
  struggle_score: number
  similarity: number
}
