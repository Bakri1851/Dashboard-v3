// Screen components: In-Class view, Student detail, Question detail, Lab assistant, Settings.

const { useState: useStateS, useMemo: useMemoS, useEffect: useEffectS } = React;

// --- Sidebar ---
function Sidebar({ view, setView, sessionActive, toggleSession, sessionCode, elapsed, assistants }) {
  const items = [
    { key: 'inclass',   label: 'In Class' },
    { key: 'analysis',  label: 'Data Analysis' },
    { key: 'compare',   label: 'Model Comparison' },
    { key: 'previous',  label: 'Previous Sessions' },
    { key: 'settings',  label: 'Settings' },
    { key: 'lab',       label: 'Lab Assistant' },
  ];
  return (
    <aside style={{
      width: 240, minWidth: 240, background: T.bg2, borderRight: `1px solid ${T.line}`,
      padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: 24,
    }}>
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 2, textTransform: 'uppercase' }}>
          Learning Analytics
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 20, color: T.ink, marginTop: 4, lineHeight: 1.1 }}>
          Studio<span style={{ color: T.accent }}>.</span>
        </div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 6 }}>
          v3 · instructor console
        </div>
      </div>

      {/* Session */}
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 10 }}>
          Lab Session
        </div>
        {!sessionActive ? (
          <Button variant="primary" onClick={toggleSession}>Start Session</Button>
        ) : (
          <div style={{ background: T.card, border: `1px solid ${T.line}`, padding: '10px 12px' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span style={{ fontFamily: T.fMono, fontSize: 9.5, color: T.ok, letterSpacing: 1.5 }}>● LIVE</span>
              <span style={{ fontFamily: T.fMono, fontSize: 11, color: T.ink, fontVariantNumeric: 'tabular-nums' }}>{elapsed}</span>
            </div>
            <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase' }}>
              Code
            </div>
            <div style={{ fontFamily: T.fMono, fontSize: 22, color: T.ink, letterSpacing: 3, marginTop: 2 }}>
              {sessionCode}
            </div>
            <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink2 }}>
              {assistants.filter(a => a.status === 'helping').length} of {assistants.length} assistants helping
            </div>
            <div style={{ marginTop: 10 }}>
              <Button variant="danger" onClick={toggleSession}>End Session</Button>
            </div>
          </div>
        )}
      </div>

      {/* Nav */}
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 10 }}>
          View
        </div>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {items.map(it => {
            const active = view === it.key;
            return (
              <button key={it.key} onClick={() => setView(it.key)} style={{
                textAlign: 'left', padding: '8px 10px', cursor: 'pointer',
                background: active ? T.card : 'transparent',
                borderLeft: `2px solid ${active ? T.accent : 'transparent'}`,
                border: 'none', borderLeftWidth: 2, borderLeftStyle: 'solid',
                borderLeftColor: active ? T.accent : 'transparent',
                fontFamily: T.fSans, fontSize: 13,
                color: active ? T.ink : T.ink2,
                fontWeight: active ? 500 : 400,
              }}>{it.label}</button>
            );
          })}
        </div>
      </div>

      {/* Filter */}
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10, color: T.ink3, letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 10 }}>
          Range
        </div>
        <select style={{
          width: '100%', padding: '6px 8px', background: T.card,
          border: `1px solid ${T.line2}`, borderRadius: 2,
          fontFamily: T.fMono, fontSize: 11, color: T.ink,
        }} defaultValue="Today">
          {['Live Session','Today','Past Hour','Past 24 Hours','Current Academic Week','Last Academic Week','Custom','All Time'].map(o =>
            <option key={o}>{o}</option>
          )}
        </select>
        <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
          Filtered records: <span style={{ color: T.ink, fontVariantNumeric: 'tabular-nums' }}>1,284</span>
        </div>
      </div>

      <div style={{ marginTop: 'auto', fontFamily: T.fMono, fontSize: 10, color: T.ink3, lineHeight: 1.5 }}>
        Last refresh 17:41:08<br/>
        Auto-refresh every 30s
      </div>
    </aside>
  );
}

// --- Topbar ---
function Topbar({ title, breadcrumbs, right }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '22px 36px', borderBottom: `1px solid ${T.line}`, background: T.bg,
    }}>
      <div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1.4, textTransform: 'uppercase' }}>
          {breadcrumbs}
        </div>
        <div style={{ fontFamily: T.fSerif, fontSize: 28, color: T.ink, marginTop: 4, lineHeight: 1.1 }}>
          {title}
        </div>
      </div>
      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        {right}
      </div>
    </div>
  );
}

// --- In-Class View ---
function InClassView({ onPickStudent, onPickQuestion, onOpenLab }) {
  const [mod, setMod] = useStateS('All Modules');
  const modules = ['All Modules', 'Data Structures', 'Algorithms', 'Databases', 'Operating Systems', 'Intro CS'];

  const s = window.MOCK.students;
  const q = window.MOCK.questions;
  const counts = s.reduce((a,x)=>{a[x.level]=(a[x.level]||0)+1;return a;},{});
  const needs = counts['Needs Help'] || 0;
  const strug = counts['Struggling'] || 0;
  const ok    = (counts['On Track'] || 0) + (counts['Minor Issues'] || 0);

  return (
    <div style={{ padding: '28px 36px', display: 'flex', flexDirection: 'column', gap: 28 }}>

      {/* Hero stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr 1fr 1fr', gap: 12 }}>
        <div style={{
          padding: '20px 22px', background: T.ink, color: '#fff', borderRadius: 2,
          display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        }}>
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, letterSpacing: 1.3, textTransform: 'uppercase', opacity: 0.7 }}>
            Priority Now
          </div>
          <div>
            <div style={{ fontFamily: T.fSerif, fontSize: 56, lineHeight: 0.95, fontFeatureSettings: '"tnum"' }}>{needs}</div>
            <div style={{ fontFamily: T.fMono, fontSize: 11, marginTop: 8, opacity: 0.75 }}>
              students need help &nbsp;·&nbsp; {strug} struggling
            </div>
            <div style={{ marginTop: 14 }}>
              <button onClick={onOpenLab} style={{
                padding: '6px 12px', background: 'transparent', color: '#fff',
                border: '1px solid rgba(255,255,255,0.4)', fontFamily: T.fMono,
                fontSize: 10.5, letterSpacing: 1.2, textTransform: 'uppercase', cursor: 'pointer',
              }}>Dispatch Assistants →</button>
            </div>
          </div>
        </div>
        <Stat label="Total Submissions" value="1,284" note="last 24h" />
        <Stat label="Unique Students" value="14" note="active today" accent={T.accent} />
        <Stat label="Questions Answered" value="11" note="across 5 modules" />
        <Stat label="Mean Incorrectness" value="0.41" note="class average" accent={T.warn} />
      </div>

      {/* Module filter */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, letterSpacing: 1, textTransform: 'uppercase', marginRight: 8 }}>
          Module
        </span>
        {modules.map(m => {
          const active = mod === m;
          return (
            <button key={m} onClick={() => setMod(m)} style={{
              padding: '5px 10px', background: active ? T.ink : 'transparent',
              color: active ? '#fff' : T.ink2, border: `1px solid ${active ? T.ink : T.line2}`,
              borderRadius: 999, fontFamily: T.fSans, fontSize: 12, cursor: 'pointer',
            }}>{m}</button>
          );
        })}
      </div>

      {/* Two leaderboards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <Leaderboard
          title="Student Struggle"
          subtitle="Ranked by composite struggle score · click to drill in"
          cols={['rank','id','level','score','submissions','recent','trend']}
          rows={s.slice(0, 10).map((x, i) => ({
            rank: i+1, id: x.id, level: x.level, score: x.score,
            submissions: x.submissions, recent: x.recent, trend: x.trend, raw: x,
          }))}
          onClick={(r) => onPickStudent(r.raw)}
        />
        <Leaderboard
          title="Question Difficulty"
          subtitle="Ranked by composite difficulty score · click for mistake clusters"
          cols={['rank','id','level','score','students','avgAttempts','module']}
          rows={q.slice(0, 10).map((x, i) => ({
            rank: i+1, id: x.id, level: x.level, score: x.score,
            students: x.students, avgAttempts: x.avgAttempts, module: x.module, raw: x,
          }))}
          onClick={(r) => onPickQuestion(r.raw)}
        />
      </div>

      {/* Distributions + timeline */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1.2fr', gap: 24 }}>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={1}>Struggle Distribution</SectionLabel>
          <Histogram
            data={[counts['On Track']||0, counts['Minor Issues']||0, counts['Struggling']||0, counts['Needs Help']||0]}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            labels={['On Track','Minor','Strug.','Needs']}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            Thresholds: on track &lt; 0.20 · minor &lt; 0.35 · struggling &lt; 0.50 · needs help ≥ 0.50
          </div>
        </div>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={2}>Difficulty Distribution</SectionLabel>
          <Histogram
            data={[
              q.filter(x=>x.level==='Easy').length,
              q.filter(x=>x.level==='Medium').length,
              q.filter(x=>x.level==='Hard').length,
              q.filter(x=>x.level==='Very Hard').length,
            ]}
            bucketColors={[T.ok, T.ink3, T.warn, T.danger]}
            labels={['Easy','Medium','Hard','V.Hard']}
            height={100}
          />
          <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 14, lineHeight: 1.6 }}>
            D = 0.28·c + 0.12·t + 0.20·a + 0.20·f + 0.20·p &nbsp;·&nbsp; weighted
          </div>
        </div>
        <div style={{ padding: 20, background: T.card, border: `1px solid ${T.line}` }}>
          <SectionLabel n={3}>Submissions, last 24h</SectionLabel>
          <TimelineChart data={window.MOCK.timeline} />
        </div>
      </div>
    </div>
  );
}

// --- Leaderboard ---
function Leaderboard({ title, subtitle, cols, rows, onClick }) {
  const header = {
    rank: '#', id: 'ID', level: 'Level', score: 'Score',
    submissions: 'Subs', recent: 'Recent', trend: 'Trend',
    students: 'Students', avgAttempts: 'Avg att.', module: 'Module',
  };
  return (
    <div style={{ background: T.card, border: `1px solid ${T.line}` }}>
      <div style={{ padding: '18px 22px 12px', borderBottom: `1px solid ${T.line}` }}>
        <div style={{ fontFamily: T.fSerif, fontSize: 18, color: T.ink }}>{title}</div>
        <div style={{ fontFamily: T.fMono, fontSize: 10.5, color: T.ink3, marginTop: 4 }}>{subtitle}</div>
      </div>
      <div style={{ maxHeight: 440, overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.fSans, fontSize: 13 }}>
          <thead>
            <tr>
              {cols.map(c => (
                <th key={c} style={{
                  textAlign: c === 'id' || c === 'module' ? 'left' : (c === 'level' ? 'left' : 'right'),
                  padding: '10px 18px', fontFamily: T.fMono, fontSize: 10,
                  color: T.ink3, letterSpacing: 1.2, textTransform: 'uppercase',
                  fontWeight: 500, borderBottom: `1px solid ${T.line}`,
                }}>{header[c]}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} onClick={() => onClick(r)} style={{ cursor: 'pointer' }}
                  onMouseEnter={(e)=>e.currentTarget.style.background=T.bg2}
                  onMouseLeave={(e)=>e.currentTarget.style.background='transparent'}>
                {cols.map(c => (
                  <td key={c} style={{
                    padding: '9px 18px', borderBottom: `1px solid ${T.line}`,
                    fontVariantNumeric: 'tabular-nums',
                    fontFamily: c === 'id' ? T.fMono : T.fSans,
                    fontSize: c === 'id' ? 12 : 13,
                    color: T.ink,
                    textAlign: c === 'id' || c === 'level' || c === 'module' ? 'left' : 'right',
                  }}>
                    {c === 'level' ? <Pill level={r[c]} /> :
                     c === 'score' ? (
                       <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end', width: '100%' }}>
                         <ScoreBar value={r[c]} color={(LEVEL_STYLES[r.level]||{}).fg || T.ink} width={44} height={3}/>
                         <span style={{ fontFamily: T.fMono, fontSize: 12 }}>{r[c].toFixed(2)}</span>
                       </div>
                     ) :
                     c === 'trend' ? (
                       <span style={{ color: r[c] >= 0 ? T.ok : T.danger, fontFamily: T.fMono, fontSize: 12 }}>
                         {r[c] >= 0 ? '↑' : '↓'} {Math.abs(r[c]).toFixed(2)}
                       </span>
                     ) :
                     c === 'recent' ? r[c].toFixed(2) :
                     c === 'rank' ? <span style={{ color: T.ink3, fontFamily: T.fMono, fontSize: 11 }}>{String(r[c]).padStart(2,'0')}</span> :
                     r[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// --- Timeline chart (hourly bars) ---
function TimelineChart({ data }) {
  const max = Math.max(...data);
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 110 }}>
        {data.map((v, i) => (
          <div key={i} style={{
            flex: 1, height: `${(v / max) * 100}%`, minHeight: v > 0 ? 1 : 0,
            background: i >= 16 && i <= 18 ? T.accent : T.ink2,
          }} title={`${i}:00 — ${v}`} />
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontFamily: T.fMono, fontSize: 9.5, color: T.ink3 }}>
        <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span>
      </div>
      <div style={{ marginTop: 10, fontFamily: T.fMono, fontSize: 10.5, color: T.ink3 }}>
        Peak at 16:00 · <span style={{ color: T.accent }}>current session window highlighted</span>
      </div>
    </div>
  );
}

Object.assign(window, { Sidebar, Topbar, InClassView, Leaderboard, TimelineChart });
