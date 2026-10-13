# Publication deployment fix

The October 12 scheduled run committed article content but failed in Pinterest's public-asset readiness check. Scheduling and generation were not disabled. Existing schedule remains Monday, Wednesday, Friday at 08:15 UTC. Quality gates remain enabled.

Changes:
- Request a branch-based GitHub Pages build after the bot push, then require a successful build for the exact pushed commit before distribution.
- Grant the workflow Pages write permission for the build API.
- Fail explicitly if Pages uses a different branch or custom deployment workflow instead of guessing.
- Extend public-asset retry allowance from 3 to 10 minutes per asset and identify the failing public URL/status without logging webhook credentials.
- Never retry a Make POST with an unknown outcome.

Validation: three mocked tests cover a delayed exact-commit build, build failure, and an old successful build that must not unblock distribution. Live workflow execution still requires verification. Do not rerun the old failed publisher simply to retry Pinterest: it can generate the next article.

Reference: https://docs.github.com/en/rest/pages/pages#request-a-github-pages-build
