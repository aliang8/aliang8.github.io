# /prints — passphrase-gated 3D prints viewer

`index.html` is a static gate: the passphrase is turned into an AES-256-GCM key in the browser
(PBKDF2-SHA256, 600 000 iterations), `vault/viewer.html.enc` is decrypted and rendered into an iframe,
and print files (`vault/m_*.bin.enc`) are decrypted on demand when a part's "Print file"/"DXF" link
is clicked. Nothing on GitHub can be read without the passphrase; the passphrase never leaves the browser.
Requires https (GitHub Pages) or localhost — WebCrypto is unavailable over plain http or file://.

Source of truth is the local viewer at `~/Documents/reports/viewer/` (served on the lab hub). To publish
a new version or change the passphrase:

    cd ~/Documents/reports/viewer
    python3 tools/build_public.py                      # -> build/viewer_bundle.html + build/media.json
    python3 tools/encrypt_vault.py 'NEW-PASSPHRASE' ~/Documents/aliang8.github.io/prints/vault
    cd ~/Documents/aliang8.github.io && git add prints && git commit -m "prints: rebuild vault" && git push

Deep links work through the gate: `/prints/?m=collector&part=roller_hub_upper_R&step=12`.
A `?pass=` test hook auto-fills the passphrase but only when the page is served from localhost/127.0.0.1;
it is ignored on the public host. The passphrase is kept in sessionStorage for the tab ("Lock" forgets it).
