#!/bin/bash
export NVM_DIR="/home/evn/.nvm"
source "$NVM_DIR/nvm.sh"
cd /home/evn/web_college_site/admin-panel
npx directus start
