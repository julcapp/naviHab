# NaviHab Deploy Skill
Current skill version: `1.0.0`.
Use this skill to publish websites to the NaviHab server.
## Core Flow
1. Read `GET /api/v1/agent-manifest` to check version compatibility.
2. If no Bearer token is available, start Connect Agent pairing:
   - Call `POST /api/v1/agent-connections`
   - Show the returned `connect_url` to the user.
   - Run `node skills/navihab/scripts/wait-for-navihab-token.mjs "$POLL_URL"`
   - Store the returned `token`.
3. Create or update the site via `POST /api/v1/sites`.
4. Poll `GET /api/v1/sites/{id}` until `status` is `active`.
5. Return the published `url` to the user.
