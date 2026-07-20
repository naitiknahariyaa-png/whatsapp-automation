#!/usr/bin/env python3
"""
WhatsApp Hub MASTER v5.2 - ALL Skills Integrated
"""

import os, sys, json, time, logging, threading, argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Hub")

# ═══ CONFIG ═══
class C:
    OPENWA_URL = os.getenv("OPENWA_URL", "http://localhost:3000")
    OPENWA_API_KEY = os.getenv("OPENWA_API_KEY", "")
    OPENWA_SESSION = os.getenv("OPENWA_SESSION", "default")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "WhatsApp Bot")
    PORT = int(os.getenv("PORT", "8000"))
    HEALTHCHECK_URL = os.getenv("HEALTHCHECK_URL", "")
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

C.HOST = os.getenv("HOST", "0.0.0.0")

# ═══ DATABASE ═══
class DB:
    def __init__(self, f="data/db.json"):
        self.f = Path(f); self.f.parent.mkdir(exist_ok=True)
        self.l = threading.Lock()
        self.d = self._load()
    
    def _load(self):
        if self.f.exists():
            try: return json.loads(self.f.read_text())
            except: pass
        return self._def()
    
    def _def(self):
        return {"customers":[],"leads":[],"orders":[],"messages":[],"templates":{
            "hi":"Hello! Welcome to {b}!","hello":"Hi!","price":"Competitive prices!",
            "order":"Tell: 1)Name 2)Items 3)Address","delivery":"Delivery 2-5 days!",
            "hours":"Open 9AM-9PM!","thanks":"You're welcome!"
        },"stats":{"m":0,"l":0,"o":0,"b":0,"ai":0},"rate":{}}
    
    def save(self):
        with self.l: self.f.write_text(json.dumps(self.d, indent=2))
    
    def clean(self, p):
        return str(p).replace("@c.us","").replace("@g.us","").replace("+","").replace(" ","").replace("-","")
    
    def add_c(self, p, n=None, s="m"):
        p = self.clean(p)
        for c in self.d["customers"]:
            if c["p"] == p: return False
        self.d["customers"].append({"id":f"c{len(self.d['customers'])}","p":p,"n":n or "","s":s,"t":datetime.now().isoformat()})
        self.save(); return True
    
    def add_l(self, p, m=None, s="wa"):
        p = self.clean(p)
        for l in self.d["leads"]:
            if l["p"] == p:
                l["lm"] = m or ""; l["u"] = datetime.now().isoformat()
                self.save(); return False
        self.d["leads"].append({"id":f"l{len(self.d['leads'])}","p":p,"fm":m or "","lm":m or "","s":s,"st":"new","t":datetime.now().isoformat()})
        self.d["stats"]["l"] += 1; self.add_c(p, s="lead"); self.save(); return True
    
    def add_m(self, s, m, d, ai=False, t="d"):
        self.d["messages"].append({"t":datetime.now().isoformat(),"s":self.clean(s),"m":m[:500],"d":d,"ai":ai,"rt":t})
        self.d["stats"]["m"] += 1
        if len(self.d["messages"]) > 5000: self.d["messages"] = self.d["messages"][-5000:]
        self.save()
    
    def add_t(self, k, v): self.d["templates"][k.lower()] = v; self.save()
    def del_t(self, k):
        k = k.lower()
        if k in self.d["templates"]: del self.d["templates"][k]; self.save(); return True
        return False
    def get_t(self, k): return self.d["templates"].get(k.lower())
    def all_t(self): return self.d["templates"]
    
    def match_t(self, m):
        ml = m.lower().strip()
        if ml in self.d["templates"]: return self.d["templates"][ml], "ex"
        for k, v in self.d["templates"].items():
            if k in ml: return v, "kw"
        return None, None
    
    def rate(self, p, lim=60):
        if not C.RATE_LIMIT_ENABLED: return True
        p = self.clean(p); n = time.time()
        if p not in self.d["rate"]: self.d["rate"][p] = {"c":0,"s":n}
        r = self.d["rate"][p]
        if n - r["s"] > 60: r["c"] = 0; r["s"] = n
        if r["c"] >= lim: return False
        r["c"] += 1; return True
    
    def stats(self):
        return {**self.d["stats"],"c":len(self.d["customers"]),"l":len(self.d["leads"]),"ln":len([x for x in self.d["leads"] if x["st"]=="new"]),"t":len(self.d["templates"]),"m":len(self.d["messages"])}

db = DB()

# ═══ AI ═══
class AI:
    def __init__(self):
        self.c = None; self.ok = False
        if C.GROQ_API_KEY:
            try:
                from groq import Groq
                self.c = Groq(api_key=C.GROQ_API_KEY); self.ok = True
                logger.info("AI: Groq connected")
            except: logger.warning("AI: groq not installed")
        else: logger.info("AI: No key (templates only)")
    
    def resp(self, m):
        t, mt = db.match_t(m)
        if t: return t.replace("{b}", C.BUSINESS_NAME), "tmpl"
        if self.c:
            try:
                ch = self.c.chat.completions.create(model=C.GROQ_MODEL,
                    msgs=[{"role":"sys","content":f"{C.BUSINESS_NAME} helper. SHORT."},{"role":"user","content":m}],
                    temp=0.7, max_tokens=150)
                return ch.choices[0].message.content, "ai"
            except: pass
        return "Thanks! We'll reply soon.", "def"

ai = AI()

# ═══ WHATSAPP ═══
class WA:
    def __init__(self):
        self.u = C.OPENWA_URL.rstrip("/"); self.k = C.OPENWA_API_KEY; self.s = C.OPENWA_SESSION
        self.ok = bool(self.k)
    
    def hdrs(self): return {"X-API-Key": self.k, "Content-Type": "application/json"}
    
    def conn(self):
        if not self.ok: return False
        try:
            import requests
            r = requests.get(f"{self.u}/api/connection", headers=self.hdrs(), timeout=5)
            return r.status_code == 200
        except: return False
    
    def send(self, p, t):
        if not self.ok: return False
        try:
            import requests
            p = db.clean(p)
            if not db.rate(p): return False
            r = requests.post(f"{self.u}/api/messages/sendText",
                headers=self.hdrs(), json={"session":self.s,"chatId":f"{p}@c.us","text":t}, timeout=30)
            return r.status_code == 200
        except: return False
    
    def bc(self, m, d=1):
        cs = db.d["customers"]; s = f = 0
        for c in cs:
            if self.send(c["p"], m): s += 1
            else: f += 1
            time.sleep(d)
        db.d["stats"]["b"] += 1; db.save()
        return s, f

wa = WA()

# ═══ HEALTH ═══
class HC:
    def __init__(self): self.u = C.HEALTHCHECK_URL
    def ping(self, e=""):
        if not self.u: return
        try:
            import requests
            requests.get(f"{self.u}{e}" if e else self.u, timeout=5)
        except: pass

hc = HC()

# ═══ AUTO REPLY ═══
def proc(s, m):
    s = db.clean(s); m = m.strip()
    if not s or not m: return
    db.add_m(s, m, "in")
    db.add_l(s, m)
    r, src = ai.resp(m)
    db.add_m(s, r, "out", ai=(src=="ai"), t=src)
    wa.send(s, r)

# ═══ FASTAPI ═══
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
    F = FastAPI()
    
    @F.post("/webhook")
    async def wh(request: Request):
        try:
            b = await request.json()
            p = b.get("payload", {})
            msg = p.get("message", {})
            conv = msg.get("conversation") or msg.get("extendedTextMessage",{}).get("text","") or str(msg)
            frm = p.get("from","")
            if frm and conv:
                proc(frm, conv)
                return JSONResponse({"status":"ok"})
            return JSONResponse({"status":"ignored"})
        except Exception as e:
            return JSONResponse({"status":"error","m":str(e)})
    
    @F.get("/api/status")
    async def st(): return JSONResponse({"ok":wa.conn(),"ai":ai.ok,"s":db.stats()})
    
    @F.get("/api/stats")
    async def ss(): return JSONResponse(db.stats())
    
    @F.get("/api/customers")
    async def cs(): return JSONResponse(db.d["customers"])
    
    @F.post("/api/customers/add")
    async def ca(req: Request):
        d = await req.json()
        return JSONResponse({"ok":db.add_c(d.get("p",""),d.get("n"))})
    
    @F.get("/api/leads")
    async def ls(): return JSONResponse(db.d["leads"])
    
    @F.get("/api/messages")
    async def ms(l=100): return JSONResponse(db.d["messages"][-l:])
    
    @F.get("/api/templates")
    async def ts(): return JSONResponse(db.all_t())
    
    @F.post("/api/templates/add")
    async def ta(req: Request):
        d = await req.json(); db.add_t(d.get("k",""),d.get("r",""))
        return JSONResponse({"ok":True})
    
    @F.post("/api/send")
    async def sm(req: Request):
        d = await req.json()
        if wa.send(d.get("p",""), d.get("m","")):
            db.add_m(d["p"], d["m"], "out"); return JSONResponse({"ok":True})
        return JSONResponse({"ok":False})
    
    @F.post("/api/broadcast")
    async def bc(req: Request):
        d = await req.json(); s,f = wa.bc(d.get("m",""))
        return JSONResponse({"ok":True,"s":s,"f":f})
    
    @F.get("/health")
    async def hl(): hc.ping(); return JSONResponse({"ok":True})
    
    @F.get("/", response_class=HTMLResponse)
    async def dash():
        return HTMLResponse(content='<!DOCTYPE html><html><head><meta charset="UTF-8"><title>WhatsApp Hub</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-900 text-white p-6"><h1 class="text-3xl font-bold">🤖 WhatsApp Hub</h1><p>Dashboard running!</p><div id="s" class="mt-4 grid grid-cols-4 gap-4"></div><script>fetch("/api/stats").then(r=>r.json()).then(d=>{document.getElementById("s").innerHTML=`<div class="bg-gray-800 p-4 rounded"><p class="text-gray-400">Messages</p><p class="text-2xl">${d.m}</p></div><div class="bg-gray-800 p-4 rounded"><p class="text-gray-400">Customers</p><p class="text-2xl">${d.c}</p></div><div class="bg-gray-800 p-4 rounded"><p class="text-gray-400">Leads</p><p class="text-2xl">${d.l}</p></div><div class="bg-gray-800 p-4 rounded"><p class="text-gray-400">Broadcasts</p><p class="text-2xl">${d.b}</p></div>`})</script></body></html>')
    
    FA = True
except:
    FA = False

# ═══ TELEGRAM ═══
def tg():
    if not C.TELEGRAM_BOT_TOKEN: return
    try:
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
        a = Application.builder().token(C.TELEGRAM_BOT_TOKEN).build()
        
        async def start(u,c): await u.message.reply_text(f"WhatsApp Hub\nWA: {'OK' if wa.conn() else 'NO'}\nAI: {'OK' if ai.ok else 'NO'}\n\n/stats /bc /send /leads")
        async def stats(u,c): s=db.stats(); await u.message.reply_text(f"Stats:\nMsgs:{s['m']}\nCust:{s['c']}\nLeads:{s['l']}\nBc:{s['b']}")
        async def bc(u,c):
            if not c.args: await u.message.reply_text("/bc MESSAGE"); return
            s,f=wa.bc(" ".join(c.args)); await u.message.reply_text(f"Done! Sent:{s} Failed:{f}")
        async def snd(u,c):
            if not c.args or len(c.args)<2: await u.message.reply_text("/send PHONE MSG"); return
            p,m=c.args[0]," ".join(c.args[1:])
            if wa.send(p,m): db.add_m(p,m,"out"); await u.message.reply_text("Sent!"); else: await u.message.reply_text("Failed!")
        async def leads(u,c):
            ls=db.d["leads"]
            if not ls: await u.message.reply_text("No leads!"); return
            await u.message.reply_text("\n".join([f"{l['p']}:{l.get('fm','')[:30]}" for l in ls[-5:]]))
        
        a.add_handler(CommandHandler("start",start))
        a.add_handler(CommandHandler("stats",stats))
        a.add_handler(CommandHandler("bc",bc))
        a.add_handler(CommandHandler("broadcast",bc))
        a.add_handler(CommandHandler("send",snd))
        a.add_handler(CommandHandler("leads",leads))
        a.run_polling()
    except Exception as e: logger.error(f"TG: {e}")

# ═══ MAIN ═══
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--setup",action="store_true")
    p.add_argument("--test",action="store_true")
    p.add_argument("--web",action="store_true")
    p.add_argument("--telegram",action="store_true")
    a = p.parse_args()
    
    if a.setup:
        print("\n=== Setup ===\nOpenWA URL:", end=" ")
        if input(): C.OPENWA_URL = input().strip()
        print("OpenWA API Key:", end=" ")
        k = input().strip()
        if k: C.OPENWA_API_KEY = k
        print("Groq Key (optional):", end=" ")
        k = input().strip()
        if k: C.GROQ_API_KEY = k
        Path(".env").write_text(f"OPENWA_URL={C.OPENWA_URL}\nOPENWA_API_KEY={C.OPENWA_API_KEY}\nGROQ_API_KEY={C.GROQ_API_KEY}\n")
        print("Done!"); return
    
    if a.test:
        print(f"\n=== Test ===\nDB: OK\nWA: {'OK' if wa.conn() else 'FAIL'}\nAI: {'OK' if ai.ok else 'FAIL'}\n"); return
    
    print(f"\n{'='*50}\nWhatsApp Hub v5.2\nWA: {'OK' if wa.conn() else 'NO'}\nAI: {'OK' if ai.ok else 'NO'}\nCustomers: {len(db.d['customers'])}\n{'='*50}\n")
    
    if FA:
        print(f"Web: http://localhost:{C.PORT}\nWebHook: http://IP:{C.PORT}/webhook\n")
        import threading
        threading.Thread(target=lambda: uvicorn.run(F,host=C.HOST,port=C.PORT,log_level="error"),daemon=True).start()
    
    if C.TELEGRAM_BOT_TOKEN:
        tg()
    else:
        while True: time.sleep(300)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nDone!")
