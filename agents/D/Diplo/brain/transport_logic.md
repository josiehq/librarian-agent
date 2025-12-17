# Diplo Transport & Authentication Logic

## Overview
D2 Diplo owns git orchestration and GitHub operations through narnia_execute and github_api tools.
In Phase 3, both tools transfer to C2 Gunash for full git management.

## Tool Ownership
**Current (Phase 1-2):**
- `narnia_execute` — D2 Diplo
- `github_api` — D2 Diplo
- `redis_queue` — D2 Diplo (memory/task queue)

**Phase 3 Transfer:**
- `narnia_execute` → C2 Gunash
- `github_api` → C2 Gunash

## Narnia CLI Transport Pattern
When copying code/repos to GitHub Codespaces for deployment:

### Authentication Flow
1. **Local machine** has `gh` CLI authenticated with personal access token (PAT)
2. **Codespace** must authenticate independently via:
   ```bash
   gh auth login
   # Or programmatically:
   echo "ghp_TOKEN" | gh auth login --with-token
   ```
3. **Never** embed tokens in:
   - Git repos
   - CLI arguments (visible in `ps`)
   - MCP tool parameters
   - Log files

### Transport Methods (ranked)

#### Option 1: gh CLI (Recommended)
```bash
# From local machine
cd /tmp
tar -czf NARNIA.tar.gz -C ~/DEV/Pythong NARNIA
gh codespace cp /tmp/NARNIA.tar.gz remote:/workspaces/librarian-agent/

# In codespace
cd /workspaces/librarian-agent
tar -xzf NARNIA.tar.gz
```

**Advantages:**
- Uses existing GitHub auth
- No SSH configuration needed
- Works through firewalls
- Built-in progress display

#### Option 2: Git Clone (For repos)
```bash
# In codespace
cd /workspaces/librarian-agent
gh repo clone josiehq/REPO_NAME
```

**Advantages:**
- Preserves git history
- Simplest for versioned code
- Automatic remote setup

#### Option 3: SSH/rsync (Advanced)
```bash
# Requires SSH key setup in codespace
rsync -avz ~/DEV/Pythong/NARNIA/ \
  super-meme-HASH.github.dev:/workspaces/librarian-agent/NARNIA/
```

**Disadvantages:**
- Host key verification issues
- SSH config complexity
- Firewall sensitivity

### Security Rules (CRITICAL)

1. **Token Handling**
   - Store in secure config: `~/.config/gh/hosts.yml`
   - Load via: `gh auth status`
   - **NEVER** echo or print tokens
   - Revoke immediately if exposed

2. **MCP Tool Invocation**
   - narnia_execute shells out to: `python3 -m narnia <command>`
   - Relies on pre-configured gh auth
   - Fails fast if auth is missing (AuthError)
   - No token parameters accepted

3. **Audit Trail**
   - All narnia calls logged to Diplo pipeline
   - Waria tracks token cost (output length / 4)
   - Exit codes returned to caller
   - Structured result: `{command, output, exit_code, success, error?}`

## Recent Transport Example
**Date:** 2025-12-17  
**Task:** Copy NARNIA (git tool) and PARAH (Visual Sovereign) to codespace

**Attempted Methods:**
1. ❌ rsync + SSH (host key verification failed)
2. ❌ tar + scp (SSH access issues)
3. ✅ gh codespace cp (succeeded)
4. ✅ gh repo clone (for git repos)

**Final Commands:**
```bash
# Local
cd /tmp
tar -czf NARNIA.tar.gz -C ~/DEV/Pythong NARNIA
tar -czf PARAH.tar.gz -C ~/DEV/GoRillah PARAH
gh codespace cp NARNIA.tar.gz remote:/workspaces/librarian-agent/
gh codespace cp PARAH.tar.gz remote:/workspaces/librarian-agent/

# Codespace
cd /workspaces/librarian-agent
tar -xzf NARNIA.tar.gz
tar -xzf PARAH.tar.gz
# Or if repos:
gh repo clone josiehq/NARNIA
gh repo clone josiehq/PARAH
```

## Integration with C2 Gunash (Phase 3)
When tool ownership transfers:

1. **C2 Gunash** inherits:
   - narnia_execute authorization
   - github_api authorization
   - All transport logic patterns

2. **Gunash Role:**
   - Supervises C1 Bash (code execution) and C3 Clash (VSCode MCP)
   - Manages git orchestration layer
   - Coordinates between Codespace environment and GitHub

3. **D2 Diplo** retains:
   - redis_queue (memory/logging)
   - Audit pipeline to Flask endpoint
   - Phase coordination logic

## Tool Signature Reference

### narnia_execute
```json
{
  "command": "see|change|write|grab|pull|create",
  "path": "string (for change)",
  "repo_url": "string (for grab)",
  "name": "string (for create)",
  "dry_run": "boolean (for write)",
  "verbose": "boolean (for write)",
  "force": "boolean (for grab)"
}
```

**Returns:**
```json
{
  "command": "string",
  "output": "string",
  "exit_code": 0,
  "success": true,
  "error": "string (if failed)"
}
```

### github_api
```json
{
  "operation": "issues|pulls|commits|...",
  "repo": "owner/repo",
  "params": {
    "issue_number": 123,
    "state": "open",
    ...
  }
}
```

## Codespace Detection
When running in codespace environment:
```bash
echo $CODESPACE_NAME  # e.g., super-meme-5g96pvg9w7724jqr
pwd                   # /workspaces/librarian-agent
```

## Future Enhancements
- [ ] Automatic token refresh via GitHub Apps
- [ ] Binary caching for faster transfers
- [ ] Delta sync for incremental updates
- [ ] Agent-to-agent direct file sharing (bypassing local machine)

---

**Maintained by:** D2 Diplo  
**Handoff target:** C2 Gunash (Phase 3)  
**Last updated:** 2025-12-17
