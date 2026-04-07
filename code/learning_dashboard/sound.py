# sound.py — Sci-fi synthesized sound effects via Web Audio API
# All sounds are generated in JavaScript using OscillatorNode/GainNode inside the package.
# Injection uses st.components.v1.html() (zero-height iframe, executes JS).
import streamlit as st
import streamlit.components.v1 as components


def _sounds_enabled() -> bool:
    return bool(st.session_state.get("sounds_enabled", True))


def _play(js_body: str) -> None:
    if not _sounds_enabled():
        return
    components.html(f"<script>{js_body}</script>", height=0)


def play_session_start() -> None:
    """Rising frequency sweep + chord stab — boot sequence (~1.8 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  var o=ctx.createOscillator(),g=ctx.createGain();
  o.type='sawtooth';
  o.frequency.setValueAtTime(80,now);
  o.frequency.exponentialRampToValueAtTime(880,now+1.2);
  g.gain.setValueAtTime(0,now);
  g.gain.linearRampToValueAtTime(0.25,now+0.1);
  g.gain.linearRampToValueAtTime(0.25,now+1.0);
  g.gain.linearRampToValueAtTime(0,now+1.4);
  o.connect(g);g.connect(ctx.destination);
  o.start(now);o.stop(now+1.5);
  [880,1108,1320].forEach(function(f){
    var o2=ctx.createOscillator(),g2=ctx.createGain();
    o2.type='sine';o2.frequency.setValueAtTime(f,now+1.0);
    g2.gain.setValueAtTime(0,now+1.0);
    g2.gain.linearRampToValueAtTime(0.15,now+1.05);
    g2.gain.exponentialRampToValueAtTime(0.001,now+1.8);
    o2.connect(g2);g2.connect(ctx.destination);
    o2.start(now+1.0);o2.stop(now+1.9);
  });
})();
""")


def play_session_end() -> None:
    """Falling frequency sweep — shutdown (~1.2 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  var o=ctx.createOscillator(),g=ctx.createGain();
  o.type='sawtooth';
  o.frequency.setValueAtTime(660,now);
  o.frequency.exponentialRampToValueAtTime(55,now+1.0);
  g.gain.setValueAtTime(0.3,now);
  g.gain.linearRampToValueAtTime(0.3,now+0.7);
  g.gain.exponentialRampToValueAtTime(0.001,now+1.2);
  o.connect(g);g.connect(ctx.destination);
  o.start(now);o.stop(now+1.3);
})();
""")


def play_selection() -> None:
    """Short crisp double-beep — student/question selected (~0.15 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  [[880,0.0],[1100,0.08]].forEach(function(p){
    var o=ctx.createOscillator(),g=ctx.createGain();
    o.type='sine';o.frequency.setValueAtTime(p[0],now+p[1]);
    g.gain.setValueAtTime(0,now+p[1]);
    g.gain.linearRampToValueAtTime(0.2,now+p[1]+0.005);
    g.gain.exponentialRampToValueAtTime(0.001,now+p[1]+0.06);
    o.connect(g);g.connect(ctx.destination);
    o.start(now+p[1]);o.stop(now+p[1]+0.08);
  });
})();
""")


def play_navigation() -> None:
    """Quick upward sweep — page navigation (~0.4 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  var o=ctx.createOscillator(),g=ctx.createGain();
  o.type='triangle';
  o.frequency.setValueAtTime(200,now);
  o.frequency.exponentialRampToValueAtTime(1200,now+0.18);
  o.frequency.exponentialRampToValueAtTime(400,now+0.35);
  g.gain.setValueAtTime(0,now);
  g.gain.linearRampToValueAtTime(0.18,now+0.04);
  g.gain.exponentialRampToValueAtTime(0.001,now+0.38);
  o.connect(g);g.connect(ctx.destination);
  o.start(now);o.stop(now+0.4);
})();
""")


def play_refresh() -> None:
    """Subtle low sine ping — data scan/refresh (~0.25 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  var o=ctx.createOscillator(),g=ctx.createGain();
  o.type='sine';o.frequency.setValueAtTime(220,now);
  g.gain.setValueAtTime(0,now);
  g.gain.linearRampToValueAtTime(0.08,now+0.01);
  g.gain.exponentialRampToValueAtTime(0.001,now+0.25);
  o.connect(g);g.connect(ctx.destination);
  o.start(now);o.stop(now+0.3);
})();
""")


def play_assistant_join() -> None:
    """Ascending 4-note arpeggio — lab assistant joined (~0.6 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  [523,659,784,1047].forEach(function(f,i){
    var t=now+i*0.12;
    var o=ctx.createOscillator(),g=ctx.createGain();
    o.type='sine';o.frequency.setValueAtTime(f,t);
    g.gain.setValueAtTime(0,t);
    g.gain.linearRampToValueAtTime(0.18,t+0.01);
    g.gain.exponentialRampToValueAtTime(0.001,t+0.18);
    o.connect(g);g.connect(ctx.destination);
    o.start(t);o.stop(t+0.22);
  });
})();
""")


def play_assignment_received() -> None:
    """Two sharp square-wave pings — assignment alert for lab assistant (~0.2 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  [0.0,0.1].forEach(function(off){
    var o=ctx.createOscillator(),g=ctx.createGain();
    o.type='square';o.frequency.setValueAtTime(1320,now+off);
    g.gain.setValueAtTime(0,now+off);
    g.gain.linearRampToValueAtTime(0.12,now+off+0.005);
    g.gain.exponentialRampToValueAtTime(0.001,now+off+0.09);
    o.connect(g);g.connect(ctx.destination);
    o.start(now+off);o.stop(now+off+0.12);
  });
})();
""")


def play_high_struggle() -> None:
    """Pulsing two-tone alarm — high-struggle student warning (~1.1 s)."""
    _play("""
(function(){
  var ctx=new(window.AudioContext||window.webkitAudioContext)();
  var now=ctx.currentTime;
  [440,330,440,330,440,330].forEach(function(f,i){
    var t=now+i*0.18;
    var o=ctx.createOscillator(),g=ctx.createGain();
    o.type='sawtooth';o.frequency.setValueAtTime(f,t);
    g.gain.setValueAtTime(0,t);
    g.gain.linearRampToValueAtTime(0.15,t+0.01);
    g.gain.exponentialRampToValueAtTime(0.001,t+0.16);
    o.connect(g);g.connect(ctx.destination);
    o.start(t);o.stop(t+0.20);
  });
})();
""")
