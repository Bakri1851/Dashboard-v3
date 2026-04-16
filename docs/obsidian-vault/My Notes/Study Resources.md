---
# Study Resources

Three self-contained HTML study aids created April 2026.
Located in the project outputs directory.

- dashboard_v3_complete_code_reference.html — every function and module
  explained with tags (model/api/state/ui), searchable, filterable
- dashboard_v3_deep_dive.html — 10-tab deep dive with interactive demos
  for struggle formula, Rasch probability, and BKT step-through
- dashboard_v3_learning_roadmap.html — 5-stage learning roadmap with
  25 tasks and 15 self-test questions with reveal/hide answers

Related: [[Architecture]], [[Analytics Engine]], [[Student Struggle Logic]]
---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard V3 — Learning Roadmap</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f1117;color:#e0e0e0;font-size:14px;line-height:1.7;padding:1.5rem}
h1{font-size:18px;font-weight:500;margin-bottom:1.25rem;color:#fff}
.stage{border:1px solid #2a2d3a;border-radius:10px;margin-bottom:1rem;overflow:hidden}
.stage-header{display:flex;align-items:center;gap:12px;padding:14px 16px;cursor:pointer;background:#161923;user-select:none}
.stage-header:hover{background:#1c2030}
.stage-num{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:500;flex-shrink:0}
.stage-title{font-size:14px;font-weight:500;flex:1;color:#e0e0e0}
.stage-meta{font-size:12px;color:#666}
.stage-chevron{font-size:11px;color:#555;transition:transform 0.2s;flex-shrink:0}
.stage-body{display:none;border-top:1px solid #2a2d3a}
.stage-body.open{display:block}
.files-row{display:flex;flex-wrap:wrap;gap:6px;padding:14px 16px 0}
.file-tag{font-size:11px;font-family:'SF Mono',Consolas,monospace;padding:3px 8px;border-radius:4px;background:#1e2231;color:#888;border:1px solid #2a2d3a}
.tasks{padding:12px 16px}
.task{display:flex;gap:10px;margin-bottom:10px;align-items:flex-start}
.task-check{width:18px;height:18px;border-radius:4px;border:1px solid #444;flex-shrink:0;cursor:pointer;margin-top:1px;display:flex;align-items:center;justify-content:center;font-size:10px;background:#1a1d27;color:#56d364}
.task-check.done{background:#0d3322;border-color:#238636}
.task-text{font-size:13px;color:#999;line-height:1.6}
.task-text code{font-family:'SF Mono',Consolas,monospace;font-size:11px;background:#1e2231;padding:1px 4px;border-radius:3px;color:#c9d1d9}
.task-text.done-text{color:#444;text-decoration:line-through}
.quiz-section{border-top:1px solid #2a2d3a;padding:14px 16px}
.quiz-label{font-size:11px;font-weight:500;color:#666;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:10px}
.quiz-q{font-size:13px;color:#999;margin-bottom:8px;line-height:1.6}
.quiz-q strong{color:#ccc;font-weight:500}
.reveal-btn{font-size:12px;padding:4px 12px;border:1px solid #333;border-radius:6px;background:#1a1d27;color:#888;cursor:pointer;margin-top:4px;margin-bottom:12px}
.reveal-btn:hover{background:#22263a;color:#ccc}
.answer{font-size:12px;color:#999;background:#161923;border-radius:6px;padding:8px 12px;margin-bottom:12px;line-height:1.6;display:none;border:1px solid #2a2d3a}
.answer.shown{display:block}
.answer code{font-family:'SF Mono',Consolas,monospace;font-size:11px;background:#1e2231;padding:1px 4px;border-radius:3px;color:#c9d1d9}
.progress-bar-wrap{background:#1a1d27;border-radius:4px;height:6px;margin-bottom:1rem;overflow:hidden}
.progress-bar-fill{height:6px;border-radius:4px;background:#238636;transition:width 0.3s}
.progress-label{font-size:12px;color:#666;margin-bottom:6px}
.s1{background:#0d2a4a;color:#7ab8f5}
.s2{background:#0d3322;color:#56d364}
.s3{background:#3a2a00;color:#e3b341}
.s4{background:#3a0d1a;color:#ff7b72}
.s5{background:#2a0d3a;color:#d2a8ff}
.footer{padding:0.5rem 0 1rem}
.footer p{font-size:13px;color:#666;margin-bottom:8px}
button.viva-btn{padding:6px 16px;font-size:13px;border:1px solid #333;border-radius:6px;background:#1a1d27;color:#ccc;cursor:pointer}
button.viva-btn:hover{border-color:#555;background:#22263a}
</style>
</head>
<body>
<h1>Dashboard V3 — Learning Roadmap</h1>

<div style="padding:0 0 0.5rem">
  <div class="progress-label" id="prog-label">0 of 25 tasks complete</div>
  <div class="progress-bar-wrap"><div class="progress-bar-fill" id="prog-bar" style="width:0%"></div></div>
</div>

<!-- STAGE 1 -->
<div class="stage">
  <div class="stage-header" onclick="toggle('s1')">
    <div class="stage-num s1">1</div>
    <div class="stage-title">Stage 1 — The data layer</div>
    <div class="stage-meta">~1 hr &nbsp;·&nbsp; data_loader.py + config.py</div>
    <div class="stage-chevron" id="chev-s1">▸</div>
  </div>
  <div class="stage-body" id="body-s1">
    <div class="files-row">
      <span class="file-tag">config.py</span>
      <span class="file-tag">data_loader.py</span>
      <span class="file-tag">paths.py</span>
      <span class="file-tag">academic_calendar.py</span>
    </div>
    <div class="tasks">
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>config.py</code> top to bottom. For every constant, say out loud what it controls in the app. Do not move on until you can explain SHRINKAGE_K, DECAY_HALFLIFE_SECONDS, and CORRECT_THRESHOLD without looking.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Open <code>data_loader.py</code>. Read <code>fetch_raw_data()</code> — note the <code>@st.cache_data(ttl=10)</code> decorator and understand exactly what happens on the first call vs subsequent calls within 10 seconds.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>parse_json_response()</code> carefully. Draw on paper what one line of the API response looks like, and trace how it becomes a record dict with 7 fields.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>normalize_and_clean()</code>. List the 4 transformations it applies in order. Understand why rows with failed timestamp parsing are dropped rather than kept with a default.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>load_data()</code>. Understand the second caching layer (hash of raw → skip re-parse). Trace what happens when the API is down — what does the caller receive?</div></div>
    </div>
    <div class="quiz-section">
      <div class="quiz-label">Self-test — answer before revealing</div>
      <div class="quiz-q"><strong>Q1.</strong> The app has been running for 8 seconds. A student submits an answer. The instructor's browser auto-refreshes. Does the new submission appear immediately? Why or why not?</div>
      <button class="reveal-btn" onclick="revealAnswer('a1')">Reveal answer</button>
      <div class="answer" id="a1">No — not yet. <code>fetch_raw_data()</code> is cached with ttl=10s. The 8-second rerun returns the cached raw string. The new submission only appears on a rerun after the 10s TTL expires. With the default 300s auto-refresh interval it would take up to 300s anyway — but even with a 5s interval, a rerun at 8s still uses the cache.</div>
      <div class="quiz-q"><strong>Q2.</strong> The API returns a response where one line has a malformed JSON object. What happens to that line, and what happens to all the other lines?</div>
      <button class="reveal-btn" onclick="revealAnswer('a2')">Reveal answer</button>
      <div class="answer" id="a2"><code>parse_json_response()</code> wraps the inner parse in a try/except. The bad line is silently skipped with <code>continue</code>. All other lines are processed normally. The function never raises — it always returns whatever records it managed to parse.</div>
      <div class="quiz-q"><strong>Q3.</strong> What is CORRECT_THRESHOLD=0.5 used for, and in how many different places does it appear across the codebase?</div>
      <button class="reveal-btn" onclick="revealAnswer('a3')">Reveal answer</button>
      <div class="answer" id="a3">It is the threshold below which a submission is considered "correct". Used in: (1) <code>compute_question_difficulty_scores()</code> to compute c_tilde, (2) <code>build_response_matrix()</code> in IRT to code binary correct/wrong, (3) <code>bkt_update()</code> calls to determine if a submission is correct, (4) <code>cluster_question_mistakes()</code> to filter to only wrong answers for clustering.</div>
    </div>
  </div>
</div>

<!-- STAGE 2 -->
<div class="stage">
  <div class="stage-header" onclick="toggle('s2')">
    <div class="stage-num s2">2</div>
    <div class="stage-title">Stage 2 — The scoring engine</div>
    <div class="stage-meta">~2 hrs &nbsp;·&nbsp; analytics.py</div>
    <div class="stage-chevron" id="chev-s2">▸</div>
  </div>
  <div class="stage-body" id="body-s2">
    <div class="files-row">
      <span class="file-tag">analytics.py</span>
    </div>
    <div class="tasks">
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>_call_openai_batch()</code> and <code>compute_incorrectness_column()</code>. Trace what happens to a feedback string that has already been scored in a previous rerun. Then trace what happens to a brand new one.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>compute_recent_incorrectness()</code>. On paper, work through an example: 3 submissions with incorrectness [0.8, 0.5, 0.2], timestamps 0s, 600s, and 1800s ago. Compute the weights and A_raw manually.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read the full <code>compute_student_struggle_scores()</code> function. Annotate each block with what it produces. Understand why n, t, and d_raw are normalised AFTER the per-student loop rather than inside it.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>compute_question_difficulty_scores()</code>. Understand the difference between c_tilde and f_tilde — both relate to incorrectness but measure different things. Be able to explain this distinction clearly.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>cluster_question_mistakes()</code>. Understand why TF-IDF is used instead of raw text, what silhouette score does, and why the centroid similarity step picks representative answers rather than random ones.</div></div>
    </div>
    <div class="quiz-section">
      <div class="quiz-label">Self-test</div>
      <div class="quiz-q"><strong>Q1.</strong> A student has 3 submissions in the last 2 minutes, all with incorrectness=1.0. Their struggle score before shrinkage is high. After shrinkage with K=5, what happens and why does this matter?</div>
      <button class="reveal-btn" onclick="revealAnswer('b1')">Reveal answer</button>
      <div class="answer" id="b1">w_n = 3/(3+5) = 0.375. S_final = 0.375×S_raw + 0.625×class_mean. With only 3 submissions, 62.5% of the score is pulled toward the class mean — so even if raw score is 1.0, the final score is significantly reduced. This matters because 3 submissions in 2 minutes is not enough evidence to confidently label someone "Needs Help".</div>
      <div class="quiz-q"><strong>Q2.</strong> A question has c_tilde=0.9 (90% of submissions are wrong) but f_tilde=0.3 (average incorrectness score is 0.3). What does this tell you, and is it possible?</div>
      <button class="reveal-btn" onclick="revealAnswer('b2')">Reveal answer</button>
      <div class="answer" id="b2">Yes it is possible — it means most submissions score just above the 0.5 CORRECT_THRESHOLD (so they count as "incorrect" for c_tilde) but the continuous incorrectness scores are mostly around 0.3 (so f_tilde is low). Students are getting nearly-correct answers. The binary threshold creates a cliff that the continuous score does not — this is exactly why having both signals matters.</div>
      <div class="quiz-q"><strong>Q3.</strong> Why are n_hat, t_hat, and d_hat computed with min-max normalisation across ALL students at once, rather than normalising each student's raw value individually?</div>
      <button class="reveal-btn" onclick="revealAnswer('b3')">Reveal answer</button>
      <div class="answer" id="b3">Because the signals only have meaning relative to the class. If you normalised each student independently you would always get 0 or 1 with no variation. Min-max normalisation across all students means: the student with the highest submission count gets n_hat=1.0, the lowest gets 0.0, and everyone else is scaled in between. This preserves the relative distribution within the class.</div>
    </div>
  </div>
</div>

<!-- STAGE 3 -->
<div class="stage">
  <div class="stage-header" onclick="toggle('s3')">
    <div class="stage-num s3">3</div>
    <div class="stage-title">Stage 3 — The advanced models</div>
    <div class="stage-meta">~2 hrs &nbsp;·&nbsp; models/</div>
    <div class="stage-chevron" id="chev-s3">▸</div>
  </div>
  <div class="stage-body" id="body-s3">
    <div class="files-row">
      <span class="file-tag">models/measurement.py</span>
      <span class="file-tag">models/irt.py</span>
      <span class="file-tag">models/bkt.py</span>
      <span class="file-tag">models/improved_struggle.py</span>
    </div>
    <div class="tasks">
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>measurement.py</code>. Understand the three factors in the confidence formula. Be able to explain why a score of 0.5 from empty feedback gets confidence=0 while a score of 0.5 from a long feedback string gets low but non-zero confidence.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>irt.py</code> fully. Derive on paper why grad_b_j = −Σ residuals (not +Σ). Understand what "identifiability" means for the Rasch model and why centring θ fixes it.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>bkt.py</code>. Work through <code>bkt_update()</code> manually: start at P(L)=0.3, submit a wrong answer, compute the posterior, then apply the transition. Verify your answer with the interactive BKT demo in the deep dive artifact.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>improved_struggle.py</code> fully. Trace what happens when has_mastery=False and has_irt=False. Verify that weights still sum to 1.0 in every degradation case.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Understand why <code>compute_improved_struggle_scores()</code> applies min-max normalisation at the end but <code>compute_student_struggle_scores()</code> does not. What problem does it solve in the improved model that does not exist in the baseline?</div></div>
    </div>
    <div class="quiz-section">
      <div class="quiz-label">Self-test</div>
      <div class="quiz-q"><strong>Q1.</strong> A question has IRT difficulty b=2.0. What is its sigmoid-mapped irt_difficulty score, and what classification would it receive?</div>
      <button class="reveal-btn" onclick="revealAnswer('c1')">Reveal answer</button>
      <div class="answer" id="c1">sigmoid(2.0) = 1/(1+exp(-2)) ≈ 0.880. Applying IRT_DIFFICULTY_THRESHOLDS: 0.880 ≥ 0.75 → "Very Hard". A b of +2 means a student needs to be significantly above average ability to have a 50% chance of getting it right.</div>
      <div class="quiz-q"><strong>Q2.</strong> A student has mean_mastery=0.8 from BKT and A_raw=0.2 (doing well recently). What is their mastery_gap, and what does this say about them?</div>
      <button class="reveal-btn" onclick="revealAnswer('c2')">Reveal answer</button>
      <div class="answer" id="c2">recent_performance = 1 - A_raw = 0.8. mastery_gap = max(0, 0.8 - 0.8) = 0.0. The student is performing exactly at their demonstrated mastery level — no gap. The improved model contributes 0 from the mastery_gap component for this student. This is a positive signal.</div>
      <div class="quiz-q"><strong>Q3.</strong> Why does the improved struggle model apply min-max normalisation after shrinkage, but the baseline model does not?</div>
      <button class="reveal-btn" onclick="revealAnswer('c3')">Reveal answer</button>
      <div class="answer" id="c3">The baseline formula uses 7 signals all in [0,1] with weights summing to 1 — the raw output naturally spans most of [0,1]. The improved model's three components can cluster in a narrow range because mastery_gap and difficulty_adjusted are often near 0 when most students are doing fine. Without normalisation, most students land in the same low score band and the classification thresholds become meaningless.</div>
    </div>
  </div>
</div>

<!-- STAGE 4 -->
<div class="stage">
  <div class="stage-header" onclick="toggle('s4')">
    <div class="stage-num s4">4</div>
    <div class="stage-title">Stage 4 — CF, RAG, and coordination</div>
    <div class="stage-meta">~1.5 hrs &nbsp;·&nbsp; analytics.py (CF) + rag.py + lab_state.py</div>
    <div class="stage-chevron" id="chev-s4">▸</div>
  </div>
  <div class="stage-body" id="body-s4">
    <div class="files-row">
      <span class="file-tag">analytics.py (CF section)</span>
      <span class="file-tag">rag.py</span>
      <span class="file-tag">lab_state.py</span>
      <span class="file-tag">paths.py</span>
    </div>
    <div class="tasks">
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>compute_cf_struggle_scores()</code>. Trace the cosine similarity computation. Understand what the diagnostics dict contains and why it is returned alongside the scores — who consumes it?</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>rag.py</code> top to bottom. Understand the rebuild guard in <code>build_rag_collection()</code> — what two conditions must both be true for the collection to be reused? What triggers a rebuild?</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Trace the difference between <code>generate_assistant_suggestions()</code> and <code>generate_cluster_suggestions()</code> — same collection, different <code>where=</code> filter, different audience and prompt tone.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>lab_state.py</code> in full. Draw the state machine on paper: what fields change when (1) a session starts, (2) an assistant joins, (3) a student is assigned, (4) the assistant marks helped, (5) the session ends.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Find every place in <code>lab_state.py</code> where <code>_write_state_unlocked()</code> is called. Confirm that every write goes through <code>_normalize_state()</code> first. Understand why normalisation before writing matters.</div></div>
    </div>
    <div class="quiz-section">
      <div class="quiz-label">Self-test</div>
      <div class="quiz-q"><strong>Q1.</strong> CF is enabled with threshold τ=0.5. A class has 6 students. None have a parametric struggle score above 0.5. What does CF return, and why?</div>
      <button class="reveal-btn" onclick="revealAnswer('d1')">Reveal answer</button>
      <div class="answer" id="d1">It falls back immediately. After computing h (binary labels), n_flagged_parametric=0. The code hits the early return: "no students above threshold". CF scores are set equal to the parametric struggle scores — no elevation occurs. diagnostics["fallback"]=True. CF requires at least one reference "struggling" student to define what struggling looks like behaviourally.</div>
      <div class="quiz-q"><strong>Q2.</strong> The session has been running for 10 minutes. 50 new submissions came in during the last refresh cycle. Will the RAG collection be rebuilt? What are the exact conditions checked?</div>
      <button class="reveal-btn" onclick="revealAnswer('d2')">Reveal answer</button>
      <div class="answer" id="d2">Yes, it will be rebuilt. The rebuild guard checks: (1) _collection is not None, AND (2) session_id == _cached_session_id, AND (3) len(df) == _cached_row_count. Condition 3 fails because len(df) increased by 50. New embeddings are computed for all rows (upserted), _cached_row_count updated.</div>
      <div class="quiz-q"><strong>Q3.</strong> An assistant named "Alice" gets ID "alice_4821", gets assigned a student, then their browser crashes and they reload the page. What happens?</div>
      <button class="reveal-btn" onclick="revealAnswer('d3')">Reveal answer</button>
      <div class="answer" id="d3">The URL still has <code>?aid=alice_4821</code>. The assistant app reads this on reload and restores assistant_id from the query param. <code>get_assignment_for_assistant("alice_4821")</code> finds the assignment in lab_session.json (persisted on disk) and routes directly to the assigned student view. The crash is completely transparent.</div>
    </div>
  </div>
</div>

<!-- STAGE 5 -->
<div class="stage">
  <div class="stage-header" onclick="toggle('s5')">
    <div class="stage-num s5">5</div>
    <div class="stage-title">Stage 5 — The UI and full system</div>
    <div class="stage-meta">~1.5 hrs &nbsp;·&nbsp; instructor_app.py + assistant_app.py + views.py + components.py</div>
    <div class="stage-chevron" id="chev-s5">▸</div>
  </div>
  <div class="stage-body" id="body-s5">
    <div class="files-row">
      <span class="file-tag">instructor_app.py</span>
      <span class="file-tag">assistant_app.py</span>
      <span class="file-tag">ui/views.py</span>
      <span class="file-tag">ui/components.py</span>
      <span class="file-tag">sound.py</span>
    </div>
    <div class="tasks">
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>instructor_app.main()</code> top to bottom. Map out every function call in order. Understand exactly why deferred actions must be processed before any widgets are built — what breaks if you move them after?</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>render_sidebar()</code> fully. Trace what <code>_resolve_time_filter_window()</code> returns in each of the 4 possible states: (a) no session, no time filter; (b) live session active; (c) time filter enabled; (d) saved session loaded.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read the view routing block in <code>main()</code>. Understand the priority order. Then read <code>in_class_view()</code>, <code>student_detail_view()</code>, and <code>question_detail_view()</code> — know what each renders and what session state it reads.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>assistant_app.main()</code>. Trace the full journey of an assistant from opening the URL for the first time through to clicking "Mark as Helped". Note every <code>lab_state</code> call and what it does.</div></div>
      <div class="task"><div class="task-check" onclick="tick(this)"></div><div class="task-text">Read <code>sound.py</code>. Understand the injection mechanism — why is it a zero-height iframe rather than a regular <code>st.markdown()</code> script tag? This is a good detail to know for the viva.</div></div>
    </div>
    <div class="quiz-section">
      <div class="quiz-label">Self-test</div>
      <div class="quiz-q"><strong>Q1.</strong> An instructor loads a saved session from 2 weeks ago. The module that was active then no longer exists in the current data. What exactly happens?</div>
      <button class="reveal-btn" onclick="revealAnswer('e1')">Reveal answer</button>
      <div class="answer" id="e1"><code>apply_saved_session_to_state()</code> receives the available_modules list. It checks: is the saved module_filter in available_modules? If not, it falls back to "All Modules" and appends a warning to session_state["session_load_warning"]. The instructor sees a warning banner and the dashboard loads showing all modules instead of the specific one.</div>
      <div class="quiz-q"><strong>Q2.</strong> The improved models are enabled. The instructor opens the Model Comparison view. What analytics computations have already happened before this view renders?</div>
      <button class="reveal-btn" onclick="revealAnswer('e2')">Reveal answer</button>
      <div class="answer" id="e2">In order: (1) compute_student_struggle_scores() — baseline, (2) compute_question_difficulty_scores() — baseline, (3) compute_irt_difficulty_scores() — if irt_enabled, (4) compute_all_mastery() then compute_student_mastery_summary() — if bkt_enabled, (5) compute_improved_struggle_scores(df, mastery_summary, irt_df) — if improved_struggle_enabled. All happen in main() before routing, so all DataFrames are already computed when comparison_view() is called.</div>
      <div class="quiz-q"><strong>Q3.</strong> A student clicks on a bar in the student leaderboard. Walk through exactly what happens in Streamlit — from the click to the detail view rendering.</div>
      <button class="reveal-btn" onclick="revealAnswer('e3')">Reveal answer</button>
      <div class="answer" id="e3">Plotly registers the bar click as a chart selection event. Streamlit detects this and triggers a rerun. In the rerun, <code>render_student_leaderboard()</code> reads the selection from Plotly's return value, extracts the student_id from the clicked bar's label, calls <code>sound.play_selection()</code>, and sets <code>st.session_state["selected_student"] = student_id</code>. The rerun continues to the routing block. selected_student is now set, so routing hits case 1 and calls <code>student_detail_view()</code>.</div>
    </div>
  </div>
</div>

<div class="footer">
  <p>When you can answer every question above without revealing the answer, you know this codebase inside out.</p>
  <p style="margin-top:6px;font-size:12px;color:#555">Total time: ~8 hours across 3–4 sessions. Work through stages in order.</p>
</div>

<script>
let totalTasks=25,doneTasks=0;
function tick(el){
  const isDone=el.classList.contains('done');
  if(isDone){el.classList.remove('done');el.textContent='';doneTasks=Math.max(0,doneTasks-1);}
  else{el.classList.add('done');el.textContent='✓';doneTasks++;}
  const txt=el.closest('.task').querySelector('.task-text');
  if(isDone)txt.classList.remove('done-text');else txt.classList.add('done-text');
  updateProgress();
}
function updateProgress(){
  const pct=Math.round(doneTasks/totalTasks*100);
  document.getElementById('prog-bar').style.width=pct+'%';
  document.getElementById('prog-label').textContent=doneTasks+' of '+totalTasks+' tasks complete';
}
function toggle(id){
  const body=document.getElementById('body-'+id);
  const chev=document.getElementById('chev-'+id);
  const isOpen=body.classList.contains('open');
  body.classList.toggle('open',!isOpen);
  chev.textContent=isOpen?'▸':'▾';
}
function revealAnswer(id){
  const el=document.getElementById(id);
  const btn=el.previousElementSibling;
  el.classList.toggle('shown');
  btn.textContent=el.classList.contains('shown')?'Hide answer':'Reveal answer';
}
</script>
</body>
</html>
```
