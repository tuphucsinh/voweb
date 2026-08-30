#!/usr/bin/env python3
"""Admin-only AI drafting helper.

It NEVER publishes. It only builds a prompt from approved/local facts and, if configured,
calls an OpenAI-compatible chat-completions endpoint. Output is a draft Markdown file.
"""
import argparse, json, os, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
claims=json.loads((ROOT/'content/claims.json').read_text())['claims']
approved=[c for c in claims if c.get('approved_vn')]

def prompt(task, locale):
    facts='\n'.join(f"- {c['key']}: {c['statement']} (source: {c['source']})" for c in approved) or '- No Vietnam-market product claims are approved yet.'
    return f'''You are the admin-only VOrigin content drafting assistant.\nTask: {task}\nLocale: {locale}\nBrand voice: quiet premium, refined, trustworthy, international, curated; never hype.\nHard rule: do not invent or infer product, health, nutrition, certification, origin, partnership or legal claims.\nApproved facts:\n{facts}\nIf the facts are insufficient, insert [NEEDS VERIFIED SOURCE] instead of guessing.\nReturn concise Markdown suitable for human review. This is a DRAFT and must never auto-publish.'''

def call_api(p):
    base=os.getenv('AI_API_BASE','').rstrip('/'); key=os.getenv('AI_API_KEY',''); model=os.getenv('AI_MODEL','')
    if not (base and key and model): return None
    req=urllib.request.Request(base+'/chat/completions',data=json.dumps({'model':model,'messages':[{'role':'user','content':p}],'temperature':0.2}).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=45) as r: data=json.load(r)
    return data['choices'][0]['message']['content']

ap=argparse.ArgumentParser(); ap.add_argument('--task',required=True); ap.add_argument('--locale',choices=['vi','en'],default='vi'); ap.add_argument('--out',default='AI_DRAFT.md'); ap.add_argument('--prompt-only',action='store_true'); args=ap.parse_args()
p=prompt(args.task,args.locale)
result=None if args.prompt_only else call_api(p)
out=Path(args.out)
out.write_text('# VOrigin AI Draft\n\n> HUMAN REVIEW REQUIRED — NEVER AUTO-PUBLISH\n\n'+(result or '## Prompt\n\n```text\n'+p+'\n```\n'),encoding='utf-8')
print(out.resolve())
