/* ═══════════════════════════════════════════════════════════════
   ZEN AGENT — Dashboard Client v2
   ═══════════════════════════════════════════════════════════════ */
const S={uid:'web-user',sid:null,mc:0,ws:null,busy:false,recon:0};
const $=s=>document.querySelector(s);
const $$=s=>document.querySelectorAll(s);

// DOM refs — match the new HTML IDs
const msgs=$('#ms'),inp=$('#ci'),send=$('#bs');
const sidEl=$('#sid'),uidEl=$('#uid'),mcEl=$('#mc');
const sdot=$('#sdt'),stxt=$('#stx');
const btnClear=$('#bc'),btnNew=$('#bn'),menuBtn=$('#mm');
const welcome=$('#wl');

/* ─── WebSocket ─────────────────────────────────────────────── */
function connect(){
  const p=location.protocol==='https:'?'wss:':'ws:';
  if(S.ws)S.ws.close();
  S.ws=new WebSocket(`${p}//${location.host}/ws/chat/${S.uid}`);
  S.ws.onopen=()=>{setStatus('on');S.recon=0};
  S.ws.onmessage=e=>{try{handle(JSON.parse(e.data))}catch(_){}};
  S.ws.onclose=()=>{
    setStatus('off');S.busy=false;rmTyping();
    if(S.recon<5){S.recon++;setTimeout(connect,1500*S.recon)}
  };
  S.ws.onerror=()=>setStatus('off');
}

function handle(d){
  switch(d.type){
    case'info':S.sid=d.session_id||'';sidEl.textContent=d.session_id||'—';uidEl.textContent=d.uid||S.uid;break;
    case'token':appendToken(d.content);break;
    case'reasoning':appendReasoning(d.content);break;
    case'done':finishStream(d.content||d.full_content);break;
    case'clear':clearUI();break;
    case'error':toast(d.message||'Error','err');finishStream(null);break;
  }
}

function wsSend(m){
  if(S.ws&&S.ws.readyState===WebSocket.OPEN){S.ws.send(JSON.stringify({message:m}));return true}
  return false
}

/* ─── Chat UI ──────────────────────────────────────────────── */
function addMsg(text,role){
  rmWelcome();rmTyping();
  const div=document.createElement('div');
  const r=role==='user'?'user':'assistant';
  div.className='msg '+r;
  const ts=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  const av=role==='user'?'👤':'🤖';
  div.innerHTML='<div class="av">'+av+'</div><div><div class="bubble"></div><div class="msg-time">'+ts+'</div></div>';
  msgs.appendChild(div);
  scroll();
  const bubble=div.querySelector('.bubble');
  if(role==='user'&&text){
    renderMarkdown(text,bubble);
  }else if(role==='assistant'){
    bubble.id='ast-msg';
    if(text)renderMarkdown(text,bubble);
  }
  return bubble;
}

function addTyping(){
  rmTyping();
  const d=document.createElement('div');d.className='msg assistant';d.id='typing-msg';
  d.innerHTML='<div class="av">🤖</div><div><div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>';
  msgs.appendChild(d);scroll();
}

function appendToken(t){
  let el=document.querySelector('#ast-msg');
  if(!el){el=addMsg('','assistant');el.id='ast-msg'}
  rmTyping();
  el.textContent+=t;
  scroll();
}

let _reasoningEl=null,_rBuf='';
function appendReasoning(t){
  _rBuf+=t;
  let el=document.querySelector('#ast-msg');
  if(!el){el=addMsg('','assistant');el.id='ast-msg'}
  rmTyping();
  if(!_reasoningEl||!document.contains(_reasoningEl)){
    const wrap=el.closest('.msg');
    if(!wrap)return;
    const box=document.createElement('div');box.className='reasoning-box';box.id='rbox';
    const btn=document.createElement('div');btn.className='reasoning-btn';
    btn.textContent='🤔 Thinking...';
    btn.onclick=function(){
      const b=document.querySelector('#rbox');
      if(!b)return;
      b.classList.toggle('open');
      if(b.classList.contains('open')){
        b.style.maxHeight=b.scrollHeight+'px';
      }else{
        b.style.maxHeight='0';
      }
      const bt=b.previousElementSibling;
      if(bt&&bt.classList.contains('reasoning-btn'))
        bt.textContent=b.classList.contains('open')?'🤔 Hide thinking':'🤔 Show thinking…';
    };
    // Inline styles for reasoning box
    box.style.cssText='display:block;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius-sm);padding:8px 12px;font-size:12px;color:var(--text2);margin-top:4px;max-height:0;overflow:hidden;transition:max-height .3s ease;font-family:var(--font-mono);white-space:pre-wrap';
    btn.style.cssText='font-size:11px;color:var(--text3);cursor:pointer;padding:2px 0;user-select:none';
    wrap.appendChild(btn);
    btn.after(box);
    _reasoningEl=box;
  }
  _reasoningEl.textContent=_rBuf;
  scroll();
}

function finishStream(full){
  rmTyping();
  if(full!==null){
    const el=document.querySelector('#ast-msg');
    if(el&&full){renderMarkdown(full,el)}
  }
  S.busy=false;updBtn();updMC();
  $$('#ast-msg').forEach(e=>e.removeAttribute('id'));
  _reasoningEl=null;_rBuf='';
  scroll();
}

function rmWelcome(){if(welcome&&welcome.parentNode)welcome.remove()}
function rmTyping(){const t=document.getElementById('typing-msg');if(t)t.remove()}
function clearUI(){
  msgs.innerHTML='';
  if(welcome)msgs.appendChild(welcome);
  updMC();S.mc=0;
  _reasoningEl=null;_rBuf='';
}
function scroll(){requestAnimationFrame(()=>{msgs.scrollTop=msgs.scrollHeight})}

/* ─── Markdown rendering ──────────────────────────────────── */
function renderMarkdown(text,el){
  if(!text||!el)return;
  let h=esc(text)
    .replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code class="lang-$1">$2</code></pre>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\*\*\*(.+?)\*\*\*/g,'<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,'<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/^### (.+)$/gm,'<h3>$1</h3>')
    .replace(/^## (.+)$/gm,'<h2>$1</h2>')
    .replace(/^# (.+)$/gm,'<h1>$1</h1>')
    .replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>')
    .replace(/^- (.+)$/gm,'<li>• $1</li>')
    .replace(/(<li>• .*<\/li>\n?)+/g,'<ul>$&</ul>')
    .replace(/^\d+\. (.+)$/gm,'<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g,'<ol>$&</ol>')
    .replace(/---+/g,'<hr>')
    .replace(/\n\n/g,'</p><p>')
    .replace(/\n/g,'<br>');
  el.innerHTML='<p>'+h+'</p>';

  // Copy buttons for code blocks
  el.querySelectorAll('pre code').forEach(block=>{
    const pre=block.parentElement;
    if(pre.querySelector('.copy-btn'))return;
    const btn=document.createElement('button');
    btn.className='copy-btn';
    btn.style.cssText='position:absolute;top:4px;right:4px;background:var(--border);border:none;color:var(--text3);padding:2px 8px;border-radius:4px;font-size:10px;cursor:pointer;font-family:inherit;z-index:1;line-height:1.4';
    btn.textContent='📋';
    btn.title='Copy code';
    btn.onclick=function(){
      navigator.clipboard.writeText(block.textContent).then(function(){
        btn.textContent='✅';setTimeout(function(){btn.textContent='📋'},1500);
      });
    };
    pre.style.cssText='position:relative;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 12px 8px;overflow-x:auto;margin:6px 0';
    pre.appendChild(btn);
    
    // Language label
    const m=block.className.match(/lang-(\w+)/);
    if(m&&!pre.querySelector('.lang-label')){
      const lbl=document.createElement('div');
      lbl.className='lang-label';
      lbl.style.cssText='font-size:9px;color:var(--text4);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;font-family:var(--font-mono)';
      lbl.textContent=m[1];
      pre.insertBefore(lbl,block);
    }
  });
  
  // Tables
  el.querySelectorAll('pre').forEach(pre=>{
    if(pre.innerHTML.includes('|')&&pre.innerHTML.includes('\n')){
      const lines=pre.textContent.split('\n').filter(l=>l.trim());
      if(lines.some(l=>l.startsWith('|')&&l.endsWith('|'))){
        let tb='<table style="border-collapse:collapse;width:100%;font-size:12px">';
        lines.forEach((l,i)=>{
          if(l.match(/^[\| :\-]+\|?$/))return;
          tb+='<tr>';
          l.split('|').filter(c=>c.trim()).forEach(c=>{
            const tg=i===0?'th':'td';
            tb+='<'+tg+' style="border:1px solid var(--border);padding:4px 8px;text-align:left">'+c.trim()+'</'+tg+'>';
          });
          tb+='</tr>';
        });
        tb+='</table>';
        pre.innerHTML=tb;
      }
    }
  });
}

function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}

/* ─── Toast system ────────────────────────────────────────── */
function toast(m,t){
  t=t||'info';
  var c=document.getElementById('toasts');
  if(!c){c=document.createElement('div');c.id='toasts';document.body.appendChild(c)}
  var d=document.createElement('div');
  d.className='tt '+t;
  d.textContent=m;
  c.appendChild(d);
  setTimeout(function(){if(d.parentNode)d.remove()},3500);
}

/* ─── Send ────────────────────────────────────────────────── */
function sendMsg(){
  const t=inp.value.trim();
  if(!t||S.busy)return;
  addMsg(t,'user');
  inp.value='';
  inp.style.height='auto';
  addTyping();
  updMC();
  if(!wsSend(t))restChat(t);
}

async function restChat(m){
  S.busy=true;updBtn();
  try{
    const r=await fetch('/api/chat',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:m,user_id:S.uid,session_id:S.sid})
    });
    const d=await r.json();
    if(!r.ok){toast(d.detail||'Request failed','err');rmTyping();finishStream(null);return}
    S.sid=d.session_id||S.sid;sidEl.textContent=S.sid||'—';
    rmTyping();
    const el=addMsg('','assistant');
    el.id='ast-msg';
    renderMarkdown(d.response||'[No response]',el);
    el.removeAttribute('id');
    finishStream(d.response);
  }catch(e){toast('Request failed','err');rmTyping();finishStream(null)}
}

/* ─── Events ──────────────────────────────────────────────── */
inp.addEventListener('input',()=>{
  inp.style.height='auto';inp.style.height=Math.min(inp.scrollHeight,80)+'px';updBtn()
});
inp.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg()}
});
send.addEventListener('click',sendMsg);

btnClear.addEventListener('click',()=>{
  if(wsSend('/clear')){}else clearUI()
});
btnNew.addEventListener('click',()=>{
  S.sid=null;clearUI();
  if(S.ws)S.ws.close();setTimeout(connect,500);
  toast('New session started','ok')
});

// Mobile menu toggle
menuBtn.addEventListener('click',()=>{
  document.getElementById('sb').classList.toggle('on')
});

// Chip suggestions
msgs.addEventListener('click',e=>{
  const c=e.target.closest('.chip');
  if(c&&c.dataset.p){inp.value=c.dataset.p;inp.style.height='auto';inp.focus();updBtn()}
});

/* ─── Helpers ─────────────────────────────────────────────── */
function updBtn(){send.disabled=!inp.value.trim()||S.busy}
function updMC(){
  const c=msgs.querySelectorAll('.msg').length;S.mc=c;
  mcEl.textContent=`${c} message${c!==1?'s':''}`;
}
function setStatus(s){
  sdot.className='dt '+s;
  stxt.textContent={on:'Connected',off:'Disconnected',busy:'Busy'}[s]||s;
}

/* ─── Init ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded',()=>{
  connect();
  updBtn();
  updMC();
  // Sidebar toggle from hamburger menu
  document.getElementById('mm').addEventListener('click',function(){
    document.getElementById('sb').classList.toggle('on');
  });
});
