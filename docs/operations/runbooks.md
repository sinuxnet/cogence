# Cogence Operations Runbooks

**Version:** 1.0.0  
**Last Updated:** 2026-06-24  
**Applies to:** MVP-v1+

---

## Overview

This document provides step-by-step runbooks for common operational tasks. Each runbook includes prerequisites, steps, verification, and rollback procedures.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Deployment Operations](#deployment-operations)
3. [Maintenance Operations](#maintenance-operations)
4. [Emergency Operations](#emergency-operations)
5. [Data Operations](#data-operations)

---

## Daily Operations

### Runbook: Verify Daily Report Delivery

**Purpose:** Ensure yesterday's report was generated and delivered successfully.

**Frequency:** Daily at 07:30 Asia/Tehran (30 minutes after scheduled delivery)

**Prerequisites:**
- Access to Rocket.Chat
- Access to server logs
- API credentials

**Steps:**

1. **Check Rocket.Chat for report message**
   ```
   Expected: Message posted at 07:00 Asia/Tehran
   Format: "Daily Engineering Report — YYYY-MM-DD"
   ```

2. **If message not found, check delivery logs:**
   ```bash
   # Check cron logs
   grep deliver /var/log/cron | tail -20
   
   # Check delivery script logs
   tail -50 /var/log/cogence/deliver.log
   ```

3. **Verify report was generated:**
   ```bash
   DATE=$(TZ=Asia/Tehran date -d "yesterday" +%Y-%m-%d)
   curl -H "Authorization: Bearer $COGENCE_API_KEY" \
     http://localhost:8000/api/v1/reports/daily/$DATE
   ```

4. **If report exists but not delivered, retry delivery:**
   ```bash
   ./scripts/deliver.sh
   ```

5. **If report doesn't exist, generate it:**
   ```bash
   DATE=$(TZ=Asia/Tehran date -d "yesterday" +%Y-%m-%d)
   curl -X POST -H "Authorization: Bearer $COGENCE_API_KEY" \
     http://localhost:8000/api/v1/reports/daily/$DATE/generate
   
   # Then deliver
   ./scripts/deliver.sh
   ```

**Verification:**
- Report message appears in Rocket.Chat
- Report contains expected sections (executive summary, repositories, contributors)
- Metadata shows reasonable values (commits > 0, generation time < 30s)

**Escalation:**
- If report generation fails repeatedly, check [Troubleshooting Guide](troubleshooting.md)
- If LLM errors persist, verify OpenAI API status
- If data collection issues, check Gitea connectivity

---

### Runbook: Monitor System Health

**Purpose:** Check system health and performance metrics.

**Frequency:** Multiple times daily (automated monitoring recommended)

**Prerequisites:**
- Access to server
- Monitoring tools access

**Steps:**

1. **Check application health:**
   ```bash
   curl http://localhost:8000/health/ready
   ```
   
   Expected response:
   ```json
   {
     "status": "ready",
     "checks": {
       "database": {"status": "ok"},
       "gitea": {"status": "ok"},
       "openai": {"status": "ok"}
     }
   }
   ```

2. **Check system resources:**
   ```bash
   # CPU and memory
   top -bn1 | head -20
   
   # Disk space
   df -h
   
   # Docker stats
   docker stats --no-stream
   ```

3. **Check application logs for errors:**
   ```bash
   docker-compose logs cogence --tail=100 | grep -i error
   ```

4. **Check database performance:**
   ```sql
   -- Active connections
   SELECT count(*) FROM pg_stat_activity;
   
   -- Database size
   SELECT pg_size_pretty(pg_database_size('cogence'));
   ```

**Alert Thresholds:**
- CPU usage > 80%: Investigate high load
- Memory usage > 80%: Check for memory leaks
- Disk usage > 80%: Clean up old data
- Error rate > 5%: Investigate errors
- Response time P95 > 2s: Optimize queries

**Actions:**
- If degraded: Investigate specific component
- If critical: Follow emergency procedures
- If persistent issues: Escalate to engineering team

---

## Deployment Operations

### Runbook: Deploy New Version

**Purpose:** Deploy a new version of Cogence to production.

**Frequency:** As needed (typically weekly or bi-weekly)

**Prerequisites:**
- New version tested in staging
- Database migrations reviewed
- Backup completed
- Maintenance window scheduled (if needed)

**Steps:**

1. **Pre-deployment checks:**
   ```bash
   # Verify current version
   curl http://localhost:8000/health
   
   # Create backup
   ./scripts/backup.sh
   
   # Check disk space
   df -h
   ```

2. **Pull new version:**
   ```bash
   cd /opt/cogence
   git fetch origin
   git checkout v1.2.0  # Replace with actual version
   ```

3. **Update dependencies:**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   # Review migrations first
   alembic history
   
   # Apply migrations
   alembic upgrade head
   ```

5. **Restart application:**
   ```bash
   # Docker
   docker-compose down
   docker-compose up -d
   
   # Or systemd
   systemctl restart cogence
   ```

6. **Verify deployment:**
   ```bash
   # Wait for startup
   sleep 10
   
   # Check health
   curl http://localhost:8000/health/ready
   
   # Check logs
   docker-compose logs cogence --tail=50
   ```

7. **Smoke test:**
   ```bash
   # Test report generation
   DATE=$(TZ=Asia/Tehran date +%Y-%m-%d)
   curl -X POST -H "Authorization: Bearer $COGENCE_API_KEY" \
     http://localhost:8000/api/v1/reports/daily/$DATE/generate
   ```

**Verification:**
- Health endpoint returns 200
- No errors in logs
- Report generation works
- All integrations functional

**Rollback Procedure:**
```bash
# Stop application
docker-compose down

# Revert to previous version
git checkout v1.1.0  # Previous version

# Rollback database (if needed)
alembic downgrade -1

# Restart
docker-compose up -d

# Verify
curl http://localhost:8000/health/ready
```

---

### Runbook: Database Migration

**Purpose:** Apply database schema changes safely.

**Frequency:** As needed with new versions

**Prerequisites:**
- Migration scripts reviewed
- Database backup completed
- Maintenance window (if breaking changes)

**Steps:**

1. **Create backup:**
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Review migration:**
   ```bash
   # Check what will be applied
   alembic upgrade head --sql
   
   # Review the SQL
   cat alembic/versions/0003_*.py
   ```

3. **Test in staging first:**
   ```bash
   # In staging environment
   alembic upgrade head
   
   # Verify application works
   pytest tests/integration/
   ```

4. **Apply to production:**
   ```bash
   # Stop application (if needed for breaking changes)
   docker-compose stop cogence
   
   # Apply migration
   alembic upgrade head
   
   # Start application
   docker-compose start cogence
   ```

5. **Verify migration:**
   ```bash
   # Check current version
   alembic current
   
   # Check table structure
   psql $DATABASE_URL -c "\d reports"
   
   # Test application
   curl http://localhost:8000/health/ready
   ```

**Rollback Procedure:**
```bash
# Stop application
docker-compose stop cogence

# Rollback migration
alembic downgrade -1

# Restore from backup (if needed)
psql $DATABASE_URL < backup_20260624_070000.sql

# Start application
docker-compose start cogence
```

---

## Maintenance Operations

### Runbook: Database Maintenance

**Purpose:** Perform routine database maintenance to optimize performance.

**Frequency:** Weekly (Sunday 02:00 Asia/Tehran)

**Prerequisites:**
- Low traffic period
- Recent backup
- Monitoring in place

**Steps:**

1. **Check database size:**
   ```sql
   SELECT schemaname, tablename,
          pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

2. **Vacuum database:**
   ```sql
   -- Analyze tables
   ANALYZE;
   
   -- Vacuum (non-blocking)
   VACUUM;
   
   -- Full vacuum (requires downtime)
   -- VACUUM FULL;
   ```

3. **Reindex if needed:**
   ```sql
   -- Check index bloat
   SELECT schemaname, tablename, indexname,
          pg_size_pretty(pg_relation_size(indexrelid))
   FROM pg_stat_user_indexes
   ORDER BY pg_relation_size(indexrelid) DESC;
   
   -- Reindex if bloated
   REINDEX TABLE commits;
   ```

4. **Update statistics:**
   ```sql
   ANALYZE VERBOSE;
   ```

5. **Clean up old data (if retention policy exists):**
   ```sql
   -- Delete reports older than 90 days
   DELETE FROM reports 
   WHERE report_date < CURRENT_DATE - INTERVAL '90 days';
   
   -- Delete commits older than 90 days
   DELETE FROM commits 
   WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '90 days';
   ```

**Verification:**
- Database size reduced or stable
- Query performance improved
- No errors in logs
- Application still functional

---

### Runbook: Log Rotation

**Purpose:** Rotate and archive application logs to prevent disk space issues.

**Frequency:** Daily (automated via logrotate)

**Prerequisites:**
- Logrotate configured
- Archive storage available

**Configuration:**

```bash
# /etc/logrotate.d/cogence
/var/log/cogence/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 cogence cogence
    sharedscripts
    postrotate
        docker-compose restart cogence > /dev/null 2>&1 || true
    endscript
}
```

**Manual Rotation:**
```bash
# Force rotation
logrotate -f /etc/logrotate.d/cogence

# Verify
ls -lh /var/log/cogence/
```

---

### Runbook: Certificate Renewal

**Purpose:** Renew SSL/TLS certificates before expiration.

**Frequency:** Every 60 days (automated via certbot)

**Prerequisites:**
- Certbot installed
- Domain DNS configured
- Port 80/443 accessible

**Steps:**

1. **Check certificate expiration:**
   ```bash
   certbot certificates
   ```

2. **Renew certificates:**
   ```bash
   # Dry run first
   certbot renew --dry-run
   
   # Actual renewal
   certbot renew
   ```

3. **Reload web server:**
   ```bash
   # Nginx
   nginx -t && nginx -s reload
   
   # Or Apache
   apachectl configtest && systemctl reload apache2
   ```

4. **Verify renewal:**
   ```bash
   # Check expiration date
   echo | openssl s_client -connect cogence.example.com:443 2>/dev/null | \
     openssl x509 -noout -dates
   ```

**Automation:**
```bash
# Add to crontab
0 3 * * * certbot renew --quiet && nginx -s reload
```

---

## Emergency Operations

### Runbook: Service Outage Response

**Purpose:** Respond to complete service outage.

**Trigger:** Service unreachable, health checks failing

**Steps:**

1. **Assess situation:**
   ```bash
   # Check if process is running
   docker-compose ps
   systemctl status cogence
   
   # Check health endpoint
   curl http://localhost:8000/health
   ```

2. **Check logs for errors:**
   ```bash
   docker-compose logs cogence --tail=100
   journalctl -u cogence -n 100
   ```

3. **Attempt restart:**
   ```bash
   docker-compose restart cogence
   
   # Wait and verify
   sleep 10
   curl http://localhost:8000/health/ready
   ```

4. **If restart fails, check dependencies:**
   ```bash
   # Database
   docker-compose ps postgres
   psql $DATABASE_URL -c "SELECT 1"
   
   # Disk space
   df -h
   
   # Memory
   free -h
   ```

5. **If still failing, full restart:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

6. **If persistent, check for corruption:**
   ```bash
   # Check database integrity
   psql $DATABASE_URL -c "SELECT pg_database.datname FROM pg_database;"
   
   # Check file system
   docker-compose exec cogence ls -la /app
   ```

**Escalation:**
- If database corrupted: Restore from backup
- If file system issues: Contact infrastructure team
- If persistent errors: Contact development team

---

### Runbook: Database Recovery

**Purpose:** Recover from database failure or corruption.

**Trigger:** Database unreachable, data corruption detected

**Steps:**

1. **Stop application:**
   ```bash
   docker-compose stop cogence
   ```

2. **Assess database state:**
   ```bash
   # Try to connect
   psql $DATABASE_URL -c "SELECT version();"
   
   # Check for corruption
   psql $DATABASE_URL -c "SELECT pg_database.datname FROM pg_database;"
   ```

3. **If database is accessible, create backup:**
   ```bash
   pg_dump $DATABASE_URL > emergency_backup_$(date +%Y%m%d_%H%M%S).sql
   ```

4. **If database is corrupted, restore from backup:**
   ```bash
   # Drop and recreate database
   dropdb cogence
   createdb cogence
   
   # Restore from latest backup
   psql $DATABASE_URL < backup_latest.sql
   
   # Run migrations
   alembic upgrade head
   ```

5. **Verify database:**
   ```bash
   # Check tables
   psql $DATABASE_URL -c "\dt"
   
   # Check data
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM commits;"
   ```

6. **Restart application:**
   ```bash
   docker-compose start cogence
   
   # Verify
   curl http://localhost:8000/health/ready
   ```

**Post-Recovery:**
- Document what happened
- Review backup procedures
- Update monitoring alerts
- Schedule post-mortem

---

### Runbook: High Load Response

**Purpose:** Respond to high CPU/memory usage or slow performance.

**Trigger:** CPU > 90%, Memory > 90%, Response time > 5s

**Steps:**

1. **Identify resource bottleneck:**
   ```bash
   # CPU and memory
   top -bn1
   
   # Disk I/O
   iostat -x 1 5
   
   # Network
   netstat -an | grep ESTABLISHED | wc -l
   ```

2. **Check application metrics:**
   ```bash
   # Active requests
   docker-compose logs cogence | grep "GET\|POST" | tail -20
   
   # Database connections
   psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **Identify slow queries:**
   ```sql
   SELECT pid, now() - query_start as duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC
   LIMIT 10;
   ```

4. **Take immediate action:**
   ```bash
   # Kill slow queries (if safe)
   psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '5 minutes';"
   
   # Restart application if needed
   docker-compose restart cogence
   ```

5. **Scale if needed:**
   ```bash
   # Add more workers (if using Docker Compose)
   docker-compose up -d --scale cogence=3
   ```

**Follow-up:**
- Analyze slow queries and optimize
- Review and adjust resource limits
- Consider horizontal scaling
- Update monitoring thresholds

---

## Data Operations

### Runbook: Manual Data Collection

**Purpose:** Manually trigger data collection from Gitea.

**Frequency:** As needed (normally automated)

**Prerequisites:**
- Gitea accessible
- Valid API token
- Database accessible

**Steps:**

1. **Run collector:**
   ```bash
   # Using Docker
   docker-compose exec cogence python -m app.collector
   
   # Or directly
   cd /opt/cogence
   source venv/bin/activate
   python -m app.collector
   ```

2. **Monitor progress:**
   ```bash
   # Watch logs
   docker-compose logs -f cogence | grep collector
   ```

3. **Verify data collected:**
   ```sql
   -- Check recent commits
   SELECT DATE(timestamp AT TIME ZONE 'Asia/Tehran') as date,
          COUNT(*) as commits
   FROM commits
   WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
   GROUP BY date
   ORDER BY date DESC;
   ```

**Troubleshooting:**
- If no data collected: Check Gitea connectivity
- If errors: Check logs for specific issues
- If duplicates: Check unique constraints

---

### Runbook: Manual Report Generation

**Purpose:** Manually generate a report for a specific date.

**Frequency:** As needed

**Prerequisites:**
- Commits collected for the date
- LLM API accessible
- API credentials

**Steps:**

1. **Generate report via API:**
   ```bash
   DATE="2026-06-23"
   curl -X POST -H "Authorization: Bearer $COGENCE_API_KEY" \
     http://localhost:8000/api/v1/reports/daily/$DATE/generate
   ```

2. **Monitor generation:**
   ```bash
   docker-compose logs -f cogence | grep report_generation
   ```

3. **Verify report:**
   ```bash
   curl -H "Authorization: Bearer $COGENCE_API_KEY" \
     http://localhost:8000/api/v1/reports/daily/$DATE
   ```

4. **Deliver to Rocket.Chat (if needed):**
   ```bash
   # Modify deliver.sh to use specific date
   DATE=$DATE ./scripts/deliver.sh
   ```

---

### Runbook: Data Cleanup

**Purpose:** Clean up old data to free disk space.

**Frequency:** Monthly or as needed

**Prerequisites:**
- Backup completed
- Retention policy defined
- Low traffic period

**Steps:**

1. **Check current data size:**
   ```sql
   SELECT 
     'commits' as table_name,
     COUNT(*) as rows,
     pg_size_pretty(pg_total_relation_size('commits')) as size
   FROM commits
   UNION ALL
   SELECT 
     'reports' as table_name,
     COUNT(*) as rows,
     pg_size_pretty(pg_total_relation_size('reports')) as size
   FROM reports;
   ```

2. **Delete old data (90+ days):**
   ```sql
   -- Delete old reports
   DELETE FROM reports 
   WHERE report_date < CURRENT_DATE - INTERVAL '90 days';
   
   -- Delete old commits
   DELETE FROM commits 
   WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '90 days';
   ```

3. **Vacuum database:**
   ```sql
   VACUUM FULL;
   ANALYZE;
   ```

4. **Verify cleanup:**
   ```sql
   -- Check remaining data
   SELECT 
     MIN(report_date) as oldest_report,
     MAX(report_date) as newest_report,
     COUNT(*) as total_reports
   FROM reports;
   ```

---

## Related Documentation

- [Troubleshooting Guide](troubleshooting.md) - Problem diagnosis and solutions
- [Monitoring Guide](monitoring.md) - Monitoring and observability
- [Error Handling](deliver-error-handling.md) - Delivery script errors
- [System Overview](../architecture/system-overview.md) - Architecture details

---

**Last Updated:** 2026-06-24  
**Version:** 1.0.0  
**Next Review:** After MVP-v2 deployment