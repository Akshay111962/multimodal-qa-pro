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
            // Update user profile
            const nameEl = document.querySelector('.user-info .name');
            if (nameEl && data.name) nameEl.textContent = data.name;
            const avatarEl = document.querySelector('.avatar-icon');
            if (avatarEl && data.name) avatarEl.textContent = data.name[0].toUpperCase();
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


with gr.Blocks(title="Multimodal Q&A Pro", fill_width=True, css=custom_css) as demo:
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

    # ─── Workspace Page (Claude-style layout) ───
    with gr.Column(visible=True, elem_id="workspace-container", elem_classes=["workspace-grid-bg"]) as col_workspace:
        with gr.Row(elem_classes=["workspace-row"]):
            # Left Sidebar
            with gr.Column(scale=0, elem_classes=["sidebar-left"]):
                gr.HTML('<div class="sidebar-logo">MQA</div>')

                btn_new_chat = gr.Button("+ New chat", elem_classes=["new-chat-btn"])

                with gr.Column(elem_classes=["h_lst"]):
                    pass

                user_profile_box = gr.HTML(value="""
                    <div class="u_p">
                        <div class="avatar-icon">A</div>
                        <div class="user-info">
                            <span class="name">User</span>
                        </div>
                    </div>
                """)

            # Center/Right Chat Area
            with gr.Column(scale=3, elem_classes=["m_cnt"]):
                chatbot = gr.Chatbot(
                    value=[{"role": "assistant", "content": "Welcome! I'm your MQA assistant. Upload a PDF or image, or ask me anything to get started."}],
                    show_label=False,
                    elem_classes=["custom-chatbot"]
                )
                with gr.Column(elem_classes=["i_w_wrapper"]):
                    with gr.Row(elem_classes=["i_w"]):
                        workspace_upload = gr.UploadButton("📎 Upload PDF/Image", file_types=[".pdf", "image"], variant="secondary", elem_classes=["inline-upload-btn"])
                        msg = gr.Textbox(placeholder="How can I help you today?", show_label=False, container=False, elem_classes=["custom-input"])

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
                user_html = f"<div class='u_p'><div class='avatar-icon'>{res['name'][0].upper()}</div><div class='user-info'><span class='name'>{res['name']}</span></div></div>"
                greeting = [{"role": "assistant", "content": f"Welcome back, {res['name']}! I'm your MQA assistant. Upload a PDF or image, or ask me anything."}]
                return user_data, user_html, greeting, json.dumps({"action": "login_success"})
            else:
                return None, gr.update(), gr.update(), json.dumps({"action": "login_error", "message": res["message"]})
        except Exception as e:
            return None, gr.update(), gr.update(), json.dumps({"action": "login_error", "message": f"Something went wrong: {e}"})

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
        outputs=[session_state, user_profile_box, chatbot, trigger_js_box],
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

    def handle_query(query, history):
        if not query:
            return history, ""
        history = history or []
        history.append({"role": "user", "content": query})

        res = run_agent_query(query)
        answer = res.get("answer", "No answer found.")
        tools_used = res.get("tools_used", [])

        if tools_used:
            tools_str = "\n".join([f"✓ {t}" for t in tools_used])
            trace_header = f'<small style="opacity:0.6;font-family:monospace;display:block;margin-bottom:8px;border-bottom:1px solid #334155;padding-bottom:4px;">Routing trace:\n{tools_str}</small>'
            bot_content = trace_header + answer
        else:
            bot_content = answer

        history.append({"role": "assistant", "content": bot_content})
        return history, ""

    def handle_upload(file_obj, history):
        if not file_obj:
            return history
        filename = file_obj.name
        history = history or []

        if filename.lower().endswith('.pdf'):
            res = process_pdf(filename)
            history.append({"role": "user", "content": f"Uploaded PDF: {os.path.basename(filename)}"})
            history.append({"role": "assistant", "content": f"✓ {res}"})
        else:
            res = process_image(filename)
            history.append({"role": "user", "content": f"Uploaded Image: {os.path.basename(filename)}"})
            history.append({"role": "assistant", "content": f"✓ {res}"})
        return history

    msg.submit(
        handle_query,
        inputs=[msg, chatbot],
        outputs=[chatbot, msg]
    )
    workspace_upload.upload(
        handle_upload,
        inputs=[workspace_upload, chatbot],
        outputs=[chatbot]
    )

if __name__ == '__main__':
    import uvicorn
    from fastapi import FastAPI

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

    # Mount Gradio app onto FastAPI
    api_app = gr.mount_gradio_app(api_app, demo, path="/", root_path="")

    uvicorn.run(api_app, host="0.0.0.0", port=7860)

