#!/bin/bash
cd /home/seth/kungfauxpandas/paper
git pull
cp /home/seth/sharelatex/sharelatex_data/data/compiles/5aecc5ba3a518f007ab52133-5aeb8780c8a91e016452182f/*.{tex,bib,sty} ./
cp -rp /home/seth/sharelatex/sharelatex_data/data/compiles/5aecc5ba3a518f007ab52133-5aeb8780c8a91e016452182f/images ./
git add *
git commit -a -m 'Auto Update from local Sharelatex'  --author="magic-lantern <magic-lantern@users.noreply.github.com>"
git push
