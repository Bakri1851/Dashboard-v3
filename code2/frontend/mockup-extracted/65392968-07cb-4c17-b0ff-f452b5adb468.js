// Detail screens: Student detail, Question detail, Lab assistant, Settings, Model comparison, Previous sessions.

function BackBar({ label, onBack }) {
  return (
    <div style={{ padding: '14px 36px', borderBottom: `1px solid ${T.line}`, background: T.bg }}>
      <button onClick={onBack} style={{
        background: 'transparent', border: 'none', cursor: 'pointer',
        fontFamily: T.fMono, fontSize: 11, color: T.ink2, letterSpacing: 1, textTransform: 'uppercase',
        display: 'flex', alignItems: 'center', gap: 8, padding: 0,
      }}>← {label}</button>
    </div>
  );
}

// --- Student detail ---
function StudentDetail({ student, onBack }) {
  const s = student;
  const lvl = LEVEL_STYLES[s.level];
  const sparkData = [0.42, 0.48, 0.55, 0.51, 0.60, 0.58, 0.64, 0.62, 0.68, 0.71];

  return (
    <div>
      <BackBar label="Back to leaderboard" onBack={onBack} />
      <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}>

        {/* Header card */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 24, alignItems: 'stretch' }}>
          <div style={{ padding: '28px 32px', background: T.card, border: `1px solid ${T.line}` }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 20 }}>
              <div>
                <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                  Student · {s.id}
                </div>
                <div style={{ fontFamily: T.fSerif, fontSize: 72, lineHeight: 0.95, color: lvl.fg, marginTop: 10, fontFeatureSettings: '"tnum"' }}>
                  {s.score.toFixed(2)}
                </div>
                <div style={{ marginTop: 10 }}><Pill level={s.level} size={12} /></div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
                  Trajectory, last 10
                </div>
                <div style={{ marginTop: 12 }}>
                  <Spark data={sparkData} width={240} height={70} color={lvl.fg} fill />
                </div>
                <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 8 }}>
                  {s.trend >= 0 ? '+' : ''}{s.trend.toFixed(2)} recent slope
                </div>
              </div>
            </div>
            <div style={{ marginTop: 24, paddingTop: 20, borderTop: `1px solid ${T.line}`, fontFamily: T.fSans, fontSize: 13, color: T.ink2, lineHeight: 1.55 }}>
              <strong style={{ color: T.ink, fontWeight: 500 }}>Why flagged.</strong> Recent incorrectness (0.68) is sharply above class mean (0.41), with retry rate {(s.retry*100).toFixed(0)}% and trajectory trending down over the last hour. Bayesian shrinkage applied with K=5; raw score 0.74 → {s.score.toFixed(2)}.
            </div>
          </div>

          {/* Metric strip */}
          <div style={{ display: 'grid', gridTemplateRows: 'repeat(4, 1fr)', gap: 8 }}>
            <MetricRow label="Submissions" value={s.submissions} note="↑ 18% vs class" />
            <MetricRow label="Time active" value={s.time} note="long session" />
            <MetricRow label="Retry rate" value={`${(s.retry*100).toFixed(0)}%`} note="median 15%" />
            <MetricRow label="Feedback requests" value={s.feedback} note="viewed AI hints" />
          </div>
        </div>

        {/* Components + Questions */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 24 }}>
          <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={4}>Score Components</SectionLabel>
            <HBars items={[
              { label: 'n̂ submissions',     value: 0.48, valueLabel: '0.48', color: T.ink3 },
              { label: 't̂ time active',     value: 0.55, valueLabel: '0.55', color: T.ink3 },
              { label: 'ī mean incorrect.', value: 0.62, valueLabel: '0.62', color: T.warn },
              { label: 'r̂ retry rate',     value: 0.42, valueLabel: '0.42', color: T.warn },
              { label: 'A recent (EMA)',    value: 0.68, valueLabel: '0.68', color: T.danger },
              { label: 'd̂ trajectory',     value: 0.72, valueLabel: '0.72', color: T.danger },
              { label: 'rep̂ repetition',   value: 0.31, valueLabel: '0.31', color: T.ink3 },
            ]} max={1} />
            <div style={{ marginTop: 16, padding: 12, background: T.bg2, fontFamily: T.fMono, fontSize: 11, color: T.ink2, lineHeight: 1.6 }}>
              S_raw = 0.10·n̂ + 0.10·t̂ + 0.20·ī + 0.10·r̂ + 0.38·A + 0.05·d̂ + 0.07·rep̂
            </div>
          </div>

          <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
            <SectionLabel n={5}>Top Questions Attempted</SectionLabel>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
              <thead>
                <tr>
                  {['Question','Attempts','Difficulty','Last feedback'].map(h => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '8px 0', fontFamily: T.fMono,
                      fontSize: 10, letterSpacing: 1, color: T.ink3, textTransform: 'uppercase',
                      fontWeight: 500, borderBottom: `1px solid ${T.line}`,
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { q: 'Q-1407', a: 8, d: 'Very Hard', f: '0.82' },
                  { q: 'Q-0928', a: 6, d: 'Very Hard', f: '0.91' },
                  { q: 'Q-2311', a: 5, d: 'Hard',      f: '0.55' },
                  { q: 'Q-0471', a: 4, d: 'Hard',      f: '0.12' },
                  { q: 'Q-1802', a: 3, d: 'Hard',      f: '0.21' },
                ].map((r, i) => (
                  <tr key={i}>
                    <td style={{ padding: '9px 0', fontFamily: T.fMono, fontSize: 12, borderBottom: `1px solid ${T.line}`, color: T.ink }}>{r.q}</td>
                    <td style={{ padding: '9px 0', fontVariantNumeric: 'tabular-nums', borderBottom: `1px solid ${T.line}` }}>{r.a}</td>
                    <td style={{ padding: '9px 0', borderBottom: `1px solid ${T.line}` }}><Pill level={r.d} /></td>
                    <td style={{ padding: '9px 0', fontFamily: T.fMono, fontSize: 12, borderBottom: `1px solid ${T.line}`, color: parseFloat(r.f) > 0.5 ? T.danger : T.ok }}>{r.f}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* CF similar students */}
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={6}>Similar Students · Collaborative Filtering</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
            {[
              { id: 'math1157', sim: 0.91, level: 'Needs Help' },
              { id: 'phys2023', sim: 0.84, level: 'Needs Help' },
              { id: 'biol1492', sim: 0.79, level: 'Struggling' },
              { id: 'chem3108', sim: 0.72, level: 'Struggling' },
              { id: 'cmps2211', sim: 0.66, level: 'Struggling' },
            ].map((p, i) => (
              <div key={i} style={{ padding: 14, border: `1px solid ${T.line}`, background: T.bg2 }}>
                <div style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink, marginBottom: 6 }}>{p.id}</div>
                <Pill level={p.level} />
                <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1 }}>
                  COS SIM
                </div>
                <div style={{ fontFamily: T.fMono, fontSize: 18, color: T.accent, marginTop: 2 }}>{p.sim.toFixed(2)}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, lineHeight: 1.6 }}>
            Ranked by cosine similarity across 5 behavioural features (n̂, t̂, ī, Â, d̂). High similarity = comparable submission patterns.
          </div>
        </div>

        {/* Recent */}
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={7}>Recent Submissions</SectionLabel>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
            <thead>
              <tr>{['Time','Question','Answer','Incorrectness'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '8px 0', fontFamily: T.fMono, fontSize: 10, letterSpacing: 1, color: T.ink3, textTransform: 'uppercase', fontWeight: 500, borderBottom: `1px solid ${T.line}` }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {window.MOCK.submissions.map((r, i) => (
                <tr key={i}>
                  <td style={{ padding: '10px 0', fontFamily: T.fMono, fontSize: 12, color: T.ink2, borderBottom: `1px solid ${T.line}` }}>{r.t}</td>
                  <td style={{ padding: '10px 0', fontFamily: T.fMono, fontSize: 12, color: T.ink, borderBottom: `1px solid ${T.line}` }}>{r.q}</td>
                  <td style={{ padding: '10px 0', fontFamily: T.fMono, fontSize: 12, color: T.ink2, borderBottom: `1px solid ${T.line}`, maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.a}</td>
                  <td style={{ padding: '10px 0', borderBottom: `1px solid ${T.line}`, width: 160 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <ScoreBar value={r.score} color={r.score > 0.5 ? T.danger : T.ok} width={80} height={3} />
                      <span style={{ fontFamily: T.fMono, fontSize: 12, color: r.score > 0.5 ? T.danger : T.ok }}>{r.score.toFixed(2)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricRow({ label, value, note }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', padding: '14px 18px', background: T.card, border: `1px solid ${T.line}`, alignItems: 'center' }}>
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>{label}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>{note}</div>
      </div>
      <div style={{ fontFamily: T.fSerif, fontSize: 30, color: T.ink, fontFeatureSettings: '"tnum"' }}>{value}</div>
    </div>
  );
}

// --- Question detail ---
function QuestionDetail({ question, onBack }) {
  const q = question;
  const lvl = LEVEL_STYLES[q.level];
  return (
    <div>
      <BackBar label="Back to leaderboard" onBack={onBack} />
      <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}>

        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 24 }}>
          <div style={{ padding: '28px 32px', background: T.card, border: `1px solid ${T.line}` }}>
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
              Question · {q.id} · {q.module}
            </div>
            <div style={{ fontFamily: T.fSerif, fontSize: 72, lineHeight: 0.95, color: lvl.fg, marginTop: 10, fontFeatureSettings: '"tnum"' }}>
              {q.score.toFixed(2)}
            </div>
            <div style={{ marginTop: 10 }}><Pill level={q.level} size={12} /></div>

            <div style={{ marginTop: 22, paddingTop: 18, borderTop: `1px solid ${T.line}`, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 0 }}>
              {[
                { l: 'Incorrect rate', v: '72%' },
                { l: 'Avg attempts',   v: q.avgAttempts.toFixed(1) },
                { l: 'Avg time',       v: q.avgTime },
                { l: 'First-fail',     v: `${(q.firstFail*100).toFixed(0)}%` },
              ].map((m, i, arr) => (
                <div key={i} style={{ borderRight: i < arr.length - 1 ? `1px solid ${T.line}` : 'none', padding: '4px 16px 4px 0' }}>
                  <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.1, textTransform: 'uppercase' }}>{m.l}</div>
                  <div style={{ fontFamily: T.fSerif, fontSize: 22, color: T.ink, marginTop: 4, fontFeatureSettings: '"tnum"' }}>{m.v}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ padding: '22px 24px', background: T.ink, color: '#fff', borderRadius: 2 }}>
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, opacity: 0.7, letterSpacing: 1.3, textTransform: 'uppercase' }}>
              Measurement Confidence
            </div>
            <div style={{ fontFamily: T.fSerif, fontSize: 56, marginTop: 10, lineHeight: 0.95 }}>0.86</div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.75, marginTop: 10 }}>
              High — based on {q.students} students, {Math.round(q.students * q.avgAttempts)} submissions
            </div>
            <div style={{ marginTop: 18, borderTop: `1px solid rgba(255,255,255,0.2)`, paddingTop: 14 }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, opacity: 0.7, letterSpacing: 1.3, textTransform: 'uppercase' }}>IRT difficulty</div>
              <div style={{ fontFamily: T.fMono, fontSize: 22, marginTop: 4 }}>b = +1.42</div>
              <div style={{ fontFamily: T.fMono, fontSize: 11, opacity: 0.7, marginTop: 6 }}>Rasch estimate, joint MLE</div>
            </div>
          </div>
        </div>

        {/* Mistake clusters */}
        <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={1}>Mistake Clusters</SectionLabel>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
            {window.MOCK.clusters.map((c, i) => (
              <div key={i} style={{ padding: '18px 20px', border: `1px solid ${T.line}`, background: T.bg2 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 16 }}>
                  <div style={{ fontFamily: T.fSans, fontSize: 14, fontWeight: 500, color: T.ink, lineHeight: 1.3 }}>
                    {c.label}
                  </div>
                  <div style={{ fontFamily: T.fSerif, fontSize: 22, color: T.accent, fontFeatureSettings: '"tnum"' }}>
                    {Math.round(c.share * 100)}<span style={{ fontSize: 13, color: T.ink3 }}>%</span>
                  </div>
                </div>
                <div style={{ marginTop: 10 }}>
                  <ScoreBar value={c.share} color={T.accent} height={2} />
                </div>
                <div style={{ marginTop: 14 }}>
                  {c.examples.map((ex, j) => (
                    <div key={j} style={{
                      fontFamily: T.fMono, fontSize: 11.5, color: T.ink2,
                      padding: '5px 0', borderTop: j === 0 ? 'none' : `1px dashed ${T.line2}`,
                    }}>{ex}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Suggested feedback */}
        <div style={{ padding: 24, background: T.accentSoft, border: `1px solid ${T.accent}` }}>
          <SectionLabel n={2}>Suggested Teaching Feedback · RAG</SectionLabel>
          <ul style={{ margin: 0, paddingLeft: 20, fontFamily: T.fSans, fontSize: 13.5, color: T.ink, lineHeight: 1.7 }}>
            <li>Re-demonstrate the half-open interval convention: <code style={{ fontFamily: T.fMono, background: '#fff', padding: '1px 4px' }}>range(n)</code> yields 0..n-1 — 38% of mistakes hinge on this.</li>
            <li>Draw a side-by-side of <code style={{ fontFamily: T.fMono, background: '#fff', padding: '1px 4px' }}>list.sort()</code> (mutates, returns None) vs <code style={{ fontFamily: T.fMono, background: '#fff', padding: '1px 4px' }}>sorted(list)</code> (returns a new list) — a full quarter of wrong answers confuse the two.</li>
            <li>Add an empty-input edge case to the worked example so students see the <code style={{ fontFamily: T.fMono, background: '#fff', padding: '1px 4px' }}>n == 0</code> guard explicitly.</li>
          </ul>
          <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
            Generated by rag.generate_cluster_suggestions · cached per session
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Lab assistant coordination view ---
function LabAssistantView({ sessionActive, sessionCode }) {
  const assistants = window.MOCK.assistants;
  const strugglers = window.MOCK.students.filter(s => s.level === 'Needs Help' || s.level === 'Struggling');

  if (!sessionActive) {
    return (
      <div style={{ padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 2, textTransform: 'uppercase' }}>
          No active session
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 28, color: T.ink }}>Start a session to coordinate assistants.</div>
        <div style={{ fontFamily: T.fSans, fontSize: 13.5, color: T.ink2, maxWidth: 440, textAlign: 'center', lineHeight: 1.6 }}>
          Click <em>Start Session</em> in the sidebar. A 6-character join code is generated; share it with lab assistants via the mobile portal at <code style={{ fontFamily: T.fMono }}>/lab</code>.
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}>

      {/* Session banner */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 24, alignItems: 'center',
        padding: '22px 28px', background: T.card, border: `1px solid ${T.line}`,
      }}>
        <div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.3, textTransform: 'uppercase' }}>
            Session Code · share with assistants
          </div>
          <div style={{ fontFamily: T.fMono, fontSize: 42, color: T.ink, letterSpacing: 8, marginTop: 4 }}>
            {sessionCode}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>Joined</div>
          <div style={{ fontFamily: T.fSerif, fontSize: 32, color: T.ink, fontFeatureSettings: '"tnum"' }}>{assistants.length}</div>
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
          <input type="checkbox" defaultChecked />
          <span style={{ fontFamily: T.fSans, fontSize: 12.5, color: T.ink2 }}>Allow self-allocation</span>
        </label>
      </div>

      {/* Two columns: assistants & dispatch queue */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.3fr', gap: 24 }}>

        {/* Assistants */}
        <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
          <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
            <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Lab Assistants</div>
            <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>Live roster · updates every 1s</div>
          </div>
          {assistants.map((a, i) => (
            <div key={i} style={{ padding: '16px 22px', borderBottom: i < assistants.length - 1 ? `1px solid ${T.line}` : 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: T.bg2, border: `1px solid ${T.line2}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.fMono, fontSize: 11, color: T.ink2 }}>
                  {a.name.split(' ').map(n=>n[0]).join('')}
                </div>
                <div>
                  <div style={{ fontFamily: T.fSans, fontSize: 13.5, color: T.ink, fontWeight: 500 }}>{a.name}</div>
                  <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 2 }}>
                    joined {a.joined}
                    {a.student && <> · <span style={{ color: T.accent }}>→ {a.student}</span></>}
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {a.status === 'helping'
                  ? <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.warn, letterSpacing: 1.2, textTransform: 'uppercase' }}>● Helping</span>
                  : <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>○ Waiting</span>}
                <Button>{a.status === 'helping' ? 'Release' : 'Assign'}</Button>
              </div>
            </div>
          ))}
        </div>

        {/* Dispatch queue */}
        <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
          <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}`, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <div>
              <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Dispatch Queue</div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>Flagged students · ranked by urgency</div>
            </div>
            <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.danger, letterSpacing: 1.2, textTransform: 'uppercase' }}>
              {strugglers.length} open
            </span>
          </div>
          {strugglers.slice(0, 6).map((s, i) => (
            <div key={i} style={{
              padding: '14px 22px', borderBottom: i < 5 ? `1px solid ${T.line}` : 'none',
              display: 'grid', gridTemplateColumns: '1fr auto auto', gap: 16, alignItems: 'center',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>{String(i+1).padStart(2,'0')}</span>
                <div>
                  <div style={{ fontFamily: T.fMono, fontSize: 13, color: T.ink }}>{s.id}</div>
                  <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 2 }}>
                    recent {s.recent.toFixed(2)} · retry {(s.retry*100).toFixed(0)}%
                  </div>
                </div>
              </div>
              <Pill level={s.level} />
              <Button variant="accent">Dispatch →</Button>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile mock preview */}
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Assistant Mobile Portal · live mirror</SectionLabel>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          <MobileMock title="Join" body={
            <div style={{ padding: 16 }}>
              <div style={{ fontFamily: T.fSerif, fontSize: 18, color: T.ink }}>Lab Assistant</div>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase', marginTop: 2 }}>Join Session</div>
              <div style={{ marginTop: 18, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>Your name</div>
              <div style={{ marginTop: 4, padding: '8px 10px', border: `1px solid ${T.line2}`, fontFamily: T.fSans, fontSize: 13, color: T.ink3 }}>Amelia R.</div>
              <div style={{ marginTop: 14, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>Code</div>
              <div style={{ marginTop: 4, padding: '8px 10px', border: `1px solid ${T.line2}`, fontFamily: T.fMono, fontSize: 22, letterSpacing: 4, color: T.ink }}>{sessionCode}</div>
              <div style={{ marginTop: 18, padding: '10px 0', textAlign: 'center', background: T.ink, color: '#fff', fontFamily: T.fMono, fontSize: 11, letterSpacing: 1.2, textTransform: 'uppercase' }}>Join</div>
            </div>
          } />
          <MobileMock title="Assigned" body={
            <div style={{ padding: 16 }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.accent, letterSpacing: 1.8, textTransform: 'uppercase' }}>● Assignment</div>
              <div style={{ fontFamily: T.fSerif, fontSize: 28, color: T.ink, marginTop: 6 }}>psyc2041</div>
              <div style={{ marginTop: 4 }}><Pill level="Needs Help" /></div>
              <div style={{ marginTop: 16, padding: 12, background: T.bg2, fontFamily: T.fSans, fontSize: 12, color: T.ink2, lineHeight: 1.5 }}>
                <strong style={{ color: T.ink }}>Why.</strong> Stuck on Q-1407 for 8 attempts. Recent incorrectness 0.68.
              </div>
              <div style={{ marginTop: 16, padding: '10px 0', textAlign: 'center', background: T.ok, color: '#fff', fontFamily: T.fMono, fontSize: 11, letterSpacing: 1.2, textTransform: 'uppercase' }}>Mark Helped</div>
              <div style={{ marginTop: 8, padding: '10px 0', textAlign: 'center', border: `1px solid ${T.line2}`, color: T.ink2, fontFamily: T.fMono, fontSize: 11, letterSpacing: 1.2, textTransform: 'uppercase' }}>Release</div>
            </div>
          } />
          <MobileMock title="Browse" body={
            <div style={{ padding: 16 }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase' }}>Available students</div>
              {strugglers.slice(0,4).map((s,i) => (
                <div key={i} style={{ marginTop: 10, padding: '10px 12px', border: `1px solid ${T.line}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink }}>{s.id}</div>
                    <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, marginTop: 2 }}>recent {s.recent.toFixed(2)}</div>
                  </div>
                  <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.accent, letterSpacing: 1.2, textTransform: 'uppercase' }}>Help →</span>
                </div>
              ))}
            </div>
          } />
        </div>
      </div>
    </div>
  );
}

function MobileMock({ title, body }) {
  return (
    <div>
      <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 10 }}>
        {title}
      </div>
      <div style={{ width: '100%', aspectRatio: '9 / 17', background: T.bg2, border: `1px solid ${T.line2}`, borderRadius: 18, overflow: 'hidden', position: 'relative' }}>
        <div style={{ background: T.card, margin: 8, borderRadius: 12, height: 'calc(100% - 16px)', overflow: 'auto' }}>
          {body}
        </div>
      </div>
    </div>
  );
}

// --- Settings ---
function SettingsView() {
  const DS = window.DashSettings;
  const [theme, setTheme] = DS.useSetting('theme');
  const [struggleModel, setStruggleModel] = DS.useSetting('struggleModel');
  const [difficultyModel, setDifficultyModel] = DS.useSetting('difficultyModel');
  const [cfEnabled, setCfEnabled] = DS.useSetting('cfEnabled');
  const [cfThreshold, setCfThreshold] = DS.useSetting('cfThreshold');
  const [smoothing, setSmoothing] = DS.useSetting('smoothing');
  const [sounds, setSounds] = DS.useSetting('sounds');
  const [autoRefresh, setAutoRefresh] = DS.useSetting('autoRefresh');
  const [refreshInterval, setRefreshInterval] = DS.useSetting('refreshInterval');
  const [pInit, setPInit] = DS.useSetting('bkt_p_init');
  const [pLearn, setPLearn] = DS.useSetting('bkt_p_learn');
  const [pGuess, setPGuess] = DS.useSetting('bkt_p_guess');
  const [pSlip, setPSlip] = DS.useSetting('bkt_p_slip');

  const themes = [
    { name: 'paper', title: 'Editorial Paper', subtitle: 'Warm off-white · IBM Plex · indigo',
      swatches: ['#ffffff','oklch(0.90 0.006 80)','oklch(0.42 0.12 265)','oklch(0.18 0.01 80)'], kind: 'light' },
    { name: 'scifi', title: 'Phosphor Console', subtitle: 'Deep space · CRT scanlines · cyan',
      swatches: ['oklch(0.14 0.02 240)','oklch(0.42 0.08 200)','oklch(0.78 0.14 195)','oklch(0.85 0.18 135)'], kind: 'scifi' },
    { name: 'blueprint', title: 'Blueprint', subtitle: 'Drafting paper · Inconsolata · grid',
      swatches: ['oklch(0.28 0.08 245)','oklch(0.58 0.12 240)','oklch(0.88 0.10 90)','oklch(0.97 0.015 240)'], kind: 'blueprint' },
    { name: 'matrix', title: 'Matrix Terminal', subtitle: 'Green phosphor · VT323 · pure term',
      swatches: ['oklch(0.08 0 0)','oklch(0.38 0.10 150)','oklch(0.92 0.22 145)','oklch(0.72 0.18 150)'], kind: 'matrix' },
    { name: 'cyberpunk', title: 'Cyberpunk', subtitle: 'Neon magenta + cyan · Rajdhani',
      swatches: ['oklch(0.12 0.05 310)','oklch(0.48 0.15 315)','oklch(0.72 0.26 335)','oklch(0.82 0.18 190)'], kind: 'cyberpunk' },
    { name: 'newsprint', title: 'Newsprint', subtitle: 'Broadsheet · Playfair · crimson',
      swatches: ['oklch(0.96 0.012 75)','oklch(0.82 0.015 75)','oklch(0.42 0.18 25)','oklch(0.15 0.02 60)'], kind: 'light' },
    { name: 'solar', title: 'Solar Flare', subtitle: 'Warm cream · Fraunces · amber',
      swatches: ['oklch(0.95 0.03 85)','oklch(0.82 0.04 85)','oklch(0.52 0.14 55)','oklch(0.30 0.04 55)'], kind: 'light' },
  ];

  const savedNote = <span style={{ fontFamily: T.fMono, fontSize: 10, color: T.ok, letterSpacing: 1 }}>● SAVED</span>;

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 960 }}>

      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
          <SectionLabel n={1}>Appearance · Theme</SectionLabel>
        </div>
        <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14, lineHeight: 1.6 }}>
          Seven visual skins — pick any. Changes persist and apply immediately.
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
          {themes.map(t => (
            <ThemeCard key={t.name} {...t} active={theme === t.name} onPick={() => setTheme(t.name)} />
          ))}
        </div>
      </div>

      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Scoring Models</SectionLabel>
        <ToggleRow label="Struggle model" options={['Baseline', 'Improved']} active={struggleModel} onChange={setStruggleModel} />
        <ToggleRow label="Difficulty model" options={['Baseline', 'IRT']} active={difficultyModel} onChange={setDifficultyModel} />
        <ToggleRow label="Collaborative Filtering" options={['Off', 'On']} active={cfEnabled ? 'On' : 'Off'} onChange={(v) => setCfEnabled(v === 'On')} />
        <div style={{ marginTop: 18, padding: 14, background: T.bg2, fontFamily: T.fMono, fontSize: 11, color: T.ink2, lineHeight: 1.6 }}>
          CF compares students on 5 behavioural features (n̂, t̂, ī, Â, d̂) using cosine similarity. Threshold τ controls strictness.
        </div>
        <div style={{ marginTop: 18, display: 'grid', gridTemplateColumns: '1fr auto', gap: 10, alignItems: 'center', opacity: cfEnabled ? 1 : 0.4 }}>
          <div style={{ fontFamily: T.fSans, fontSize: 13, color: T.ink }}>CF threshold (τ)</div>
          <div style={{ fontFamily: T.fMono, fontSize: 13, color: T.accent }}>{Number(cfThreshold).toFixed(2)}</div>
          <input type="range" min="0" max="1" step="0.01" value={cfThreshold} disabled={!cfEnabled}
            onChange={(e) => setCfThreshold(parseFloat(e.target.value))}
            style={{ gridColumn: '1 / span 2', accentColor: T.accent }} />
        </div>
      </div>

      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}`, opacity: struggleModel === 'Improved' ? 1 : 0.55 }}>
        <SectionLabel n={3}>BKT Parameters · Improved model</SectionLabel>
        {struggleModel !== 'Improved' && (
          <div style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3, marginBottom: 14 }}>
            Enabled only when struggle model is set to "Improved".
          </div>
        )}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
          {[
            { l: 'p_init', val: pInit, setter: setPInit },
            { l: 'p_learn', val: pLearn, setter: setPLearn },
            { l: 'p_guess', val: pGuess, setter: setPGuess },
            { l: 'p_slip', val: pSlip, setter: setPSlip },
          ].map((p) => (
            <div key={p.l} style={{ padding: 14, border: `1px solid ${T.line}`, background: T.bg2 }}>
              <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1, textTransform: 'uppercase' }}>{p.l}</div>
              <div style={{ fontFamily: T.fSerif, fontSize: 26, color: T.ink, marginTop: 4 }}>{Number(p.val).toFixed(2)}</div>
              <input type="range" min="0" max="1" step="0.01" value={p.val}
                disabled={struggleModel !== 'Improved'}
                onChange={(e) => p.setter(parseFloat(e.target.value))}
                style={{ width: '100%', marginTop: 6, accentColor: T.accent }} />
            </div>
          ))}
        </div>
      </div>

      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={4}>Environment</SectionLabel>
        <ToggleRow label="Temporal smoothing (EMA)" options={['Off', 'On']} active={smoothing ? 'On' : 'Off'} onChange={(v) => setSmoothing(v === 'On')} />
        <ToggleRow label="Sound effects" options={['Off', 'On']} active={sounds ? 'On' : 'Off'} onChange={(v) => { setSounds(v === 'On'); if (v === 'On') setTimeout(() => window.DashSettings.playSelect(), 50); }} />
        <ToggleRow label="Auto-refresh" options={['Off', 'On']} active={autoRefresh ? 'On' : 'Off'} onChange={(v) => setAutoRefresh(v === 'On')} />
        <div style={{ marginTop: 12, display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'center', gap: 10, opacity: autoRefresh ? 1 : 0.4 }}>
          <div style={{ fontFamily: T.fSans, fontSize: 13 }}>Refresh interval</div>
          <div style={{ fontFamily: T.fMono, fontSize: 13 }}>{refreshInterval}s</div>
          <input type="range" min="5" max="120" step="5" value={refreshInterval}
            disabled={!autoRefresh}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value, 10))}
            style={{ gridColumn: '1 / span 2', accentColor: T.accent }} />
        </div>
      </div>

      <div style={{ padding: '14px 18px', background: T.bg2, border: `1px dashed ${T.line2}`, fontFamily: T.fMono, fontSize: 11, color: T.ink2, display: 'flex', justifyContent: 'space-between' }}>
        <span>All changes save automatically to your browser.</span>
        <button onClick={() => {
          if (!confirm('Reset all settings to defaults?')) return;
          Object.entries(window.DashSettings.DEFAULTS).forEach(([k, v]) => {
            if (k !== 'theme') window.DashSettings.set(k, v);
          });
        }} style={{
          background: 'transparent', color: T.danger, border: `1px solid ${T.danger}`,
          padding: '3px 10px', fontFamily: T.fMono, fontSize: 10, letterSpacing: 1,
          textTransform: 'uppercase', cursor: 'pointer',
        }}>Reset Defaults</button>
      </div>
    </div>
  );
}

function ThemeCard({ name, active, title, subtitle, swatches, kind, onPick }) {
  const isDark = kind === 'scifi' || kind === 'blueprint' || kind === 'matrix' || kind === 'cyberpunk';
  const bg = swatches[0];
  const borderColor = active ? T.accent : T.line;
  const titleColor = isDark ? 'rgba(255,255,255,0.95)' : 'oklch(0.18 0.01 80)';
  const subColor = isDark ? 'rgba(255,255,255,0.55)' : 'oklch(0.58 0.008 80)';
  const fontFam = {
    scifi: `'Space Grotesk', sans-serif`,
    blueprint: `'Inconsolata', monospace`,
    matrix: `'VT323', monospace`,
    cyberpunk: `'Rajdhani', sans-serif`,
    newsprint: `'Playfair Display', serif`,
    solar: `'Fraunces', serif`,
  }[name] || T.fSerif;
  return (
    <div onClick={onPick} style={{
      position: 'relative', cursor: 'pointer', padding: 16, background: bg,
      border: `1.5px solid ${borderColor}`,
      boxShadow: active ? `0 0 0 3px ${T.accent}33` : 'none',
      transition: 'all 0.15s',
      overflow: 'hidden',
    }}>
      {active && (
        <div style={{ position: 'absolute', top: 8, right: 10, fontFamily: T.fMono, fontSize: 9,
          letterSpacing: 1.5, color: T.accent, textTransform: 'uppercase', zIndex: 2 }}>● Active</div>
      )}
      <div style={{ position: 'relative', zIndex: 2 }}>
        <div style={{ fontFamily: T.fMono, fontSize: 9.5, letterSpacing: 1.5, color: subColor,
          textTransform: 'uppercase', marginBottom: 6 }}>Theme · {name}</div>
        <div style={{ fontFamily: fontFam, fontSize: name === 'matrix' ? 28 : 19, color: titleColor,
          fontWeight: 500, letterSpacing: name === 'cyberpunk' ? 0.8 : 0, lineHeight: 1.1 }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: subColor, marginTop: 6, lineHeight: 1.4 }}>{subtitle}</div>
        <div style={{ display: 'flex', gap: 4, marginTop: 14 }}>
          {swatches.map((c, i) => (
            <div key={i} style={{
              width: 26, height: 26, background: c,
              border: `1px solid ${isDark ? 'rgba(255,255,255,0.15)' : 'oklch(0.90 0.006 80)'}`,
              boxShadow: isDark && i === 2 ? `0 0 8px ${c}` : 'none',
            }} />
          ))}
        </div>
      </div>
      {kind === 'scifi' && (
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'repeating-linear-gradient(to bottom, transparent 0, transparent 2px, rgba(0,230,255,0.05) 2px, rgba(0,230,255,0.05) 3px)' }} />
      )}
      {kind === 'blueprint' && (
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px) 0 0 / 100% 20px, linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px) 0 0 / 20px 100%' }} />
      )}
      {kind === 'matrix' && (
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'repeating-linear-gradient(to bottom, transparent 0, transparent 2px, rgba(0,255,100,0.08) 2px, rgba(0,255,100,0.08) 3px)' }} />
      )}
      {kind === 'cyberpunk' && (
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'radial-gradient(circle at 80% 20%, rgba(220,40,180,0.25) 0, transparent 50%), radial-gradient(circle at 20% 80%, rgba(0,220,220,0.2) 0, transparent 50%)' }} />
      )}
    </div>
  );
}

function ToggleRow({ label, options, active, onChange }) {
  const sf = T.themeKind === 'scifi' || T.themeKind === 'matrix' || T.themeKind === 'cyberpunk' || T.themeKind === 'blueprint';
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', padding: '10px 0', borderBottom: `1px dashed ${T.line}`, alignItems: 'center', gap: 12 }}>
      <div style={{ fontFamily: T.fSans, fontSize: 13, color: T.ink }}>{label}</div>
      <div style={{ display: 'flex', border: `1px solid ${T.line2}` }}>
        {options.map((o,i) => {
          const isActive = o === active;
          return (
            <div key={i} onClick={() => onChange && onChange(o)} style={{
              padding: '5px 12px', fontFamily: T.fMono, fontSize: 11, letterSpacing: 0.5,
              background: isActive ? (sf ? T.accent : T.ink) : 'transparent',
              color: isActive ? (sf ? T.bg : '#fff') : T.ink2,
              borderLeft: i > 0 ? `1px solid ${T.line2}` : 'none',
              cursor: 'pointer', fontWeight: isActive ? 500 : 400,
              boxShadow: sf && isActive ? `0 0 10px ${T.accent}66` : 'none',
              transition: 'all 0.1s',
            }}>{o}</div>
          );
        })}
      </div>
    </div>
  );
}

// --- Model comparison ---
function ComparisonView() {
  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <ModelCard
          title="Baseline Struggle"
          formula="S = 0.10·n̂ + 0.10·t̂ + 0.20·ī + 0.10·r̂ + 0.38·A + 0.05·d̂ + 0.07·rep̂"
          rows={window.MOCK.students.slice(0,8)}
          kind="base"
        />
        <ModelCard
          title="Improved (BKT + IRT-weighted)"
          formula="S = f(1 − mastery, difficulty_adj, recent_A)"
          rows={window.MOCK.students.slice(0,8).map((s, i) => ({ ...s, score: Math.max(0, Math.min(1, s.score + (i % 2 ? -0.04 : 0.06))) }))}
          kind="impr"
        />
      </div>
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Rank Concordance · Spearman ρ</SectionLabel>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          {[
            { l: 'Struggle ρ', v: '0.82', n: 'baseline vs improved' },
            { l: 'Difficulty ρ', v: '0.88', n: 'baseline vs IRT' },
            { l: 'Needs-Help overlap', v: '86%', n: 'top-10 agreement' },
            { l: 'Hard-Q overlap', v: '91%', n: 'top-10 agreement' },
          ].map((m, i) => (
            <Stat key={i} label={m.l} value={m.v} note={m.n} accent={T.accent} />
          ))}
        </div>
      </div>
    </div>
  );
}

function ModelCard({ title, formula, rows, kind }) {
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
      <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
        <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 6, lineHeight: 1.5 }}>{formula}</div>
      </div>
      {rows.map((r,i) => (
        <div key={i} style={{
          padding: '10px 22px', borderBottom: i < rows.length - 1 ? `1px solid ${T.line}` : 'none',
          display: 'grid', gridTemplateColumns: '28px 1fr auto 100px auto', gap: 12, alignItems: 'center',
        }}>
          <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink3 }}>{String(i+1).padStart(2,'0')}</span>
          <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink }}>{r.id}</span>
          <Pill level={r.level} />
          <ScoreBar value={r.score} color={(LEVEL_STYLES[r.level]||{}).fg || T.ink} height={3} />
          <span style={{ fontFamily: T.fMono, fontSize: 12, color: T.ink, fontVariantNumeric: 'tabular-nums' }}>{r.score.toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

// --- Previous sessions ---
function PreviousSessions() {
  const sessions = [
    { name: 'Lab Session 2026-04-11 17:00', start: '2026-04-11 17:00', dur: '1h 42m', students: 16, flagged: 4 },
    { name: 'Lab Session 2026-04-04 17:00', start: '2026-04-04 17:00', dur: '1h 58m', students: 18, flagged: 6 },
    { name: 'Lab Session 2026-03-28 17:00', start: '2026-03-28 17:00', dur: '1h 31m', students: 14, flagged: 2 },
    { name: 'Revision Session 2026-03-21', start: '2026-03-21 14:00', dur: '2h 10m', students: 22, flagged: 7 },
  ];
  return (
    <div style={{ padding: '28px 36px' }}>
      <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
        <div style={{ padding: '18px 22px', borderBottom: `1px solid ${T.line}` }}>
          <div style={{ fontFamily: T.fSerif, fontSize: 18 }}>Saved Sessions</div>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>
            Loaded sessions apply a fixed start/end window to all views
          </div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>{['Name', 'Start', 'Duration', 'Students', 'Flagged', ''].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '10px 22px', fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase', fontWeight: 500, borderBottom: `1px solid ${T.line}` }}>{h}</th>
            ))}</tr>
          </thead>
          <tbody>
            {sessions.map((s, i) => (
              <tr key={i}>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, color: T.ink }}>{s.name}</td>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, fontFamily: T.fMono, fontSize: 12, color: T.ink2 }}>{s.start}</td>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, fontFamily: T.fMono, fontSize: 12, color: T.ink2 }}>{s.dur}</td>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, fontFamily: T.fMono, fontSize: 12, fontVariantNumeric: 'tabular-nums', color: T.ink }}>{s.students}</td>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, fontFamily: T.fMono, fontSize: 12, fontVariantNumeric: 'tabular-nums', color: T.danger }}>{s.flagged}</td>
                <td style={{ padding: '14px 22px', borderBottom: `1px solid ${T.line}`, textAlign: 'right' }}>
                  <Button>Load</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// --- Data analysis view (simpler) ---
function DataAnalysisView() {
  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        <Stat label="Modules" value="5" note="active today" />
        <Stat label="Peak hour" value="16:00" note="52 submissions" accent={T.accent} />
        <Stat label="Avg attempts / Q" value="2.3" note="class median" />
        <Stat label="Avg session" value="47m" note="active students" />
      </div>
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={1}>Module Breakdown</SectionLabel>
        <HBars items={[
          { label: 'Data Structures', value: 412, valueLabel: '412 subs', color: T.danger },
          { label: 'Algorithms',      value: 318, valueLabel: '318 subs', color: T.warn },
          { label: 'Databases',       value: 241, valueLabel: '241 subs', color: T.ink2 },
          { label: 'Operating Sys',   value: 188, valueLabel: '188 subs', color: T.ink3 },
          { label: 'Intro CS',        value: 125, valueLabel: '125 subs', color: T.ok },
        ]} height={10} />
      </div>
      <div style={{ padding: 24, background: T.card, border: `1px solid ${T.line}` }}>
        <SectionLabel n={2}>Hourly Submissions · last 24h</SectionLabel>
        <TimelineChart data={window.MOCK.timeline} />
      </div>
    </div>
  );
}

Object.assign(window, { StudentDetail, QuestionDetail, LabAssistantView, SettingsView, ComparisonView, PreviousSessions, DataAnalysisView });
