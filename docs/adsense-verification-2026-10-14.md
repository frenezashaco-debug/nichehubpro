# Public verification, October 14, 2026

- About, home, cognitive-load article, privacy and ads.txt returned HTTP 200.
- About no longer contains the old years-of-expertise claim.
- Home and cognitive-load article contain the revised title. The article contains the specific PubMed reference 25666463.
- No manual Cloudflare purge was performed.
- Fixed a stale cognitive-load title and summary in api/articles.json locally. JSON parsing and title consistency test passed. This additional change has not been committed or deployed.
- No fundingchoices, __tcfapi or cookiebot marker was found in the fetched HTML. This is not proof that a dynamically loaded or geographically targeted CMP is absent.

Next: inspect the actual AdSense Privacy & messaging configuration and test advertising consent. Analytics consent alone is not advertising consent. Do not infer account approval or activate advertising settings from source inspection alone.

Official requirement checked: https://support.google.com/adsense/answer/13554116?hl=fr
Google requires a certified TCF-integrated CMP for personalized ads to users in the EEA, UK and Switzerland.

Scope: this is a deployment and consent-readiness check, not a whole-site editorial audit or an AdSense approval guarantee.
