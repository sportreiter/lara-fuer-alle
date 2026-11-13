#!/usr/bin/env python3
"""Scoped owner-gated GitHub Discussions adapter. No personal access tokens."""
import json
import os
import re
import sys
import urllib.request

OWNER, REPO = "sportreiter", "lara-fuer-alle"
BASE = "https://api.github.com"
APPROVAL = "vom Nutzer zur Veröffentlichung freigegeben"
Q_CATS = """query($owner:String!,$name:String!) {
 repository(owner:$owner,name:$name) {
  nameWithOwner id discussionCategories(first:100) {nodes {id name}}
 }
}"""
Q_DISC = """query($owner:String!,$name:String!,$number:Int!) {
 repository(owner:$owner,name:$name) {
  nameWithOwner discussion(number:$number) {id number url}
 }
}"""
M_CREATE = """mutation($repositoryId:ID!,$categoryId:ID!,$title:String!,$body:String!) {
 createDiscussion(input:{repositoryId:$repositoryId,categoryId:$categoryId,title:$title,body:$body}) {
  discussion {number url}
 }
}"""
M_COMMENT = """mutation($discussionId:ID!,$body:String!) {
 addDiscussionComment(input:{discussionId:$discussionId,body:$body}) {
  comment {id url}
 }
}"""

def post(url, data, token):
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req=urllib.request.Request(
        url, data=json.dumps(data).encode("utf-8"), method="POST",
        headers={"Authorization":"Bearer "+token, "Accept":"application/vnd.github+json",
                 "Content-Type":"application/json", "X-GitHub-Api-Version":"2022-11-28"})
    with opener.open(req, timeout=18) as resp:
        return json.load(resp)

def gql(q,variables,token):
    reply=post(BASE+"/graphql",{"query":q,"variables":variables},token)
    if reply.get("errors") or not isinstance(reply.get("data"),dict):
        raise ValueError("GraphQL rejected operation")
    return reply["data"]

def repo_check(result):
    r=result.get("repository")
    if not isinstance(r,dict) or r.get("nameWithOwner")!=OWNER+"/"+REPO:
        raise ValueError("repository identity mismatch")
    return r

def run():
    if os.environ.get("LARA_REPO") != OWNER+"/"+REPO:
        raise ValueError("scope mismatch")
    with open(os.environ["LARA_EVENT_PATH"],encoding="utf-8") as f:
        issue=json.load(f)["issue"]
    if issue.get("user",{}).get("login")!=OWNER or not issue.get("title","").startswith("[LaraWrite]"):
        raise ValueError("not an owner-issued request")
    raw=issue.get("body") or ""
    if len(raw)>12000:raise ValueError("payload too long")
    payload=json.loads(raw)
    if not isinstance(payload,dict):raise ValueError("payload format")
    act=payload.get("action")
    token=os.environ["LARA_GITHUB_TOKEN"]
    v={"owner":OWNER,"name":REPO}
    if act=="probe":
        if set(payload)!={"action"}:raise ValueError("unexpected fields")
        r=repo_check(gql(Q_CATS,v,token))
        names=[c["name"] for c in r["discussionCategories"]["nodes"]]
        answer="**LaraWrite-Konfiguration geprüft** (noch kein Beitrag veröffentlicht).\n\nVerfügbare Kategorien: "+", ".join(names)
    elif act=="create":
        if set(payload)!={"action","category","title","body","approval"}:raise ValueError("unexpected fields")
        if payload.get("approval")!=APPROVAL:raise ValueError("explicit user approval missing")
        title,body,category=payload["title"],payload["body"],payload["category"]
        if not all(isinstance(x,str) for x in (title,body,category)) or not 1<=len(title)<=130 or not 1<=len(body)<=5000 or not 1<=len(category)<=80:
            raise ValueError("invalid content length")
        r=repo_check(gql(Q_CATS,v,token))
        cats=[c for c in r["discussionCategories"]["nodes"] if c["name"]==category]
        if len(cats)!=1:raise ValueError("category not uniquely found")
        x=gql(M_CREATE,{"repositoryId":r["id"],"categoryId":cats[0]["id"],"title":title,"body":body},token)
        d=x.get("createDiscussion",{}).get("discussion") or {}
        if not str(d.get("url","")).startswith("https://github.com/"+OWNER+"/"+REPO+"/discussions/"):
            raise ValueError("no confirmed discussion")
        answer="**Freigegebene Discussion erstellt:** "+d["url"]
    elif act=="comment":
        if set(payload)!={"action","number","body","approval"}:raise ValueError("unexpected fields")
        if payload.get("approval")!=APPROVAL:raise ValueError("explicit user approval missing")
        num,body=payload["number"],payload["body"]
        if type(num) is not int or not 1<=num<=1000000 or not isinstance(body,str) or not 1<=len(body)<=5000:
            raise ValueError("invalid target or content")
        r=repo_check(gql(Q_DISC,{**v,"number":num},token))
        d=r.get("discussion")
        if not d or d["number"]!=num:raise ValueError("discussion not found")
        x=gql(M_COMMENT,{"discussionId":d["id"],"body":body},token)
        c=x.get("addDiscussionComment",{}).get("comment") or {}
        if not str(c.get("url","")).startswith("https://github.com/"+OWNER+"/"+REPO+"/discussions/"):
            raise ValueError("no confirmed comment")
        answer="**Freigegebener Kommentar erstellt:** "+c["url"]
    else:
        raise ValueError("unsupported action")
    post(BASE+"/repos/"+OWNER+"/"+REPO+"/issues/"+str(issue["number"])+"/comments",{"body":answer},token)
    print("LaraWrite operation completed; credential never printed.")

if __name__=="__main__":
    try: run()
    except Exception:
        print("LaraWrite request rejected or failed; check GitHub workflow permissions. Do not retry mutations blindly.",file=sys.stderr)
        sys.exit(1)
