# Incident Runbook

## Purpose
This runbook provides a structured approach for responding to incidents affecting the PulseOps application.

## Incident Severity
- Sev1: full outage or critical data loss risk
- Sev2: major degradation affecting job submission or completion
- Sev3: minor degradation or isolated service issue

## Initial Response
1. Confirm the scope of impact.
2. Identify whether the issue affects the frontend, API, worker, PostgreSQL, or Redis.
3. Check service health endpoints:
   - `http://localhost:8000/health/live`
   - `http://localhost:8000/health/ready`
4. Review recent deployment activity, image changes, and resource saturation.

## Common Incident Scenarios
### API unhealthy
- Check PostgreSQL connectivity.
- Check Redis connectivity.
- Review API logs for startup or database connection errors.

### Worker not processing jobs
- Verify the worker pod/container is running.
- Check Redis queue contents.
- Confirm the worker can connect to PostgreSQL.

### Frontend unavailable
- Verify nginx is running.
- Confirm the frontend container is healthy.
- Check whether requests to `/api` are being proxied correctly.

## Mitigation Steps
- Restart the affected service if the issue is transient.
- Roll back to the last known good image or manifest version.
- Scale the service horizontally if capacity pressure is observed.
- Disable or pause recent changes if a regression is suspected.

## Communication
- Notify stakeholders if service availability is degraded.
- Include current status, impact, mitigation steps, and next update time.

## Post-Incident
- Document root cause and remediation.
- Update deployment or monitoring configuration if needed.
- Add preventive improvements to the runbook or automation.
