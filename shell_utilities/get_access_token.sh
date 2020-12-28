curl --request POST \
  --url https://thea-tenant.eu.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{"client_id":"M5vr9O0av3SC13Sj6uJkvEidYu2yh9Zj","client_secret":"d3C8UGm2mccDDAa-r1ZeRsBSpCsas6SdlZlbwxha2A0PeOSkuaE-H0KFE9KPL2bQ","audience":"https://thea-core.com/api","grant_type":"client_credentials", "scope": "email"}'