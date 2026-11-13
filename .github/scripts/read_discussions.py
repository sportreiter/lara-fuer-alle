#!/usr/bin/env python3
"""Read-only GitHub Discussions bridge for owner-authorized Issues. No PAT."""
import json
import os
import re
import sys
import urllib.request
import urllib.error

OWNER = "sportreiter"
REPO = "lara-fuer-alle"
API = "https://api.github.com"
MAX_BODY = 15000
Q_LIST = """query($owner:String!,$name:String!) {
  repository(owner:$owner,name:$name) {
    nameWithOwner
    discussions(first:15, orderBy:{field:UPDATED_AT,direction:DESC}) {
      nodes {number title url updatedAt comments {totalCount}}
    }
  }
}"""
Q_READ = """query($owner:String!,$name:String!,$number:Int!) {
  repository(owner:$owner,name:$name) {
    nameWithOwner
    discussion(number:$number) {
      number title url bodyText
      comments(first:15) {nodes {author {login} bodyText createdAt}}
    }
  }
}"""

def request(url, data, token):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Authorization":"Bearer "+token,
                                          "Accept":"application/vnd.github+json",
                                          "Content-Type":"application/json",
                                          "X-GitHub-Api-Version":"2022-11-28"})
    with opener.open(req, timeout=18) as response:
        return json.load(response)

def clean(text, limit=240):
    text = str(text or "")[:limit].replace("\r"," ").replace("\n"," ")
    return re.sub(r"([\\\x60*_{}\[\]()#+.!|>~-])",r"\\\1",text)

def run():
    if os.environ.get("LARA_REPO") != OWNER+"/"+REPO:
        raise ValueError("repository mismatch")
    path = os.environ["LARA_EVENT_PATH"]
    with open(path, encoding="utf-8") as stream:
        event = json.load(stream)
    issue = event["issue"]
    if issue.get("user",{}).get("login") != OWNER or not issue.get("title","").startswith("[LaraBridge]"):
        raise ValueError("not an owner-authorized bridge issue")
    body = issue.get("body") or ""
    if len(body)>MAX_BODY:
        raise ValueError("command too long")
    cmd = json.loads(body)
    if not isinstance(cmd,dict) or set(cmd)-{"action","number"}:
        raise ValueError("unknown command fields")
    act = cmd.get("action")
    if act=="list" and set(cmd)=={"action"}:
        query=Q_LIST
        variables={"owner":OWNER,"name":REPO}
    elif act=="read" and set(cmd)=={"action","number"} and type(cmd.get("number")) is int and 1<=cmd["number"]<=1000000:
        query=Q_READ
        variables={"owner":OWNER,"name":REPO,"number":cmd["number"]}
    else:
        raise ValueError("only list/read supported")
    token=os.environ["LARA_GITHUB_TOKEN"]
    data=request(API+"/graphql",{"query":query,"variables":variables},token)
    if data.get("errors"):
        raise RuntimeError("GraphQL permission or query error")
    repo=data.get("data",{}).get("repository") or {}
    if repo.get("nameWithOwner")!=OWNER+"/"+REPO:
        raise ValueError("GraphQL target mismatch")
    if act=="list":
        nodes=repo.get("discussions",{}).get("nodes") or []
        text="**LaraBridge · Discussions (lesend)**\n\n"+("\n".join(
          "- #"+str(d["number"])+" "+clean(d["title"])+" — "+str(d["comments"]["totalCount"])+" Kommentare — "+d["url"]
          for d in nodes) or "Noch keine Discussions.")
    else:
        d=repo.get("discussion")
        if not d: text="Keine Discussion mit dieser Nummer gefunden."
        else:
            text="**LaraBridge · Discussion #"+str(d["number"])+" (lesend)**\n\n**"+clean(d["title"])+"**\n\n"+clean(d.get("bodyText"),2500)
            for c in d.get("comments",{}).get("nodes") or []:
                text+="\n\n- **"+clean((c.get("author") or {}).get("login"),60)+"**: "+clean(c.get("bodyText"),700)
            text=text[:12500]
    number=int(issue["number"])
    request(API+"/repos/"+OWNER+"/"+REPO+"/issues/"+str(number)+"/comments",{"body":text},token)
    print("LaraBridge read operation completed without exposing any token")

if __name__=="__main__":
    try: run()
    except Exception:
        print("LaraBridge read failed; check workflow permissions and input. No credentials printed.",file=sys.stderr)
        sys.exit(1)
