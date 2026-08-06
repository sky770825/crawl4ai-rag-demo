#!/bin/bash
# auto_pipeline.sh - 自動累積 RAG + 重新部署 demo
# 每天跑 2 次,自動 dedup,自動 rebuild Surge
set -e
cd /c/Users/user/Desktop/crawl4ai
LOG=/c/Users/user/Desktop/crawl4ai/auto_pipeline.log
TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "=== $TS START ===" >> "$LOG"
# 1. 累積 RAG
/c/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe cumulative_rag.py >> "$LOG" 2>&1
# 2. 重新 build site
/c/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe build_site.py >> "$LOG" 2>&1
# 3. Surge 部署
cd /c/Users/user/Desktop/crawl4ai/site && surge . crawl4ai-rag-20260806.surge.sh >> "$LOG" 2>&1
echo "=== $TS DONE ===" >> "$LOG"
