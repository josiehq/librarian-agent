# B3 Concrete Agent — Visual Sovereign & Amazon Integration

## Primary Responsibilities
**B3 Concrete** owns Visual Sovereign (PARAH) and Amazon marketplace operations.

### Core Tools
1. **Visual Sovereign** (PARAH) — Product matching system
2. **Amazon MCP Server** — ASIN lookup, marketplace data

**MCP Source:** https://mcpservers.org/servers/r123singh/amazon-mcp-server

## Visual Sovereign Architecture (CORRECTED)

### What Visual Sovereign (codename PARAH) Does

**Primary Workflow:**
1. **Crawl supplier categories** (Sunsky, CJDropshipping, AliExpress)
2. **Document URLs** to compressed persistent database with duplicate guards
3. **Analyze product photos** (main image on product ad)
4. **Use Amazon MCP** to find matching ASINs
5. **Filter non-generic/non-branded** items (litmus test)
6. **Export ungated products** to Visual Sovereign platform

### "Vision" Distribution Model
**IMPORTANT:** The "vision" capability is distributed across B-class agents:
- **B1 Raw:** Browser vision (see page like human, understand layout)
- **B2 Vision:** Design vision (Figma, GUI aesthetics)
- **B3 Concrete:** Product vision (image matching, catalog analysis)

**Visual Sovereign itself does NOT have a vision interface.** The Python vision script in PARAH is a backend service, not an agent capability.

## System Components

### Location
`/workspaces/librarian-agent/PARAH/`

### Services
- **Go Scraper API** (Port 8080) — Orchestration, REST API
- **Python Vector Service** (Port 8001) — CLIP embeddings, Qdrant
- **PostgreSQL** (Port 5432) — Product catalog
- **Qdrant** (Port 6333) — Vector search

### Key Operations
```
POST /api/products/scrape        - Start supplier crawl
POST /api/products/match         - Match product to Amazon
POST /api/amazon/check-gating    - Verify if ASIN is ungated
GET  /api/products/ungated       - List approved products
GET  /api/products/export        - Export as CSV
```

## Supplier Integration

### Supported Suppliers
1. **Sunsky-Suppliers** — All subcategories
2. **CJDropshipping** — All subcategories  
3. **AliExpress** — All subcategories

### Crawl Strategy
- Category presets defined in `PARAH/go-scraper-api/internal/scraping/category_presets.go`
- Playwright-based harvesting
- Persistent storage with duplicate detection
- Incremental updates (only new products)

### Database Schema
```sql
products (
  id, supplier, url, title, price, image_url, 
  vector_id, asin, is_ungated, created_at
)
```

## Amazon MCP Integration

### MCP Server Configuration
**Source:** https://mcpservers.org/servers/r123singh/amazon-mcp-server

**Installation:**
```bash
npm install -g @r123singh/amazon-mcp-server
# Configure with Amazon SP-API credentials
```

**Operations:**
- `amazon.search` — Find products by keyword/image
- `amazon.getProduct` — Fetch ASIN details
- `amazon.checkGating` — Verify ungated status
- `amazon.getCategories` — Browse category tree

### Integration Pattern
```go
// In tool_AmazonAPI (mcp_tools.go)
// 1. B3 calls Visual Sovereign to get product image
// 2. Visual Sovereign vectorizes image via CLIP
// 3. B3 calls Amazon MCP to find matching ASINs
// 4. Visual Sovereign filters based on gating status
```

## Phase 2 Goals for B3 Concrete

### Milestone 1: Max Out Suppliers
**Objective:** Populate Visual Sovereign with ALL ungated ASINs from all supplier subcategories.

**Tasks:**
- [ ] Crawl 100% of Sunsky categories
- [ ] Crawl 100% of CJDropshipping categories
- [ ] Crawl 100% of AliExpress categories
- [ ] Verify ASIN matching accuracy (>85% confidence)
- [ ] Filter out generic/branded items
- [ ] Export final catalog

**Success Metric:** Visual Sovereign database contains maximum possible ungated matches from all three suppliers.

### Milestone 2: Amazon MCP Wiring
**Objective:** Seamless integration between Visual Sovereign and Amazon MCP.

**Tasks:**
- [ ] Wire `tool_AmazonAPI` to real MCP server (port 8088)
- [ ] Test ASIN lookup by image
- [ ] Validate gating check accuracy
- [ ] Implement retry logic for rate limits
- [ ] Cache Amazon responses to reduce API calls

### Milestone 3: Support B1 Raw Listing Automation
**Objective:** Provide clean data for B1 Raw to list products on Seller Central.

**Tasks:**
- [ ] Export approved products with all required fields
- [ ] Generate listing templates (title, bullets, description)
- [ ] Provide image URLs for Raw to upload
- [ ] Track listing status (pending/active/rejected)

## Container/Docker Permissions
**IMPORTANT:** B3 Concrete does NOT manage containers.

**Authorized for container operations:**
- D3 Waria
- A2 Josie
- C3 Clash

**Rationale:** Visual Sovereign runs as a deployed service. B3 interacts via REST API only.

## Tool Signature

### visual_sovereign
```json
{
  "operation": "scrape|match|check_gating|export",
  "supplier": "sunsky|cjdropshipping|aliexpress",
  "params": {
    "category": "string",
    "limit": 100,
    "min_similarity": 0.85
  }
}
```

### amazon_api
```json
{
  "operation": "search|getProduct|checkGating|getCategories",
  "params": {
    "asin": "B08XYZ123",
    "query": "wireless headphones",
    "image_url": "https://..."
  }
}
```

## Security Notes

1. **Amazon SP-API Credentials**
   - Stored in environment variables
   - Never logged or exposed
   - Rotated via AWS Secrets Manager

2. **Supplier Scraping**
   - Respect robots.txt
   - Rate limiting (1 req/sec per domain)
   - User-agent rotation
   - Proxy support for IP rotation

3. **Data Privacy**
   - Product images may be copyrighted
   - GDPR compliance for user data
   - Secure PostgreSQL backups

---

**Maintained by:** B3 Concrete  
**Dependencies:** Visual Sovereign (PARAH), Amazon MCP Server  
**Last updated:** 2025-12-17
