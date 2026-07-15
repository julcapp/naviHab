#!/usr/bin/env node
const https = require('https');
const http = require('http');
const pollUrl = process.argv[2];
if (!pollUrl) { console.error('Usage: node wait-for-navihab-token.mjs <poll_url>'); process.exit(1); }
const url = new URL(pollUrl.startsWith('http') ? pollUrl : `http://localhost:8000${pollUrl}`);
const lib = url.protocol === 'https:' ? https : http;
console.log(`Polling ${url.href} for approval...`);
function poll() {
  const req = lib.get(url, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
      try {
        const json = JSON.parse(data);
        if (json.status === 'approved' && json.token) {
          console.log(`\n✅ Approved! Token: ${json.token}`);
          process.exit(0);
        } else {
          console.log('⏳ Waiting for user approval...');
          setTimeout(poll, 3000);
        }
      } catch (e) { setTimeout(poll, 3000); }
    });
  });
  req.on('error', () => setTimeout(poll, 3000));
}
poll();
