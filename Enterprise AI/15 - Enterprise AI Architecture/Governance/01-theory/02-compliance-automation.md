# Compliance Automation

## Automated Compliance Gates

| Gate | Trigger | Check | Action |
|------|---------|-------|--------|
| Registration | New model created | Risk tier auto-assigned | Block if incomplete |
| Development | PR created | Model card updated | Block if missing |
| Pre-deploy | Deploy initiated | All checks passed | Auto-approve if T1-T2 |
| Canary | Canary start | Metrics OK | Promote or rollback |
| Production | Full rollout | Final approval recorded | Allow deploy |
| Monitoring | Continuous | Compliance drift | Alert on deviation |

## Evidence Automation

| Evidence | Collection | Storage | Retention |
|----------|-----------|---------|-----------|
| Model documentation | Auto-generated from metadata | Registry | Lifetime of model |
| Audit trail | Immutable log | Log store | 3 years |
| Bias audit | Scheduled job | Results DB | 3 years |
| Incident report | Post-incident workflow | Incident system | 5 years |
| Deployment record | CI/CD pipeline | Artifact store | 3 years |
