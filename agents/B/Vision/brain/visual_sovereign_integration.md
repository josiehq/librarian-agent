# B2 Vision Agent — Figma Interface Specialist

## Primary Responsibility
**B2 Vision** handles frontend/GUI design and prototyping via Figma MCP integration.

**Core Tool:** Figma MCP Server  
**Source:** https://mcpservers.org/servers/mohammeduvaiz/figma-mcp-server

**IMPORTANT:** Visual Sovereign (PARAH) is NOT assigned to Vision. It belongs to B3 Concrete.

## Figma MCP Integration

### Go Scraper API (Port 8080)
- **Path:** `PARAH/go-scraper-api/`
- **Role:** Orchestrates scraping, handles REST API
- **Key functions:**
  - Playwright-based web scraping
  - Supplier config management
  - Product data normalization
  - Amazon SP-API gating checks

### Python Vector Service (Port 8001)
- **Path:** `PARAH/python-vector-service/`
- **Role:** CLIP model inference for image vectorization
- **Key functions:**
  - Image embedding generation
  - Vector similarity search
  - Qdrant database operations

### Streamlit Dashboard (Port 8501)
- **Path:** `PARAH/frontend-streamlit/`
- **Role:** User interface for product matching workflow

### Data Stores
- **PostgreSQL** (Port 5432): Products, matches, supplier data
- **Qdrant** (Port 6333): Vector embeddings

## Agent Integration Strategy

### Agent Assignment (CORRECTED)
**B2 Vision:**
- Figma API/MCP for frontend design
- GUI prototyping and interface creation
- Does NOT own Visual Sovereign

**B3 Concrete:**
- Visual Sovereign/PARAH (product matching)
- Amazon MCP server integration
- Supplier catalog crawling and ASIN matching

### MCP Tool Mapping

#### Current Stub: `visual_sovereign`
**Location:** `go/kernel/mcp_tools.go:648`  
**Status:** Placeholder — returns "not yet implemented"

#### Proposed Operations:
```json
{
  "operation": "scrape|vectorize|match|check_gating|export",
  "supplier": "cjdropshipping|sunsky|aliexpress",
  "params": {
    "category": "string",
    "limit": 100,
    "min_similarity": 0.85
  }
}
```

### REST API Endpoints (Go Scraper)
```
GET  /health
GET  /api/products
POST /api/scrape
POST /api/match
GET  /api/suppliers
POST /api/check-gating
```

### Integration Implementation Plan

#### Phase 1: Direct HTTP Proxy
Wire `tool_VisualSovereign` to forward requests to `http://localhost:8080/api/`

```go
func (s *MCPServer) tool_VisualSovereign(args map[string]interface{}, agentID string) (interface{}, error) {
    operation, okOp := args["operation"].(string)
    params, _ := args["params"].(map[string]interface{})
    
    // Map operation to REST endpoint
    endpoint := mapOperationToEndpoint(operation)
    
    // POST to http://localhost:8080/api/<endpoint>
    resp, err := http.Post(visualSovereignURL + endpoint, "application/json", payload)
    
    // Return structured result
    return parseVisualSovereignResponse(resp)
}
```

#### Phase 2: Docker Compose Integration
Add Visual Sovereign services to librarian-agent deployment:

```yaml
services:
  visual-sovereign-api:
    build: ./PARAH/go-scraper-api
    ports:
      - "8080:8080"
    environment:
      - VECTOR_SERVICE_URL=http://vector-service:8001
      - POSTGRES_DSN=...
      
  vector-service:
    build: ./PARAH/python-vector-service
    ports:
      - "8001:8001"
    environment:
      - QDRANT_URL=http://qdrant:6333
```

#### Phase 3: Agent Workflow
B2 Vision can invoke Visual Sovereign for:

1. **Product Research**
   - Scrape supplier catalogs
   - Build product database

2. **Market Analysis**
   - Match products to Amazon listings
   - Check gating status
   - Export ungated opportunities

3. **Visual Intelligence**
   - Image similarity searches
   - Product clustering by visual features
   - Trend detection via image analysis

## Authorization Matrix (CORRECTED)

**B2 Vision tools:**
```go
"B2_Vision": {"figma_api"}
```

**B3 Concrete tools:**
```go
"B3_Concrete": {"amazon_api", "visual_sovereign"}
```

**MCP Server Sources:**
- Figma: https://mcpservers.org/servers/mohammeduvaiz/figma-mcp-server
- Amazon: https://mcpservers.org/servers/r123singh/amazon-mcp-server
- Visual Sovereign: PARAH Go API (localhost:8080)

## Startup Requirements

### Environment Variables
```bash
# Amazon SP-API Credentials
SP_API_CLIENT_ID=...
SP_API_CLIENT_SECRET=...
SP_API_REFRESH_TOKEN=...

# Database
POSTGRES_DSN=postgres://user:pass@localhost:5432/visualsovereign
QDRANT_URL=http://localhost:6333

# Service URLs
VECTOR_SERVICE_URL=http://localhost:8001
GO_API_URL=http://localhost:8080
```

### Docker Compose Launch
```bash
cd /workspaces/librarian-agent/PARAH
docker-compose up -d

# Verify health
curl http://localhost:8080/health
curl http://localhost:8001/health
```

## Security Considerations

1. **Amazon SP-API Credentials**
   - Never log or expose tokens
   - Rotate refresh tokens periodically
   - Use AWS Secrets Manager in production

2. **Scraping Ethics**
   - Respect robots.txt
   - Rate limit requests
   - User-agent identification

3. **Data Privacy**
   - Product data may contain copyrighted images
   - GDPR compliance for user data
   - Secure database backups

## Testing Strategy

### Unit Tests
- Scraper logic (PARAH/go-scraper-api/internal/scraping/)
- Vector similarity (PARAH/python-vector-service/)

### Integration Tests
- MCP tool → Go API → Vector Service
- End-to-end product matching workflow

### Load Tests
- Concurrent scraping jobs
- Vector search performance
- Database connection pooling

## Handoff to B-Class Implementation

**Next Steps:**
1. ✅ Document architecture (this file)
2. ⏳ Implement B1 Raw tools (browser_navigate, web_crawl)
3. ⏳ Implement B2 Vision tool (figma_api + visual_sovereign)
4. ⏳ Implement B3 Concrete tool (amazon_api)
5. ⏳ Wire Visual Sovereign backend to B2 Vision MCP tool

**Dependencies:**
- Visual Sovereign must be running (docker-compose up)
- PostgreSQL + Qdrant must be accessible
- Amazon SP-API credentials configured

---

**Maintained by:** B2 Vision (visual intelligence lead)  
**Backend system:** Visual Sovereign (PARAH)  
**Last updated:** 2025-12-17
