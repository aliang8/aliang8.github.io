#!/bin/bash
# Republish the policy-customization report to aliang8.github.io whenever the local report changes (checks every 20 min).
SITE=~/Documents/aliang8.github.io; SRC=~/Documents/reports/policy_customization; SLUG=policy-customization
while true; do
  cd "$SITE" || exit 1
  newest=$(find "$SRC" -maxdepth 2 \( -name '*.html' -o -name '*.png' -o -name '*.mp4' \) -newer "reports/$SLUG/manifest.json" | head -1)
  if [ -n "$(find "$SRC" -maxdepth 1 -name '*.html' -size -200c)" ]; then   # an empty page means a rebuild is mid-write or broke
    echo "$(date '+%m-%d %H:%M') skipped: empty page" >> /tmp/autopublish.log; sleep 300; continue
  fi
  if [ -n "$newest" ]; then
    git pull -q --rebase origin master
    python3 tools/build_report_vault.py "$SRC" "$SLUG" >/dev/null && git add -A "reports/$SLUG" &&
      git -c user.name="Anthony Liang" -c user.email=aliang80@usc.edu commit -qm "reports: republish" && git push -q origin master &&
      echo "$(date '+%m-%d %H:%M') republished" >> /tmp/autopublish.log
  fi
  sleep 1200
done
