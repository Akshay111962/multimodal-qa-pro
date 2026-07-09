import os
import sys
import json
import gradio as gr
from fastapi import Request
from fastapi.responses import JSONResponse
from auth import register_user, login_user
from dotenv import load_dotenv

# Ensure root directory is in the Python path for backend imports
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Import backend functions
from backend_interface import process_pdf, process_image, run_agent_query

# Load environment variables
load_dotenv()

# --- HTML Landing Page Content ---
landing_page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Multimodal Q&A Pro — One agent. Three senses.</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#F4F6F8;
    --surface:#FFFFFF;
    --surface-2:#EAEDF0;
    --line:#DDE2E7;
    --text:#0E1116;
    --muted:#5C6470;
    --accent:#0EA5E9;
    --accent-soft:#0284C7;
    --accent-dim: rgba(14,165,233,0.10);
    --shadow: rgba(15,25,35,0.10);
    --nav-bg: rgba(244,246,248,0.72);
  }
  [data-theme="dark"]{
    --bg:#070A10;
    --surface:#0E121A;
    --surface-2:#141A24;
    --line:#212A38;
    --text:#EAF2F8;
    --muted:#7C8797;
    --accent:#38BDF8;
    --accent-soft:#7DD3FC;
    --accent-dim: rgba(56,189,248,0.16);
    --shadow: rgba(0,0,0,0.6);
    --nav-bg: rgba(7,10,16,0.68);
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{
    background:
      repeating-linear-gradient(0deg, transparent, transparent 39px, var(--line) 40px),
      repeating-linear-gradient(90deg, transparent, transparent 39px, var(--line) 40px),
      var(--bg);
    background-attachment:fixed;
    color:var(--text);
    font-family:'Inter',sans-serif;
    overflow-x:hidden;
    cursor:auto;
    transition:background-color .4s ease, color .4s ease;
  }
  [data-theme="dark"] body{ opacity:1; }
  body{ position:relative; }
  ::selection{background:var(--accent);color:#03131E;}
  a{color:inherit;text-decoration:none;}
 
  /* ---------- magnetic hover targets ---------- */
  .magnetic{ transition:transform .15s ease-out; }
 
  section{position:relative;z-index:1;}
 
  /* ---------- nav ---------- */
  nav{
    position:fixed;top:0;left:0;right:0;z-index:100;
    display:flex;align-items:center;justify-content:space-between;
    padding:20px 5vw;
    backdrop-filter:blur(10px);
    background:var(--nav-bg);
    border-bottom:1px solid var(--line);
  }
  .logo{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:18px;letter-spacing:-0.02em;display:flex;align-items:center;gap:8px;}
  .logo span{color:var(--accent);}
  .nav-links{display:flex;gap:36px;align-items:center;}
  .nav-links a{font-size:14px;color:var(--muted);transition:color .2s;font-weight:500;}
  .nav-links a:hover{color:var(--text);}
  .nav-right{display:flex;align-items:center;gap:14px;}
  .theme-toggle{
    width:38px;height:38px;border-radius:50%;border:1px solid var(--line);
    background:var(--surface);display:flex;align-items:center;justify-content:center;
    font-size:15px;transition:border-color .2s, transform .3s;
  }
  .theme-toggle:hover{border-color:var(--accent);transform:rotate(20deg);}
  .login-link{font-size:13.5px;font-weight:600;color:var(--muted);padding:10px 6px;transition:color .2s;}
  .login-link:hover{color:var(--text);}
  .nav-cta{
    border:1.25px solid var(--accent);color:var(--accent);font-weight:600;font-size:13.5px;
    padding:9px 19px;border-radius:100px;font-family:'Inter';background:var(--accent-dim);
    transition:transform .25s, box-shadow .25s, background .25s;
  }
  .nav-cta:hover{transform:scale(1.05);box-shadow:0 0 22px rgba(14,165,233,0.35);background:var(--accent);color:#03131E;}
 
  /* ---------- hero ---------- */
  .hero{
    min-height:92vh;display:flex;flex-direction:column;justify-content:center;
    padding:140px 5vw 60px;max-width:1400px;margin:0 auto;
  }
  .eyebrow{
    font-family:'JetBrains Mono',monospace;font-size:11.5px;letter-spacing:0.14em;
    color:var(--accent-soft);text-transform:uppercase;margin-bottom:28px;
    display:inline-flex;align-items:center;gap:10px;
    opacity:0;animation:fadeUp .7s ease forwards;animation-delay:.1s;
  }
  .eyebrow::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pulse 1.8s infinite;}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.3;}}
 
  h1.headline{
    font-family:'Space Grotesk',sans-serif;font-weight:700;
    font-size:clamp(44px, 6.6vw, 100px);line-height:0.98;letter-spacing:-0.03em;
    max-width:1150px;
  }
  h1.headline .line{display:block;overflow:hidden;}
  h1.headline .line span{display:block;opacity:0;transform:translateY(110%);animation:lineUp .8s cubic-bezier(.22,1,.36,1) forwards;}
  h1.headline .line:nth-child(1) span{animation-delay:.15s;}
  h1.headline .line:nth-child(2) span{animation-delay:.28s;}
  h1.headline .line:nth-child(3) span{animation-delay:.41s;}
  h1.headline .accent{color:var(--accent);font-style:italic;}
  @keyframes lineUp{to{opacity:1;transform:translateY(0);}}
 
  .hero-sub{
    font-size:18px;color:var(--muted);max-width:560px;margin:34px 0 40px;line-height:1.55;
    opacity:0;animation:fadeUp .7s ease forwards;animation-delay:.6s;
  }
  @keyframes fadeUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
 
  .hero-ctas{display:flex;gap:16px;flex-wrap:wrap;align-items:center;opacity:0;animation:fadeUp .7s ease forwards;animation-delay:.75s;}
  .btn-primary, .btn-ghost{
    position:relative;padding:16px 30px;border-radius:100px;font-weight:600;font-size:15px;
    display:inline-flex;align-items:center;gap:10px;transition:transform .15s ease-out, box-shadow .2s, background .2s, color .2s;
  }
  .btn-primary{background:var(--accent-dim);color:var(--accent);border:1.5px solid var(--accent);}
  .btn-primary:hover{background:var(--accent);color:#03131E;box-shadow:0 0 30px rgba(14,165,233,0.4);}
  .btn-ghost{border:1px solid var(--line);color:var(--text);}
  .btn-ghost:hover{border-color:var(--accent);}
  .hero-note{font-size:12.5px;color:var(--muted);font-family:'JetBrains Mono';}
 
  .hero-meta{
    margin-top:80px;display:flex;gap:56px;flex-wrap:wrap;
    opacity:0;animation:fadeUp .7s ease forwards;animation-delay:.9s;
  }
  .meta-item .num{font-family:'Space Grotesk';font-size:30px;font-weight:700;color:var(--text);}
  .meta-item .lbl{font-size:12px;color:var(--muted);margin-top:4px;font-family:'JetBrains Mono';letter-spacing:.03em;}
 
  /* ---------- interactive particle panel ---------- */
  .interactive-wrap{background:#04060A;border-top:1px solid var(--line);border-bottom:1px solid var(--line);}
  .interactive-head{max-width:1400px;margin:0 auto;padding:70px 5vw 20px;}
  .interactive-head .kicker{color:var(--accent-soft);}
  .interactive-head h2{color:#EAF2F8;}
  .interactive-head p{color:#7C8797;margin-top:16px;font-size:16px;max-width:560px;}
  .particle-stage{
    position:relative;width:100%;height:56vh;min-height:380px;max-height:560px;
    max-width:1400px;margin:0 auto;padding:0 5vw 70px;
  }
  .particle-stage canvas{
    display:block;width:100%;height:100%;border-radius:18px;
    border:1px solid #172033;background:#04060A;
  }
  .particle-caption{
    position:absolute;bottom:96px;left:50%;transform:translateX(-50%);
    color:#5C6B7E;font-family:'JetBrains Mono';font-size:11px;letter-spacing:0.18em;
    text-transform:uppercase;pointer-events:none;user-select:none;
  }
 
  /* ---------- marquee ---------- */
  .marquee-wrap{
    border-bottom:1px solid var(--line);
    background:var(--surface);padding:22px 0;overflow:hidden;transform:rotate(-1deg);margin:0 -2vw;
  }
  .marquee{display:flex;width:max-content;animation:scroll 26s linear infinite;}
  .marquee span{
    font-family:'Space Grotesk';font-size:28px;font-weight:600;color:var(--muted);
    padding:0 34px;white-space:nowrap;display:flex;align-items:center;gap:34px;
  }
  .marquee span.on{color:var(--accent);}
  .marquee span::after{content:'◇';font-size:12px;color:var(--line);margin-left:34px;}
  @keyframes scroll{from{transform:translateX(0);}to{transform:translateX(-50%);}}
 
  /* ---------- section shell ---------- */
  .wrap{max-width:1400px;margin:0 auto;padding:120px 5vw;}
  .section-head{max-width:640px;margin-bottom:70px;}
  .kicker{font-family:'JetBrains Mono';font-size:11.5px;letter-spacing:.14em;color:var(--accent-soft);text-transform:uppercase;margin-bottom:16px;}
  h2{font-family:'Space Grotesk';font-weight:700;font-size:clamp(28px,3.8vw,46px);letter-spacing:-0.02em;line-height:1.08;}
  .section-head p{color:var(--muted);margin-top:18px;font-size:16.5px;line-height:1.6;}
 
  .reveal{opacity:0;transform:translateY(28px);transition:opacity .7s ease, transform .7s cubic-bezier(.22,1,.36,1);}
  .reveal.in{opacity:1;transform:translateY(0);}
 
  /* ---------- bento ---------- */
  .bento{display:grid;grid-template-columns:repeat(6,1fr);gap:18px;}
  .card{
    background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:32px;
    transition:border-color .3s, transform .3s;position:relative;overflow:hidden;
  }
  .card:hover{border-color:rgba(14,165,233,0.45);transform:translateY(-4px);}
  .card.big{grid-column:span 4;grid-row:span 2;padding:40px;}
  .card.small{grid-column:span 2;}
  .card .icon{
    width:44px;height:44px;border-radius:10px;background:var(--accent-dim);border:1px solid rgba(14,165,233,0.25);
    display:flex;align-items:center;justify-content:center;margin-bottom:22px;font-size:19px;
  }
  .card h3{font-family:'Space Grotesk';font-size:19px;font-weight:600;margin-bottom:10px;}
  .card p{color:var(--muted);font-size:14.5px;line-height:1.55;}
  .card .tag{
    position:absolute;top:32px;right:32px;font-family:'JetBrains Mono';font-size:10.5px;
    color:var(--muted);border:1px solid var(--line);padding:4px 10px;border-radius:100px;
  }
  .mono-line{
    font-family:'JetBrains Mono';font-size:12.5px;color:var(--accent-soft);
    margin-top:24px;padding-top:18px;border-top:1px dashed var(--line);
  }
 
  /* ---------- product preview ---------- */
  .preview-shell{
    background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;
    box-shadow:0 40px 100px -30px var(--shadow);
  }
  .preview-lock{
    display:flex;align-items:center;gap:8px;font-family:'JetBrains Mono';font-size:11px;
    color:var(--accent-soft);border:1px solid var(--line);padding:6px 12px;border-radius:100px;
    width:fit-content;margin-bottom:24px;
  }
  .preview-top{display:flex;align-items:center;gap:10px;padding:16px 20px;border-bottom:1px solid var(--line);}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--surface-2);border:1px solid var(--line);}
  .preview-bar{
    flex:1;background:var(--surface-2);border-radius:100px;padding:7px 14px;font-family:'JetBrains Mono';
    font-size:11.5px;color:var(--muted);margin-left:8px;
  }
  .preview-body{display:grid;grid-template-columns:260px 1fr;min-height:420px;}
  .preview-side{border-right:1px solid var(--line);padding:26px;}
  .preview-tabs{display:flex;gap:8px;margin-bottom:22px;}
  .ptab{font-size:12.5px;font-weight:600;padding:8px 14px;border-radius:8px;color:var(--muted);}
  .ptab.on{background:var(--accent);color:#03131E;}
  .plabel{font-family:'JetBrains Mono';font-size:10.5px;color:var(--accent-soft);letter-spacing:.08em;margin-bottom:12px;}
  .pfile{display:flex;align-items:center;gap:10px;background:var(--surface-2);padding:10px 12px;border-radius:10px;margin-bottom:10px;font-size:13px;}
  .pfile .fi{width:26px;height:26px;border-radius:6px;background:var(--accent-dim);display:flex;align-items:center;justify-content:center;font-size:12px;}
  .ptrace{font-family:'JetBrains Mono';font-size:11px;color:var(--muted);line-height:2;}
  .ptrace .go{color:var(--accent-soft);}
  .preview-main{padding:30px;display:flex;flex-direction:column;justify-content:space-between;}
  .pbubble-user{
    align-self:flex-end;background:var(--accent);color:#03131E;font-weight:600;font-size:14px;
    padding:14px 18px;border-radius:16px 16px 4px 16px;max-width:340px;
  }
  .pbubble-ai{
    background:var(--surface-2);border:1px solid var(--line);padding:18px 20px;border-radius:16px 16px 16px 4px;
    max-width:420px;font-size:14.5px;line-height:1.6;color:var(--text);margin-top:16px;
  }
  .pbubble-ai .aitag{font-family:'JetBrains Mono';font-size:10px;color:var(--accent-soft);margin-bottom:8px;letter-spacing:.06em;}
  .pinput{margin-top:20px;background:var(--surface-2);border:1px solid var(--line);border-radius:100px;padding:14px 20px;color:var(--muted);font-size:13.5px;}
 
  /* ---------- footer cta ---------- */
  .cta-final{
    text-align:center;padding:150px 5vw;position:relative;
  }
  .cta-final h2{font-size:clamp(34px,5.6vw,68px);max-width:900px;margin:0 auto 30px;}
  .cta-final .btn-primary{padding:20px 42px;font-size:17px;}
 
  footer{
    border-top:1px solid var(--line);padding:40px 5vw;
    display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;
  }
  footer .fmuted{color:var(--muted);font-size:13px;font-family:'JetBrains Mono';}
  footer .flinks{display:flex;gap:26px;}
  footer .flinks a{color:var(--muted);font-size:13.5px;transition:color .2s;}
  footer .flinks a:hover{color:var(--accent);}
 
  @media(max-width:860px){
    .bento{grid-template-columns:1fr 1fr;}
    .card.big{grid-column:span 2;}
    .card.small{grid-column:span 2;}
    .preview-body{grid-template-columns:1fr;}
    .preview-side{border-right:none;border-bottom:1px solid var(--line);}
    .nav-links{display:none;}
    .hero-meta{gap:32px;}
    .particle-caption{bottom:40px;}
  }

  /* ===== goo filter container (mode: blob) ===== */
  #gooLayer{ position:fixed; inset:0; z-index:150; pointer-events:none; filter:url(#gooFilter); display:block; }
  .goo-dot{
    position:absolute; border-radius:50%; background:var(--accent);
    top:0; left:0; transform:translate(-50%,-50%);
  }
</style>
</head>
<body style="cursor:none;">
 
<!-- SVG goo filter definition -->
<svg width="0" height="0" style="position:absolute;">
  <filter id="gooFilter">
    <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="blur" />
    <feColorMatrix in="blur" mode="matrix"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 24 -10" result="goo" />
  </filter>
</svg>
<div id="gooLayer"></div>

<nav>
  <div class="logo">MQA<span>°</span></div>
  <div class="nav-links">
    <a href="#how">How it thinks</a>
    <a href="#preview">Preview</a>
    <a href="#stack">Stack</a>
  </div>
  <div class="nav-right">
    <button class="theme-toggle magnetic" id="themeToggle" aria-label="Toggle dark mode">🌙</button>
    <a href="#" onclick="window.parent.postMessage('go_login', '*'); return false;" class="login-link">Log in</a>
    <a href="#" onclick="window.parent.postMessage('go_signup', '*'); return false;" class="nav-cta magnetic">Sign up free</a>
  </div>
</nav>
 
<section class="hero">
  <div class="eyebrow">GenAI Summer of Code · Hackathon 2026 · Team dev-x</div>
  <h1 class="headline">
    <span class="line"><span>One brain.</span></span>
    <span class="line"><span>Three <span class="accent">senses.</span></span></span>
    <span class="line"><span>Zero guesswork.</span></span>
  </h1>
  <p class="hero-sub">Upload a PDF. Drop in a photo. Ask anything. One agent decides — on its own — whether to check your documents, the live web, or the image, then hands back one honest answer.</p>
  <div class="hero-ctas">
    <a href="#" onclick="window.parent.postMessage('go_signup', '*'); return false;" class="btn-primary magnetic">Create your account →</a>
    <a href="https://github.com/Akshay111962/multimodal-qa-pro" target="_blank" class="btn-ghost magnetic">View on GitHub</a>
  </div>
  <div class="hero-meta">
    <div class="meta-item"><div class="num">03</div><div class="lbl">TOOLS, ONE AGENT</div></div>
    <div class="meta-item"><div class="num">12hr</div><div class="lbl">BUILD WINDOW</div></div>
    <div class="meta-item"><div class="num">100%</div><div class="lbl">LIVE, NOT SLIDES</div></div>
  </div>
</section>
 
<div class="interactive-wrap">
  <div class="interactive-head reveal">
    <div class="kicker">Interactive</div>
    <h2>It reacts to you.</h2>
    <p>Move your cursor through it. Every particle responds instantly — the same way the agent adjusts its reasoning to whatever you ask it.</p>
  </div>
  <div class="particle-stage reveal">
    <canvas id="particleCanvas"></canvas>
    <div class="particle-caption">Move your cursor to interact</div>
  </div>
</div>
 
<div class="marquee-wrap">
  <div class="marquee">
    <span>DOCUMENTS</span><span class="on">LIVE WEB</span><span>IMAGES</span>
    <span>DOCUMENTS</span><span class="on">LIVE WEB</span><span>IMAGES</span>
    <span>DOCUMENTS</span><span class="on">LIVE WEB</span><span>IMAGES</span>
    <span>DOCUMENTS</span><span class="on">LIVE WEB</span><span>IMAGES</span>
  </div>
</div>
 
<section id="how" class="wrap">
  <div class="section-head reveal">
    <div class="kicker">How it thinks</div>
    <h2>Three tools. One decision engine.</h2>
    <p>The agent reads your question first, then figures out what it actually needs — never all three by default.</p>
  </div>
 
  <div class="bento">
    <div class="card big reveal">
      <span class="tag">core</span>
      <div class="icon">◈</div>
      <h3>ReAct Agent</h3>
      <p>Reasons, acts, observes, repeats. Built on <b>create_react_agent</b> with a recursion limit of 12 — it stops second-guessing itself once it's confident.</p>
      <div class="mono-line">→ routes per question, not per default</div>
    </div>
    <div class="card small reveal">
      <div class="icon">▤</div>
      <h3>search_documents</h3>
      <p>RAG over ChromaDB — every answer traceable to a real chunk, with page numbers.</p>
    </div>
    <div class="card small reveal">
      <div class="icon">◎</div>
      <h3>search_web</h3>
      <p>DuckDuckGo lookup for anything your PDFs don't cover yet.</p>
    </div>
    <div class="card small reveal">
      <div class="icon">◐</div>
      <h3>describe_image</h3>
      <p>Groq Vision reads charts, screenshots, and photos — then cross-checks them against your docs.</p>
    </div>
    <div class="card small reveal">
      <div class="icon">≡</div>
      <h3>Live trace</h3>
      <p>Every tool call is visible, streamed in real time — never a black box.</p>
    </div>
  </div>
</section>
 
<section id="preview" class="wrap">
  <div class="section-head reveal">
    <div class="kicker">Preview</div>
    <h2>What's waiting inside.</h2>
    <p>Create an account, upload a PDF or a photo, and start asking — this is the workspace you land in.</p>
  </div>
 
  <div class="reveal">
    <div class="preview-lock">🔒 Unlocks after sign up</div>
    <div class="preview-shell">
      <div class="preview-top">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="preview-bar">app.multimodal-qa-pro.dev/workspace</div>
      </div>
      <div class="preview-body">
        <div class="preview-side">
          <div class="preview-tabs">
            <div class="ptab on">Chat</div>
            <div class="ptab">PDF</div>
            <div class="ptab">Image</div>
          </div>
          <div class="plabel">UPLOADS</div>
          <div class="pfile"><div class="fi">▤</div> report.pdf</div>
          <div class="pfile"><div class="fi">◐</div> chart.png</div>
          <div class="plabel" style="margin-top:22px;">REASONING TRACE</div>
          <div class="ptrace">
            <div class="go">✓ describe_image</div>
            <div class="go">✓ search_documents</div>
            <div>● synthesizing…</div>
          </div>
        </div>
        <div class="preview-main">
          <div>
            <div class="pbubble-user">What's in this chart, and is it in my report?</div>
            <div class="pbubble-ai">
              <div class="aitag">AGENT ANSWER</div>
              This is a quarterly revenue bar chart. Your uploaded report.pdf discusses the same Q3 increase on page 4 — both sources agree.
            </div>
          </div>
          <div class="pinput">Ask a follow-up…</div>
        </div>
      </div>
    </div>
  </div>
</section>
 
<section id="stack" class="wrap" style="padding-top:0;">
  <div class="section-head reveal">
    <div class="kicker">Built with</div>
    <h2>Free-tier, open, no shortcuts.</h2>
  </div>
  <div class="bento" style="grid-template-columns:repeat(4,1fr);">
    <div class="card reveal"><h3 style="font-size:16px;">LangGraph</h3><p>Agent orchestration</p></div>
    <div class="card reveal"><h3 style="font-size:16px;">ChromaDB</h3><p>Vector retrieval</p></div>
    <div class="card reveal"><h3 style="font-size:16px;">Groq Vision</h3><p>Image understanding</p></div>
    <div class="card reveal"><h3 style="font-size:16px;">HF Spaces</h3><p>Live deployment</p></div>
  </div>
</section>
 
<section class="cta-final">
  <div class="kicker reveal" style="justify-content:center;display:flex;">Team dev-x</div>
  <h2 class="reveal">Ready to see<br>it <span style="color:var(--accent);font-style:italic;">think?</span></h2>
  <div class="hero-ctas reveal" style="justify-content:center;">
    <a href="#" onclick="window.parent.postMessage('go_signup', '*'); return false;" class="btn-primary magnetic">Create your account →</a>
  </div>
</section>
 
<footer>
  <div class="fmuted">© 2026 · Achyut Pathak · Akshay Purohit</div>
  <div class="flinks">
    <a href="https://github.com/Akshay111962/multimodal-qa-pro" target="_blank">GitHub</a>
    <a href="#" onclick="window.parent.postMessage('go_login', '*'); return false;">Log in</a>
    <a href="#how">How it works</a>
  </div>
</footer>
 
<script>
  // theme toggle — light is default, dark is black+navy blend (not pure black)
  const root = document.documentElement;
  const themeBtn = document.getElementById('themeToggle');
  themeBtn.addEventListener('click', ()=>{
    const isDark = root.getAttribute('data-theme') === 'dark';
    const nextTheme = isDark ? 'light' : 'dark';
    root.setAttribute('data-theme', nextTheme);
    themeBtn.textContent = isDark ? '🌙' : '☀️';
    window.parent.postMessage({action: 'toggle_theme', theme: nextTheme}, '*');
  });

  window.addEventListener('message', (event) => {
    const data = event.data;
    if (data.action === 'apply_theme') {
      root.setAttribute('data-theme', data.theme);
      themeBtn.textContent = data.theme === 'dark' ? '☀️' : '🌙';
    }
  });
 
  // magnetic pull — buttons, cards, theme toggle
  document.querySelectorAll('.magnetic, .card').forEach(btn=>{
    btn.addEventListener('mousemove', e=>{
      const r = btn.getBoundingClientRect();
      const x = e.clientX - r.left - r.width/2;
      const y = e.clientY - r.top - r.height/2;
      const strength = btn.classList.contains('card') ? 0.06 : 0.25;
      btn.style.transform = `translate(${x*strength}px, ${y*strength}px)`;
    });
    btn.addEventListener('mouseleave', ()=>{ btn.style.transform='translate(0,0)'; });
  });
 
  // scroll reveal
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); } });
  }, {threshold:0.15});
  document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
 
  // ---------- interactive particle-text canvas (adapted from provided snippet) ----------
  (function(){
    const stage = document.querySelector('.particle-stage');
    const canvas = document.getElementById('particleCanvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    let particleArray = [];
    const mouse = { x: undefined, y: undefined, radius: 90 };
 
    function getRect(){ return canvas.getBoundingClientRect(); }
 
    canvas.addEventListener('mousemove', (event) => {
      const rect = getRect();
      mouse.x = event.clientX - rect.left;
      mouse.y = event.clientY - rect.top;
    });
    canvas.addEventListener('mouseleave', () => {
      mouse.x = undefined; mouse.y = undefined;
    });
 
    class Particle {
      constructor(x, y) {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.baseX = x;
        this.baseY = y;
        this.size = Math.random() * 1.8 + 1;
        this.density = (Math.random() * 30) + 1;
        this.color = '#38bdf8';
      }
      draw() {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fill();
      }
      update() {
        if (mouse.x === undefined) {
          if (this.x !== this.baseX) { this.x -= (this.x - this.baseX) / 10; }
          if (this.y !== this.baseY) { this.y -= (this.y - this.baseY) / 10; }
          return;
        }
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.hypot(dx, dy);
        let forceDirectionX = dx / (distance || 1);
        let forceDirectionY = dy / (distance || 1);
        let maxDistance = mouse.radius;
        let force = (maxDistance - distance) / maxDistance;
        let directionX = forceDirectionX * force * this.density;
        let directionY = forceDirectionY * force * this.density;
        if (distance < mouse.radius) {
          this.x -= directionX;
          this.y -= directionY;
        } else {
          if (this.x !== this.baseX) { this.x -= (this.x - this.baseX) / 10; }
          if (this.y !== this.baseY) { this.y -= (this.y - this.baseY) / 10; }
        }
      }
    }
 
    function init() {
      const rect = getRect();
      canvas.width = rect.width;
      canvas.height = rect.height;
      particleArray = [];
      ctx.fillStyle = 'white';
      const fontSize = Math.floor(canvas.height * 0.5);
      ctx.font = `700 ${fontSize}px "Space Grotesk", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('MQA', canvas.width / 2, canvas.height / 2);
      const textCoordinates = ctx.getImageData(0, 0, canvas.width, canvas.height);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const gap = Math.max(3, Math.floor(canvas.width / 260));
      for (let y = 0; y < textCoordinates.height; y += gap) {
        for (let x = 0; x < textCoordinates.width; x += gap) {
          if (textCoordinates.data[(y * 4 * textCoordinates.width) + (x * 4) + 3] > 128) {
            particleArray.push(new Particle(x, y));
          }
        }
      }
    }
 
    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < particleArray.length; i++) {
        particleArray[i].draw();
        particleArray[i].update();
      }
      requestAnimationFrame(animate);
    }
 
    init();
    animate();
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(init, 150);
    });
  })();

  /* ===== MODE 1: gooey blob trail ===== */
  let blobMx = window.innerWidth/2, blobMy = window.innerHeight/2;
  document.addEventListener('mousemove', e=>{ blobMx = e.clientX; blobMy = e.clientY; });

  const gooLayer = document.getElementById('gooLayer');
  const DOT_COUNT = 9;
  const gooDots = [];
  for(let i=0;i<DOT_COUNT;i++){
    const d = document.createElement('div');
    d.className = 'goo-dot';
    const size = 26 - i*1.6;
    d.style.width = size+'px'; d.style.height = size+'px';
    gooLayer.appendChild(d);
    gooDots.push({el:d, x:blobMx, y:blobMy});
  }
  function animateGoo(){
    let px = blobMx, py = blobMy;
    gooDots.forEach((dot, i)=>{
      dot.x += (px - dot.x) * 0.32;
      dot.y += (py - dot.y) * 0.32;
      dot.el.style.left = dot.x+'px';
      dot.el.style.top = dot.y+'px';
      px = dot.x; py = dot.y;
    });
    requestAnimationFrame(animateGoo);
  }
  animateGoo();
</script>
 
</body>
</html>
"""

login_page_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auth</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#F4F6F8; --surface:#FFFFFF; --surface-2:#EAEDF0; --line:#DDE2E7;
    --text:#0E1116; --muted:#5C6470; --accent:#0EA5E9; --accent-soft:#0284C7;
    --accent-dim: rgba(14,165,233,0.10); --shadow: rgba(15,25,35,0.10);
  }
  .dark, [data-theme="dark"]{
    --bg:#070A10; --surface:#0E121A; --surface-2:#141A24; --line:#212A38;
    --text:#EAF2F8; --muted:#7C8797; --accent:#38BDF8; --accent-soft:#7DD3FC;
    --accent-dim: rgba(56,189,248,0.16); --shadow: rgba(0,0,0,0.6);
  }

  body {
    margin: 0;
    background-color: var(--bg);
    background-image: 
      linear-gradient(var(--line) 1px, transparent 1px),
      linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size: 40px 40px;
    color: var(--text);
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    overflow: hidden;
    transition: background-color 0.3s, color 0.3s;
  }
  
  .top-bar {
    position: fixed;
    top: 0; left: 0; right: 0;
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
  }
  .top-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .back-btn {
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    cursor: pointer;
    transition: color 0.2s;
  }
  .back-btn:hover { color: var(--text); }
  
  .top-right {
    display: flex;
    align-items: center;
    gap: 24px;
  }
  .theme-toggle {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: var(--muted);
    transition: color 0.2s, transform 0.2s;
  }
  .theme-toggle:hover { color: var(--text); transform: scale(1.1); }
  
  .logo { font-family: 'Space Grotesk'; font-weight: 700; font-size: 18px; color: var(--text); }
  .logo span { color: var(--accent); }

  .wrp {
    perspective: 1200px;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .crd {
    width: 380px;
    height: 520px;
    position: relative;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
  }
  
  .crd.flp {
    transform: rotateY(180deg);
  }
  
  .m_cnt {
    background: var(--chat-bg) !important;
    background-image:
      linear-gradient(var(--grid-line) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid-line) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    flex: 1 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    border: none !important;
    padding: 0 !important;
    overflow: hidden !important;
  }
  
  .m_cnt .wrap, .m_cnt .contain, .m_cnt > .wrap, .m_cnt > .contain {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .sidebar-left {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--line) !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
    overflow: hidden !important;
  }

  .sidebar-left .wrap, .sidebar-left .contain, .sidebar-left > .wrap, .sidebar-left > .contain {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
  }

  .fce {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 40px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 50px -12px var(--shadow);
  }
  
  .bck {
    transform: rotateY(180deg);
  }
  
  .header-area { margin-bottom: 30px; }
  h2 {
    margin: 0 0 6px 0;
    color: var(--text);
    font-size: 2.2em;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -1px;
  }
  .subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
  }
  
  .input-group {
    margin-bottom: 16px;
  }
  .input-group label {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
  
  input {
    width: 100%;
    padding: 15px;
    background: var(--surface-2);
    border: 1px solid var(--line);
    color: var(--text);
    border-radius: 8px;
    box-sizing: border-box;
    outline: none;
    font-size: 15px;
    font-family: 'Inter', sans-serif;
    transition: all 0.3s;
  }
  
  input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 15px var(--accent-dim);
  }
  
  button {
    width: 100%;
    padding: 15px;
    background: var(--accent);
    color: #000;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 15px;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s;
    margin-top: 10px;
  }
  
  button:hover {
    background: var(--accent-soft);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px var(--accent-dim);
  }
  
  .swp {
    margin-top: auto;
    text-align: center;
    font-size: 12.5px;
    color: var(--muted);
    cursor: pointer;
  }
  
  .swp span {
    color: var(--accent);
    font-weight: 600;
  }
</style>
</head>
<body class="dark">

<div class="top-bar">
  <div class="top-left">
    <div class="back-btn" onclick="window.parent.postMessage('go_landing', '*');">← Back to site</div>
  </div>
  <div class="top-right">
    <button class="theme-toggle" id="themeBtn" title="Toggle Light/Dark Mode">🌓</button>
    <div class="logo">MQA<span>°</span></div>
  </div>
</div>

<div class="wrp" id="w">
  <div class="crd" id="c">
    <!-- FRONT: LOGIN -->
    <div class="fce frt">
      <div class="header-area">
        <h2>Log in.</h2>
        <div class="subtitle">// access your workspace</div>
      </div>
      
      <form onsubmit="(function(e){ e.preventDefault(); var btn=e.target.querySelector('button'); btn.disabled=true; btn.innerText='Logging in...'; var email=e.target.querySelector('input[type=email]').value, pass=e.target.querySelector('input[type=password]').value; fetch(window.parent.location.origin+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,password:pass})}).then(function(r){return r.json();}).then(function(res){ if(res.success){ window.parent.postMessage({action:'login_success',name:res.name,email:res.email},'*'); }else{ var err=document.getElementById('login-error'); err.innerText=res.message; err.style.display='block'; btn.disabled=false; btn.innerText='Continue →'; } }).catch(function(err){ var errDiv=document.getElementById('login-error'); errDiv.innerText='Connection error. Please retry.'; errDiv.style.display='block'; btn.disabled=false; btn.innerText='Continue →'; }); })(event); return false;">
        <div class="input-group">
          <label>Email</label>
          <input type="email" placeholder="you@example.com" required>
        </div>
        <div class="input-group">
          <label>Password</label>
          <input type="password" placeholder="••••••••" required>
        </div>
        <div class="auth-error" id="login-error" style="display:none;"></div>
        <button type="submit">Continue →</button>
      </form>
      
      <div class="swp" id="s1">Don't have an account? <span>Sign up</span></div>
    </div>
    
    <!-- BACK: SIGNUP -->
    <div class="fce bck">
      <div class="header-area">
        <h2>Sign up.</h2>
        <div class="subtitle">// create your account</div>
      </div>
      
      <form onsubmit="(function(e){ e.preventDefault(); var btn=e.target.querySelector('button'); btn.disabled=true; btn.innerText='Creating account...'; var name=e.target.querySelector('input[type=text]').value, email=e.target.querySelector('input[type=email]').value, pass=e.target.querySelector('input[type=password]').value; fetch(window.parent.location.origin+'/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,email:email,password:pass})}).then(function(r){return r.json();}).then(function(res){ if(res.success){ var s=document.getElementById('signup-success'); s.innerText='Account created! Redirecting to login...'; s.style.display='block'; setTimeout(function(){ document.getElementById('s2').click(); btn.disabled=false; btn.innerText='Create account →'; },1500); }else{ var err=document.getElementById('signup-error'); err.innerText=res.message; err.style.display='block'; btn.disabled=false; btn.innerText='Create account →'; } }).catch(function(err){ var errDiv=document.getElementById('signup-error'); errDiv.innerText='Connection error. Please retry.'; errDiv.style.display='block'; btn.disabled=false; btn.innerText='Create account →'; }); })(event); return false;">
        <div class="input-group">
          <label>Name</label>
          <input type="text" placeholder="John Doe" required>
        </div>
        <div class="input-group">
          <label>Email</label>
          <input type="email" placeholder="you@example.com" required>
        </div>
        <div class="input-group">
          <label>Password</label>
          <input type="password" placeholder="min 8 characters" required>
        </div>
        <div class="auth-error" id="signup-error" style="display:none;"></div>
        <div class="auth-success" id="signup-success" style="display:none;"></div>
        <button type="submit">Create account →</button>
      </form>
      
      <div class="swp" id="s2">Already have an account? <span>Log in</span></div>
    </div>
  </div>
</div>

<script>
  // Theme Toggle Logic
  const themeBtn = document.getElementById('themeBtn');
  themeBtn.addEventListener('click', () => {
    const isDark = document.body.classList.toggle('dark');
    document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
    window.parent.postMessage({action: 'toggle_theme', theme: isDark ? 'dark' : 'light'}, '*');
  });

  const w = document.getElementById('w');
  const c = document.getElementById('c');
  const s1 = document.getElementById('s1');
  const s2 = document.getElementById('s2');

  s1.addEventListener('click', () => c.classList.add('flp'));
  s2.addEventListener('click', () => c.classList.remove('flp'));

  w.addEventListener('mousemove', (e) => {
    let rx = (window.innerWidth / 2 - e.pageX) / 25;
    let ry = (window.innerHeight / 2 - e.pageY) / 25;
    
    if (c.classList.contains('flp')) {
      c.style.transform = `rotateY(180deg) rotateX(${ry}deg) rotateZ(${rx}deg)`;
    } else {
      c.style.transform = `rotateX(${-ry}deg) rotateY(${-rx}deg)`;
    }
  });


  window.addEventListener('message', (event) => {
    const data = event.data;
    if (data.action === 'signup_success') {
      const successDiv = document.getElementById('signup-success');
      const errorDiv = document.getElementById('signup-error');
      if (successDiv) {
        successDiv.innerText = data.message;
        successDiv.style.display = 'block';
      }
      if (errorDiv) errorDiv.style.display = 'none';
      setTimeout(() => {
        // Clear inputs and flip card back to login face
        document.getElementById('c').classList.remove('flp');
        if (successDiv) successDiv.style.display = 'none';
      }, 2000);
    } else if (data.action === 'signup_error') {
      const errorDiv = document.getElementById('signup-error');
      if (errorDiv) {
        errorDiv.innerText = data.message;
        errorDiv.style.display = 'block';
      }
    } else if (data.action === 'login_error') {
      const errorDiv = document.getElementById('login-error');
      if (errorDiv) {
        errorDiv.innerText = data.message;
        errorDiv.style.display = 'block';
      }
      const btn = document.querySelector('.frt button');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Continue →';
      }
    } else if (data.action === 'signup_error') {
      const errorDiv = document.getElementById('signup-error');
      if (errorDiv) {
        errorDiv.innerText = data.message;
        errorDiv.style.display = 'block';
      }
      const btn = document.querySelector('.bck button');
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Create account →';
      }
    } else if (data.action === 'apply_theme') {
      if (data.theme === 'dark') {
        document.body.classList.add('dark');
        document.body.setAttribute('data-theme', 'dark');
      } else {
        document.body.classList.remove('dark');
        document.body.setAttribute('data-theme', 'light');
      }
    }
  });

  w.addEventListener('mouseleave', () => {
    c.style.transform = c.classList.contains('flp') ? 'rotateY(180deg)' : 'rotateX(0) rotateY(0)';
  });
</script>

</body>
</html>
"""


# --- Custom Workspace HTML ---
workspace_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Workspace — Multimodal Q&A Pro</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<script>
  (function(){
    let theme = 'dark';
    document.documentElement.setAttribute('data-theme', theme);

    function syncToggleIcons(){
      document.querySelectorAll('.theme-toggle').forEach(btn=>{
        btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      });
    }
    window.toggleTheme = function(){
      theme = theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', theme);
      syncToggleIcons();
      // Notify parent frame
      try { parent.postMessage({action:'toggle_theme', theme: theme}, '*'); } catch(e){}
    };
    document.addEventListener('DOMContentLoaded', function(){
      syncToggleIcons();
    });
    // Listen for theme sync from parent
    window.addEventListener('message', function(e){
      if(e.data && e.data.action === 'apply_theme'){
        theme = e.data.theme;
        document.documentElement.setAttribute('data-theme', theme);
        syncToggleIcons();
      }
      if(e.data && e.data.action === 'set_user'){
        const nameEl = document.querySelector('.user-name');
        const avatarEl = document.querySelector('.avatar');
        if(nameEl) nameEl.textContent = e.data.name || 'User';
        if(avatarEl) avatarEl.textContent = (e.data.name || 'U').substring(0,2).toUpperCase();
      }
    });
  })();
</script>
<style>
  :root{
    --bg:#F4F6F8; --surface:#FFFFFF; --surface-2:#EAEDF0; --line:#DDE2E7;
    --text:#0E1116; --muted:#5C6470; --accent:#0EA5E9; --accent-soft:#0284C7;
    --accent-dim: rgba(14,165,233,0.10); --shadow: rgba(15,25,35,0.10);
    --sidebar-bg:#EFF1F3; --bubble-user:#E4E7EA;
  }
  [data-theme="dark"]{
    --bg:#070A10; --surface:#0E121A; --surface-2:#141A24; --line:#212A38;
    --text:#EAF2F8; --muted:#7C8797; --accent:#38BDF8; --accent-soft:#7DD3FC;
    --accent-dim: rgba(56,189,248,0.16); --shadow: rgba(0,0,0,0.6);
    --sidebar-bg:#0B0E15; --bubble-user:#1B222F;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{
    background:var(--bg); color:var(--text); font-family:'Inter',sans-serif;
    height:100vh; overflow:hidden; transition:background-color .3s, color .3s;
  }
  a{color:inherit;text-decoration:none;}
  ::selection{background:var(--accent);color:#03131E;}
  .magnetic{ transition:transform .15s ease-out; }
  button{ font-family:'Inter'; cursor:pointer; border:none; background:none; color:inherit; }

  .app{ display:flex; height:100vh; }

  /* ================= SIDEBAR ================= */
  .sidebar{
    width:272px; flex-shrink:0; background:var(--sidebar-bg); border-right:1px solid var(--line);
    display:flex; flex-direction:column; padding:18px 14px;
  }
  .sb-logo{
    font-family:'Space Grotesk'; font-weight:700; font-size:18px; padding:8px 8px 18px;
    display:flex; align-items:center; gap:8px;
  }
  .sb-logo span{ color:var(--accent); }

  .new-chat-btn{
    display:flex; align-items:center; gap:10px; width:100%; padding:11px 12px;
    border:1px solid var(--line); border-radius:10px; background:var(--surface);
    font-size:13.5px; font-weight:600; color:var(--text); margin-bottom:22px;
    transition:border-color .2s, background .2s;
  }
  .new-chat-btn:hover{ border-color:var(--accent); background:var(--accent-dim); }
  .new-chat-btn .plus{ color:var(--accent); font-size:16px; font-weight:700; }

  .sb-section-label{
    font-family:'JetBrains Mono'; font-size:10.5px; letter-spacing:.1em; color:var(--muted);
    text-transform:uppercase; padding:0 8px 10px;
  }
  .history-list{ flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:2px; }
  .history-item{
    display:flex; align-items:center; gap:10px; padding:10px 10px; border-radius:8px;
    font-size:13px; color:var(--muted); transition:background .2s, color .2s; position:relative; cursor:pointer;
  }
  .history-item:hover{ background:var(--surface); color:var(--text); }
  .history-item.active{ background:var(--accent-dim); color:var(--accent-soft); font-weight:600; }
  .history-item .h-icon{ font-size:12px; opacity:.7; flex-shrink:0; }
  .history-item .h-title{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; }
  .history-group-label{
    font-family:'JetBrains Mono'; font-size:10px; color:var(--muted); opacity:.6;
    padding:14px 10px 6px; text-transform:uppercase; letter-spacing:.08em;
  }
  .history-group-label:first-child{ padding-top:4px; }

  .sb-bottom{ border-top:1px solid var(--line); padding-top:12px; margin-top:10px; position:relative; }
  .user-row{
    display:flex; align-items:center; gap:10px; padding:8px; border-radius:10px;
    transition:background .2s; width:100%;
  }
  .user-row:hover{ background:var(--surface); }
  .avatar{
    width:30px; height:30px; border-radius:50%; background:var(--accent); color:#03131E;
    display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700;
    font-family:'Space Grotesk'; flex-shrink:0;
  }
  .user-name{ font-size:13px; font-weight:600; flex:1; text-align:left; }
  .user-chevron{ color:var(--muted); font-size:11px; }

  .user-menu{
    position:absolute; bottom:56px; left:0; width:100%; background:var(--surface);
    border:1px solid var(--line); border-radius:10px; padding:6px; display:none;
    box-shadow:0 20px 50px -12px var(--shadow); z-index:20;
  }
  .user-menu.open{ display:block; }
  .user-menu button{
    width:100%; text-align:left; padding:9px 10px; border-radius:7px; font-size:13px;
    display:flex; align-items:center; gap:10px; color:var(--text); transition:background .2s;
  }
  .user-menu button:hover{ background:var(--surface-2); }

  /* ================= MAIN ================= */
  .main{ flex:1; display:flex; flex-direction:column; min-width:0; }
  .main-top{
    display:flex; align-items:center; justify-content:space-between; padding:16px 26px;
    border-bottom:1px solid var(--line); flex-shrink:0;
  }
  .chat-title{ font-family:'Space Grotesk'; font-weight:600; font-size:14.5px; color:var(--muted); }
  .main-top-right{ display:flex; align-items:center; gap:10px; }
  .icon-btn{
    width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center;
    color:var(--muted); font-size:14px; transition:background .2s, color .2s;
  }
  .icon-btn:hover{ background:var(--surface-2); color:var(--text); }

  .chat-area{ flex:1; overflow-y:auto; }
  .chat-inner{ max-width:760px; margin:0 auto; padding:40px 24px 20px; }

  /* welcome / empty state */
  .welcome{ display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; text-align:center; padding:0 24px; }
  .welcome .w-icon{
    width:52px; height:52px; border-radius:14px; background:var(--accent-dim); border:1px solid var(--line);
    display:flex; align-items:center; justify-content:center; font-size:22px; margin-bottom:20px;
  }
  .welcome h1{ font-family:'Space Grotesk'; font-size:28px; font-weight:700; margin-bottom:10px; letter-spacing:-0.01em; }
  .welcome p{ color:var(--muted); font-size:14px; max-width:420px; margin-bottom:30px; line-height:1.5; }
  .suggestion-row{ display:flex; gap:10px; flex-wrap:wrap; justify-content:center; max-width:600px; }
  .suggestion-chip{
    border:1px solid var(--line); background:var(--surface); padding:10px 16px; border-radius:100px;
    font-size:12.5px; color:var(--text); transition:border-color .2s, background .2s; cursor:pointer;
  }
  .suggestion-chip:hover{ border-color:var(--accent); background:var(--accent-dim); }

  /* messages */
  .msg{ margin-bottom:28px; }
  .msg-user{ display:flex; justify-content:flex-end; }
  .msg-user .bubble{
    background:var(--bubble-user); color:var(--text); padding:12px 16px; border-radius:16px 16px 4px 16px;
    max-width:70%; font-size:14.5px; line-height:1.5;
  }
  .msg-assistant{ display:flex; gap:12px; }
  .msg-assistant .a-avatar{
    width:26px; height:26px; border-radius:7px; background:var(--accent); flex-shrink:0; margin-top:2px;
    display:flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; color:#03131E;
    font-family:'Space Grotesk';
  }
  .msg-assistant .a-content{ flex:1; min-width:0; padding-top:2px; }
  .msg-assistant .a-text{ font-size:14.5px; line-height:1.65; color:var(--text); }

  .trace-box{
    border:1px solid var(--line); border-radius:10px; margin-bottom:12px; overflow:hidden; background:var(--surface);
  }
  .trace-head{
    display:flex; align-items:center; gap:8px; padding:9px 13px; cursor:pointer;
    font-family:'JetBrains Mono'; font-size:11px; color:var(--accent-soft); user-select:none;
  }
  .trace-head .chev{ margin-left:auto; font-size:10px; color:var(--muted); transition:transform .2s; }
  .trace-box.open .chev{ transform:rotate(180deg); }
  .trace-body{ display:none; padding:0 13px 12px; font-family:'JetBrains Mono'; font-size:11px; color:var(--muted); line-height:1.9; }
  .trace-box.open .trace-body{ display:block; }
  .trace-body .go{ color:var(--accent-soft); }

  .thinking{ display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono'; font-size:12px; color:var(--muted); padding:4px 0; }
  .thinking .tdot{ width:5px; height:5px; border-radius:50%; background:var(--accent); animation:tblip 1.1s infinite; }
  .thinking .tdot:nth-child(2){ animation-delay:.15s; }
  .thinking .tdot:nth-child(3){ animation-delay:.3s; }
  @keyframes tblip{ 0%,100%{opacity:.2;} 50%{opacity:1;} }

  /* ================= COMPOSER ================= */
  .composer-wrap{ padding:14px 24px 22px; flex-shrink:0; }
  .composer{
    max-width:760px; margin:0 auto; border:1.5px solid var(--line); background:var(--surface);
    border-radius:20px; padding:8px 8px 8px 8px; transition:border-color .2s, box-shadow .2s;
  }
  .composer:focus-within{ border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-dim); }
  .composer-attachments{ display:flex; gap:6px; flex-wrap:wrap; padding:4px 8px 6px; }
  .attach-chip{
    display:flex; align-items:center; gap:6px; background:var(--surface-2); border:1px solid var(--line);
    border-radius:8px; padding:5px 9px; font-size:11.5px; color:var(--text);
  }
  .attach-chip .rm{ color:var(--muted); font-size:12px; margin-left:2px; cursor:pointer; }
  .attach-chip .rm:hover{ color:#E24C4C; }
  .composer-row{ display:flex; align-items:flex-end; gap:6px; }
  .attach-wrap{ position:relative; flex-shrink:0; }
  .attach-btn{
    width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    color:var(--muted); font-size:19px; transition:background .2s, color .2s;
  }
  .attach-btn:hover{ background:var(--surface-2); color:var(--accent); }
  .attach-menu{
    position:absolute; bottom:44px; left:0; background:var(--surface); border:1px solid var(--line);
    border-radius:10px; padding:6px; display:none; min-width:180px; box-shadow:0 20px 50px -12px var(--shadow); z-index:10;
  }
  .attach-menu.open{ display:block; }
  .attach-menu button{
    width:100%; text-align:left; padding:9px 10px; border-radius:7px; font-size:13px;
    display:flex; align-items:center; gap:10px; transition:background .2s;
  }
  .attach-menu button:hover{ background:var(--surface-2); }

  .composer textarea{
    flex:1; border:none; background:transparent; outline:none; resize:none; color:var(--text);
    font-family:'Inter'; font-size:14.5px; line-height:1.5; padding:8px 4px; max-height:160px;
  }
  .composer textarea::placeholder{ color:var(--muted); }
  .send-btn{
    width:36px; height:36px; border-radius:50%; background:var(--accent); color:#03131E;
    display:flex; align-items:center; justify-content:center; font-size:15px; flex-shrink:0;
    transition:transform .15s, opacity .2s; opacity:.4; pointer-events:none;
  }
  .send-btn.ready{ opacity:1; pointer-events:auto; }
  .send-btn.ready:hover{ transform:scale(1.08); }
  .composer-hint{ text-align:center; font-size:10.5px; color:var(--muted); margin-top:10px; font-family:'JetBrains Mono'; }

  /* File input hidden */
  .hidden-file-input{ display:none; }

  ::-webkit-scrollbar{ width:8px; }
  ::-webkit-scrollbar-thumb{ background:var(--line); border-radius:10px; }

  @media(max-width:800px){
    .sidebar{ position:fixed; z-index:40; height:100vh; transform:translateX(-100%); transition:transform .25s; }
    .sidebar.open{ transform:translateX(0); }
    #sidebarToggle{ display:flex !important; }
  }
</style>
</head>
<body>

<input type="file" id="realFileInput" class="hidden-file-input" accept=".pdf,image/*">

<div class="app">

  <!-- ================= SIDEBAR ================= -->
  <div class="sidebar" id="sidebar">
    <a class="sb-logo">MQA<span>&deg;</span></a>

    <button class="new-chat-btn magnetic" onclick="newChat()">
      <span class="plus">+</span> New chat
    </button>

    <div class="history-list" id="historyList">
      <!-- dynamically populated -->
    </div>

    <div class="sb-bottom">
      <div class="user-menu" id="userMenu">
        <button onclick="toggleTheme()">&#127769; Toggle theme</button>
        <button onclick="handleLogout()">&#8618; Log out</button>
      </div>
      <button class="user-row" onclick="toggleUserMenu()">
        <div class="avatar">AP</div>
        <span class="user-name">Achyut Pathak</span>
        <span class="user-chevron">&#9650;</span>
      </button>
    </div>
  </div>

  <!-- ================= MAIN ================= -->
  <div class="main">
    <div class="main-top">
      <div style="display:flex;align-items:center;gap:10px;">
        <button class="icon-btn magnetic" id="sidebarToggle" onclick="document.getElementById('sidebar').classList.toggle('open')" style="display:none;">&#9776;</button>
        <div class="chat-title" id="chatTitle">New chat</div>
      </div>
      <div class="main-top-right">
        <button class="icon-btn magnetic theme-toggle" onclick="toggleTheme()" title="Toggle theme">&#127769;</button>
      </div>
    </div>

    <div class="chat-area" id="chatArea">
      <div class="chat-inner" id="chatInner">
        <!-- populated by JS -->
      </div>
    </div>

    <div class="composer-wrap">
      <div class="composer" id="composer">
        <div class="composer-attachments" id="attachments"></div>
        <div class="composer-row">
          <div class="attach-wrap">
            <button class="attach-btn" onclick="toggleAttachMenu(event)">+</button>
            <div class="attach-menu" id="attachMenu">
              <button onclick="triggerFileUpload('pdf')">&#9636; Upload PDF</button>
              <button onclick="triggerFileUpload('image')">&#9680; Upload Image</button>
            </div>
          </div>
          <textarea id="composerInput" rows="1" placeholder="Ask anything, or drop a PDF / image&hellip;" oninput="onComposerInput(this)" onkeydown="onComposerKey(event)"></textarea>
          <button class="send-btn" id="sendBtn" onclick="sendMessage()">&#8593;</button>
        </div>
      </div>
      <div class="composer-hint">MQA can check your documents, the live web, or an image &mdash; it decides per question.</div>
    </div>
  </div>
</div>

<script>
  /* ---------- chat state ---------- */
  const chats = {};
  let currentChat = null;
  let chatCounter = 0;

  function generateChatId(){ return 'chat_' + (++chatCounter) + '_' + Date.now(); }

  const chatArea = document.getElementById('chatArea');
  const chatTitle = document.getElementById('chatTitle');

  function renderChat(id){
    currentChat = id;
    document.querySelectorAll('.history-item').forEach(el=>el.classList.toggle('active', el.dataset.chat===id));
    const data = chats[id];

    if(!data || !data.messages || data.messages.length===0){
      chatTitle.textContent = 'New chat';
      chatArea.innerHTML = '<div class="welcome">' +
        '<div class="w-icon">&#9672;</div>' +
        '<h1>Where should we start?</h1>' +
        '<p>Ask a question, upload a PDF, or drop an image &mdash; MQA figures out which source to check.</p>' +
        '<div class="suggestion-row">' +
          '<div class="suggestion-chip" onclick="quickFill(\\'Summarize the key points of this PDF\\')">Summarize a PDF</div>' +
          '<div class="suggestion-chip" onclick="quickFill(\\'What does this chart show?\\')">Explain an image</div>' +
          '<div class="suggestion-chip" onclick="quickFill(\\'What are the latest interest rates?\\')">Check the live web</div>' +
        '</div>' +
      '</div>';
      return;
    }

    chatTitle.textContent = data.title;
    chatArea.innerHTML = '<div class="chat-inner" id="chatInner"></div>';
    const inner = document.getElementById('chatInner');
    data.messages.forEach(m=>{
      if(m.role==='user'){
        inner.innerHTML += '<div class="msg msg-user"><div class="bubble">' + m.text + '</div></div>';
      } else {
        let traceHtml = '';
        if(m.trace && m.trace.length){
          traceHtml = '<div class="trace-box" onclick="this.classList.toggle(\\'open\\')">' +
            '<div class="trace-head">&#9672; Reasoning trace <span class="chev">&#9662;</span></div>' +
            '<div class="trace-body">' +
              m.trace.map(t=>'<div class="go">&#10003; ' + t.tool + '</div><div style="margin-bottom:6px;color:var(--muted);">&rarr; ' + t.out + '</div>').join('') +
            '</div></div>';
        }
        inner.innerHTML += '<div class="msg msg-assistant">' +
          '<div class="a-avatar">M</div>' +
          '<div class="a-content">' + traceHtml + '<div class="a-text">' + m.text + '</div></div></div>';
      }
    });
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function newChat(){
    const id = generateChatId();
    chats[id] = {title:'New chat', messages:[]};
    addHistoryItem(id, 'New chat');
    renderChat(id);
    closeMenus();
  }

  function addHistoryItem(id, title){
    const list = document.getElementById('historyList');
    // Remove empty placeholder if any
    const existing = list.querySelector('[data-chat="'+id+'"]');
    if(existing) return;

    const div = document.createElement('div');
    div.className = 'history-item';
    div.dataset.chat = id;
    div.innerHTML = '<span class="h-icon">&#9680;</span><span class="h-title">' + title + '</span>';
    div.addEventListener('click', ()=>{ renderChat(id); });
    list.insertBefore(div, list.firstChild);
  }

  function quickFill(text){
    document.getElementById('composerInput').value = text;
    onComposerInput(document.getElementById('composerInput'));
    document.getElementById('composerInput').focus();
  }

  /* ---------- composer ---------- */
  function onComposerInput(el){
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.classList.toggle('ready', el.value.trim().length > 0 || attachedFiles.length > 0);
  }
  function onComposerKey(e){
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      sendMessage();
    }
  }

  let attachedFiles = [];
  function toggleAttachMenu(e){
    e.stopPropagation();
    document.getElementById('attachMenu').classList.toggle('open');
  }

  function triggerFileUpload(type){
    const input = document.getElementById('realFileInput');
    if(type === 'pdf'){
      input.accept = '.pdf';
    } else {
      input.accept = 'image/*';
    }
    input.click();
    document.getElementById('attachMenu').classList.remove('open');
  }

  document.getElementById('realFileInput').addEventListener('change', function(e){
    const file = e.target.files[0];
    if(!file) return;
    attachedFiles.push({file: file, name: file.name, icon: file.name.endsWith('.pdf') ? '&#9636;' : '&#9680;'});
    renderAttachments();
    onComposerInput(document.getElementById('composerInput'));
    e.target.value = '';
  });

  function renderAttachments(){
    const wrap = document.getElementById('attachments');
    wrap.innerHTML = attachedFiles.map((f,i)=>
      '<div class="attach-chip">' + f.icon + ' ' + f.name + ' <span class="rm" onclick="removeAttach(' + i + ')">&#10005;</span></div>'
    ).join('');
  }
  function removeAttach(i){
    attachedFiles.splice(i,1);
    renderAttachments();
    onComposerInput(document.getElementById('composerInput'));
  }

  /* ---------- send message (calls real backend) ---------- */
  async function sendMessage(){
    const input = document.getElementById('composerInput');
    const text = input.value.trim();
    if(!text && attachedFiles.length===0) return;

    // Ensure we have a chat
    if(!currentChat || !chats[currentChat]){
      newChat();
    }
    if(chats[currentChat].messages.length === 0){
      chatArea.innerHTML = '<div class="chat-inner" id="chatInner"></div>';
    }

    // Handle file uploads first
    if(attachedFiles.length > 0){
      for(const af of attachedFiles){
        const uploadText = 'Uploaded: ' + af.name;
        chats[currentChat].messages.push({role:'user', text: uploadText});
        const inner = document.getElementById('chatInner');
        inner.innerHTML += '<div class="msg msg-user"><div class="bubble">' + uploadText + '</div></div>';

        // Show thinking
        const thinkId = 'think-upload-'+Date.now();
        inner.innerHTML += '<div class="msg msg-assistant" id="' + thinkId + '">' +
          '<div class="a-avatar">M</div>' +
          '<div class="a-content"><div class="thinking"><span class="tdot"></span><span class="tdot"></span><span class="tdot"></span> processing file&hellip;</div></div></div>';
        chatArea.scrollTop = chatArea.scrollHeight;

        try{
          const formData = new FormData();
          formData.append('file', af.file);
          const resp = await fetch('/api/upload', {method:'POST', body: formData});
          const data = await resp.json();
          const el = document.getElementById(thinkId);
          el.innerHTML = '<div class="a-avatar">M</div><div class="a-content">' +
            '<div class="trace-box" onclick="this.classList.toggle(\\'open\\')">' +
            '<div class="trace-head">&#9672; Processing trace <span class="chev">&#9662;</span></div>' +
            '<div class="trace-body"><div class="go">&#10003; ' + (af.name.endsWith('.pdf') ? 'process_pdf' : 'process_image') + '</div>' +
            '<div style="color:var(--muted);">&rarr; ' + data.filename + '</div></div></div>' +
            '<div class="a-text">' + data.result + '</div></div>';
          chats[currentChat].messages.push({role:'assistant', text: data.result, trace:[{tool: af.name.endsWith('.pdf') ? 'process_pdf' : 'process_image', out: data.filename}]});
        } catch(err){
          const el = document.getElementById(thinkId);
          el.innerHTML = '<div class="a-avatar">M</div><div class="a-content"><div class="a-text">Error uploading file: ' + err.message + '</div></div>';
        }
        chatArea.scrollTop = chatArea.scrollHeight;
      }
      attachedFiles = [];
      renderAttachments();
    }

    // Handle text query
    if(text){
      let displayText = text;
      chats[currentChat].messages.push({role:'user', text: displayText});

      // Update chat title from first message
      if(chats[currentChat].title === 'New chat'){
        chats[currentChat].title = text.substring(0, 40) + (text.length > 40 ? '...' : '');
        chatTitle.textContent = chats[currentChat].title;
        const histItem = document.querySelector('[data-chat="'+currentChat+'"] .h-title');
        if(histItem) histItem.textContent = chats[currentChat].title;
      }

      const inner = document.getElementById('chatInner');
      inner.innerHTML += '<div class="msg msg-user"><div class="bubble">' + displayText + '</div></div>';

      input.value=''; input.style.height='auto';
      document.getElementById('sendBtn').classList.remove('ready');

      const thinkingId = 'think-'+Date.now();
      inner.innerHTML += '<div class="msg msg-assistant" id="' + thinkingId + '">' +
        '<div class="a-avatar">M</div>' +
        '<div class="a-content"><div class="thinking"><span class="tdot"></span><span class="tdot"></span><span class="tdot"></span> deciding which tool to use&hellip;</div></div></div>';
      chatArea.scrollTop = chatArea.scrollHeight;

      try{
        const resp = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({query: text})
        });
        const data = await resp.json();
        const el = document.getElementById(thinkingId);

        let traceHtml = '';
        if(data.tools_used && data.tools_used.length){
          traceHtml = '<div class="trace-box" onclick="this.classList.toggle(\\'open\\')">' +
            '<div class="trace-head">&#9672; Reasoning trace <span class="chev">&#9662;</span></div>' +
            '<div class="trace-body">' +
              data.tools_used.map(t=>'<div class="go">&#10003; ' + t + '</div>').join('') +
            '</div></div>';
        }
        el.innerHTML = '<div class="a-avatar">M</div><div class="a-content">' + traceHtml + '<div class="a-text">' + data.answer + '</div></div>';
        chats[currentChat].messages.push({role:'assistant', text: data.answer, trace: (data.tools_used||[]).map(t=>({tool:t, out:''}))});
      } catch(err){
        const el = document.getElementById(thinkingId);
        el.innerHTML = '<div class="a-avatar">M</div><div class="a-content"><div class="a-text">Error: ' + err.message + '</div></div>';
      }
      chatArea.scrollTop = chatArea.scrollHeight;
    } else {
      input.value=''; input.style.height='auto';
      document.getElementById('sendBtn').classList.remove('ready');
    }
  }

  /* ---------- user menu ---------- */
  function toggleUserMenu(){
    document.getElementById('userMenu').classList.toggle('open');
    document.getElementById('attachMenu').classList.remove('open');
  }
  function closeMenus(){
    document.getElementById('userMenu').classList.remove('open');
    document.getElementById('attachMenu').classList.remove('open');
  }
  function handleLogout(){
    try { parent.postMessage({action:'go_landing'}, '*'); } catch(e){}
  }
  document.addEventListener('click', (e)=>{
    if(!e.target.closest('.user-row') && !e.target.closest('.user-menu')) document.getElementById('userMenu').classList.remove('open');
    if(!e.target.closest('.attach-wrap')) document.getElementById('attachMenu').classList.remove('open');
  });

  /* ---------- magnetic ---------- */
  document.querySelectorAll('.magnetic').forEach(btn=>{
    btn.addEventListener('mousemove', e=>{
      const r = btn.getBoundingClientRect();
      const x = e.clientX - r.left - r.width/2;
      const y = e.clientY - r.top - r.height/2;
      btn.style.transform = 'translate(' + (x*0.12) + 'px, ' + (y*0.2) + 'px)';
    });
    btn.addEventListener('mouseleave', ()=>{ btn.style.transform='translate(0,0)'; });
  });

  // Start with a new empty chat
  newChat();
</script>
</body>
</html>
"""


# JavaScript to listen for postMessage events from the iframes
listen_js = '''
function() {
    // Start with landing page visible, hide others
    setTimeout(() => {
        const landing = document.getElementById('landing-page-html');
        const login = document.getElementById('login-container');
        const workspace = document.getElementById('workspace-container');
        if (landing) landing.style.setProperty('display', 'flex', 'important');
        if (login) login.style.setProperty('display', 'none', 'important');
        if (workspace) workspace.style.setProperty('display', 'none', 'important');
    }, 100);

    function showPage(pageId) {
        const pages = ['landing-page-html', 'login-container', 'workspace-container'];
        pages.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                if (id === pageId) {
                    el.style.setProperty('display', 'flex', 'important');
                } else {
                    el.style.setProperty('display', 'none', 'important');
                }
            }
        });
    }

    window.addEventListener('message', (event) => {
        let data = event.data;
        if (typeof data === 'string') { data = {action: data}; }

        if (data.action === 'go_login' || data.action === 'go_signup') {
            showPage('login-container');
        } else if (data.action === 'go_landing') {
            showPage('landing-page-html');
        } else if (data.action === 'login_success') {
            showPage('workspace-container');
            // Send user info to workspace iframe
            const wsIframe = document.querySelector('#workspace-iframe');
            if (wsIframe && wsIframe.contentWindow && data.name) {
                wsIframe.contentWindow.postMessage({action: 'set_user', name: data.name}, '*');
            }
        } else if (data.action === 'toggle_theme') {
            const theme = data.theme;
            if (theme === 'dark') {
                document.body.classList.add('dark');
                document.body.setAttribute('data-theme', 'dark');
            } else {
                document.body.classList.remove('dark');
                document.body.setAttribute('data-theme', 'light');
            }
            // Sync to ALL iframes
            document.querySelectorAll('iframe').forEach(iframe => {
                if (iframe && iframe.contentWindow) {
                    iframe.contentWindow.postMessage({action: 'apply_theme', theme: theme}, '*');
                }
            });
        }
    });
}
'''


custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg: #F4F6F8;
  --surface: #FFFFFF;
  --surface-2: #EAEDF0;
  --line: #DDE2E7;
  --text: #0E1116;
  --muted: #5C6470;
  --accent: #0EA5E9;
  --accent-soft: #0284C7;
  --accent-dim: rgba(14,165,233,0.10);
  --shadow: rgba(15, 25, 35, 0.08);
  --sidebar-bg: #FFFFFF;
  --chat-bg: #F4F6F8;
}

body.dark, body[data-theme='dark'], .dark {
  --bg: #070A10;
  --surface: #0E121A;
  --surface-2: #141A24;
  --line: #212A38;
  --text: #EAF2F8;
  --muted: #7C8797;
  --accent: #38BDF8;
  --accent-soft: #7DD3FC;
  --accent-dim: rgba(56,189,248,0.16);
  --shadow: rgba(0, 0, 0, 0.4);
  --sidebar-bg: #0E121A;
  --chat-bg: #070A10;
}

/* Base resets to prevent viewport overflow and browser scrollbars */
html, body {
  height: 100vh !important;
  max-height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  background-color: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
}

.gradio-container {
  height: 100vh !important;
  max-height: 100vh !important;
  max-width: 100% !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  border: none !important;
  background: var(--bg) !important;
}

/* Top-level Svelte/Gradio wrappers stretch */
.gradio-container > .wrap,
.gradio-container > .contain,
.gradio-container > .wrap > .contain,
.gradio-container > div {
  height: 100% !important;
  width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* Hide footers completely */
footer, .footer, #footer {
  display: none !important;
}

/* State Trigger hidden components */
#btn-hidden-go-login, #btn-hidden-go-landing,
#btn-hidden-do-login, #btn-hidden-do-signup,
#login-email, #login-password,
#signup-name, #signup-email, #signup-password,
#trigger-js-box {
  display: none !important;
}

#landing-page-html, #login-container {
  height: 100vh !important;
  max-height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  border: none !important;
}

#workspace-container {
  height: 100vh !important;
  max-height: 100vh !important;
  padding: 0 !important;
  margin: 0 !important;
  overflow: hidden !important;
  border: none !important;
}

/* Outer workspace wrappers stretch */
#workspace-container .form,
#workspace-container .contain,
#workspace-container .wrap {
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  gap: 0 !important;
}

/* Grid background matching landing page */
.workspace-grid-bg {
  background:
    repeating-linear-gradient(0deg, transparent, transparent 39px, var(--line) 40px),
    repeating-linear-gradient(90deg, transparent, transparent 39px, var(--line) 40px),
    var(--bg) !important;
  background-attachment: fixed !important;
}

/* Workspace Row */
.workspace-row {
  display: flex !important;
  flex-direction: row !important;
  height: 100vh !important;
  max-height: 100vh !important;
  width: 100% !important;
  gap: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* Ensure all wrapper containers inside workspace-row span full height and row direction */
.workspace-row .form,
.workspace-row .contain,
.workspace-row .wrap {
  display: flex !important;
  flex-direction: row !important;
  height: 100% !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
  gap: 0 !important;
}

/* Left Sidebar */
.sidebar-left {
  width: 260px !important;
  min-width: 260px !important;
  max-width: 260px !important;
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--line) !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  z-index: 10 !important;
}

.sidebar-left .form,
.sidebar-left .contain,
.sidebar-left .wrap {
  flex-direction: column !important;
}

.sidebar-logo {
  padding: 24px 20px 16px 20px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  font-size: 22px !important;
  color: var(--text) !important;
  letter-spacing: -0.02em !important;
}

.new-chat-btn {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--text) !important;
  border-radius: 20px !important;
  padding: 10px 16px !important;
  text-align: left !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  margin: 0 16px 12px 16px !important;
  width: calc(100% - 32px) !important;
}

.new-chat-btn:hover {
  border-color: var(--accent) !important;
  box-shadow: 0 2px 8px var(--shadow) !important;
}

.h_lst {
  flex: 1 !important;
  overflow-y: auto !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  padding: 8px 16px !important;
  min-height: 0 !important;
}

.u_p {
  padding: 16px 20px !important;
  border-top: 1px solid var(--line) !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  background: var(--surface-2) !important;
  margin-top: auto !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.avatar-icon {
  width: 36px !important;
  height: 36px !important;
  background: var(--accent) !important;
  color: #03131E !important;
  border-radius: 50% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-weight: 700 !important;
  font-size: 15px !important;
}

.user-info {
  display: flex !important;
  flex-direction: column !important;
  min-width: 0 !important;
}

.user-info .name {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--text) !important;
}

/* Main Chat Area */
.m_cnt {
  flex: 1 !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
}

.m_cnt .form,
.m_cnt .contain,
.m_cnt .wrap {
  flex-direction: column !important;
}

/* Chatbot component and its nested wrappers forced to occupy full remaining height */
.custom-chatbot,
.custom-chatbot .wrapper,
.custom-chatbot .chatbot,
.custom-chatbot .contain,
.custom-chatbot .wrap,
.custom-chatbot .message-wrap {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 !important;
  height: 100% !important;
  min-height: 0 !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.custom-chatbot .message-wrap {
  padding: 24px 8% !important;
  overflow-y: auto !important;
}

.custom-chatbot .message {
  padding: 16px 20px !important;
  border-radius: 16px !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
  max-width: 80% !important;
  box-shadow: 0 4px 12px var(--shadow) !important;
  margin-bottom: 12px !important;
}

.custom-chatbot .message.user {
  align-self: flex-end !important;
  background: var(--accent) !important;
  color: #03131E !important;
  border-bottom-right-radius: 4px !important;
  border: none !important;
}

.custom-chatbot .message.bot {
  align-self: flex-start !important;
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  color: var(--text) !important;
  border-bottom-left-radius: 4px !important;
}

/* Input Area (Claude style search bar - Made bigger) */
.i_w_wrapper {
  padding: 16px 8% 24px 8% !important;
  background: transparent !important;
  width: 100% !important;
  border: none !important;
  flex-shrink: 0 !important;
}

.i_w_wrapper .form,
.i_w_wrapper .contain,
.i_w_wrapper .wrap {
  display: flex !important;
  flex-direction: column !important;
  width: 100% !important;
  padding: 0 !important;
  margin: 0 !important;
}

.i_w {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  background: var(--surface) !important;
  border: 1.5px solid var(--line) !important;
  border-radius: 32px !important;
  padding: 10px 16px 10px 22px !important;
  max-width: 900px !important;
  width: 100% !important;
  margin: 0 auto !important;
  box-shadow: 0 10px 30px var(--shadow) !important;
  gap: 16px !important;
  box-sizing: border-box !important;
}

.i_w:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 10px 30px var(--accent-dim) !important;
}

.i_w .form,
.i_w .contain,
.i_w .wrap {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  width: 100% !important;
  gap: 12px !important;
  padding: 0 !important;
  margin: 0 !important;
}

/* Upload Button inside the search bar */
.inline-upload-btn {
  background: var(--surface-2) !important;
  border: none !important;
  color: var(--text) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 0 20px !important;
  height: 42px !important;
  border-radius: 21px !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  box-shadow: none !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 !important;
}

.inline-upload-btn:hover {
  background: var(--accent-dim) !important;
  color: var(--accent) !important;
}

/* Text Input inside the search bar (Larger font size) */
.custom-input {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  flex: 1 !important;
  min-width: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}

.custom-input .form,
.custom-input .contain,
.custom-input .wrap {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  width: 100% !important;
}

.custom-input textarea,
.custom-input input {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--text) !important;
  font-size: 16px !important;
  padding: 8px 0 !important;
  resize: none !important;
  min-height: 28px !important;
  max-height: 120px !important;
  outline: none !important;
  width: 100% !important;
}
"""


with gr.Blocks(title="Multimodal Q&A Pro", fill_width=True) as demo:
    gr.HTML(f"<style>{custom_css}</style>")
    session_state = gr.State(None)
    trigger_js_box = gr.Textbox(visible=False, elem_id='trigger-js-box')

    # Hidden buttons — kept for Gradio event wiring but fully hidden via CSS elem_id targeting
    btn_go_login = gr.Button("Go Login Hidden", visible=False, elem_id="btn-hidden-go-login")
    btn_go_landing = gr.Button("Go Landing Hidden", visible=False, elem_id="btn-hidden-go-landing")
    btn_do_login = gr.Button("Do Login Hidden", visible=False, elem_id="btn-hidden-do-login")
    login_email = gr.Textbox(visible=False, elem_id="login-email")
    login_password = gr.Textbox(visible=False, elem_id="login-password")
    btn_do_signup = gr.Button("Do Signup Hidden", visible=False, elem_id="btn-hidden-do-signup")
    signup_name = gr.Textbox(visible=False, elem_id="signup-name")
    signup_email = gr.Textbox(visible=False, elem_id="signup-email")
    signup_password = gr.Textbox(visible=False, elem_id="signup-password")

    # ─── Landing Page ───
    with gr.Column(visible=True, elem_id="landing-page-html") as col_landing:
        gr.HTML(
            f'''<iframe srcdoc="{landing_page_html.replace('"', '&quot;')}" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; margin: 0; padding: 0; display: block; z-index: 9999;"></iframe>'''
        )
        demo.load(None, None, None, js=listen_js)

    # ─── Login Page ───
    with gr.Column(visible=True, elem_id="login-container") as col_login:
        gr.HTML(
            f'''<iframe srcdoc="{login_page_html.replace('"', '&quot;')}" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; margin: 0; padding: 0; display: block; z-index: 9998;"></iframe>'''
        )

    # ─── Workspace Page (custom HTML served as iframe) ───
    with gr.Column(visible=True, elem_id="workspace-container", elem_classes=["workspace-grid-bg"]) as col_workspace:
        gr.HTML(
            f'''<iframe id="workspace-iframe" srcdoc="{workspace_html.replace('"', '&quot;')}" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; border: none; margin: 0; padding: 0; display: block; z-index: 9997;"></iframe>'''
        )

    # ─── Event Handlers ───
    def show_landing():
        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    def show_login():
        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

    def handle_signup(name, email, password):
        try:
            res = register_user(name, email, password)
            if res["success"]:
                return json.dumps({"action": "signup_success", "message": res["message"]})
            else:
                return json.dumps({"action": "signup_error", "message": res["message"]})
        except Exception as e:
            return json.dumps({"action": "signup_error", "message": f"Something went wrong: {e}"})

    def handle_login(email, password):
        try:
            res = login_user(email, password)
            if res["success"]:
                user_data = {"name": res["name"], "email": res["email"]}
                return user_data, json.dumps({"action": "login_success", "name": res["name"], "email": res["email"]})
            else:
                return None, json.dumps({"action": "login_error", "message": res["message"]})
        except Exception as e:
            return None, json.dumps({"action": "login_error", "message": f"Something went wrong: {e}"})

    btn_go_login.click(show_login, None, [col_landing, col_login, col_workspace])
    btn_go_landing.click(show_landing, None, [col_landing, col_login, col_workspace])

    btn_do_signup.click(
        handle_signup,
        inputs=[signup_name, signup_email, signup_password],
        outputs=[trigger_js_box],
        js="(n, e, p) => [window.auth_data.name, window.auth_data.email, window.auth_data.password]",
        queue=False
    )

    btn_do_login.click(
        handle_login,
        inputs=[login_email, login_password],
        outputs=[session_state, trigger_js_box],
        js="(e, p) => [window.auth_data.email, window.auth_data.password]",
        queue=False
    )

    trigger_js_box.change(
        fn=None,
        inputs=[trigger_js_box],
        outputs=None,
        js="""(val) => {
            if (!val) return;
            try {
                const data = JSON.parse(val);
                if (data.action === 'signup_error' || data.action === 'login_error') {
                    const iframe = document.querySelector('#login-container iframe');
                    if (iframe && iframe.contentWindow) {
                        iframe.contentWindow.postMessage(data, '*');
                    }
                }
            } catch(e) {}
        }"""
    )

if __name__ == '__main__':
    import uvicorn
    import tempfile
    import shutil
    from fastapi import FastAPI, UploadFile, File, Form
    from fastapi.responses import HTMLResponse

    # Create a standalone FastAPI app with auth API routes
    api_app = FastAPI()

    @api_app.post("/api/login")
    async def api_login(request: Request):
        try:
            body = await request.json()
            email = body.get("email", "").strip().lower()
            password = body.get("password", "")
            res = login_user(email, password)
            return JSONResponse(content=res)
        except Exception as e:
            return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

    @api_app.post("/api/signup")
    async def api_signup(request: Request):
        try:
            body = await request.json()
            name = body.get("name", "").strip()
            email = body.get("email", "").strip().lower()
            password = body.get("password", "")
            res = register_user(name, email, password)
            return JSONResponse(content=res)
        except Exception as e:
            return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

    @api_app.post("/api/chat")
    async def api_chat(request: Request):
        """Handle chat messages from the workspace frontend"""
        try:
            body = await request.json()
            query = body.get("query", "").strip()
            if not query:
                return JSONResponse(content={"answer": "Please enter a question.", "tools_used": []})
            res = run_agent_query(query)
            answer = res.get("answer", "No answer found.")
            tools_used = res.get("tools_used", [])
            return JSONResponse(content={"answer": answer, "tools_used": tools_used})
        except Exception as e:
            return JSONResponse(content={"answer": f"Error: {str(e)}", "tools_used": []}, status_code=500)

    @api_app.post("/api/upload")
    async def api_upload(file: UploadFile = File(...)):
        """Handle file uploads from the workspace frontend"""
        try:
            # Save uploaded file to a temp location
            suffix = os.path.splitext(file.filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            tmp.close()

            filename = tmp.name
            if file.filename.lower().endswith('.pdf'):
                res = process_pdf(filename)
            else:
                res = process_image(filename)

            # Clean up temp file
            try:
                os.unlink(filename)
            except:
                pass

            return JSONResponse(content={"result": str(res), "filename": file.filename})
        except Exception as e:
            return JSONResponse(content={"result": f"Error: {str(e)}", "filename": file.filename if file else "unknown"}, status_code=500)

    # Mount Gradio app onto FastAPI
    api_app = gr.mount_gradio_app(api_app, demo, path="/", root_path="")

    uvicorn.run(api_app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))

