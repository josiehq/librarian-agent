# Phase 2: B-Rank Agent Deployment

## Overview
Phase 2 introduces the B-class builder agents with specialized tools for visual design, data processing, and web automation. This phase culminates in testing Visual Sovereign for the first time.

**Status**: Checkpoint 2 of 2  
**Deployment Type**: Monolithic (extends Phase 1)  
**New Components**: B1-B4 agents + specialized MCP tools

---

## Agent Roster - B Class

### B1: Raw
- **Role**: Web Automation & Data Scraping
- **Primary Function**: Browser automation and raw-to-structured data conversion
- **Capabilities**:
  - Selenium/Playwright browser control
  - Raw data extraction
  - Data structure conversion
  - Web scraping with anti-detection
- **Tools**: Selenium + Playwright MCP (or equivalent powerful combo)
- **Testing Priority**: HIGH - First browser tool test
- **Status**: Practice job phase

### B2: Vision
- **Role**: Visual Design & Prototyping
- **Primary Function**: Figma integration for UI/UX design
- **Capabilities**:
  - Figma API integration
  - Design asset management
  - Component library access
  - Visual mockup generation
- **Tools**: Figma MCP
- **Dependencies**: Raw (for design-to-code pipeline)
- **Status**: Practice job phase

### B3: Concrete
- **Role**: Data Validation & Testing
- **Primary Function**: Visual Sovereign tool testing with Amazon MCP
- **Capabilities**:
  - E-commerce data validation
  - Visual Sovereign integration testing
  - Amazon product data handling
  - Business data verification
- **Tools**: 
  - Amazon MCP Server (https://mcpservers.org/servers/r123singh/amazon-mcp-server)
  - Visual Sovereign (~/DEV/GoRillah/PARAH)
- **Testing Priority**: CRITICAL - First child build test after full deployment
- **Status**: First real job assignment

### B4: Kirktower
- **Role**: Infrastructure Core
- **Primary Function**: Central coordination and MCP orchestration
- **Capabilities**:
  - MCP server management
  - Agent coordination
  - Resource allocation
  - System monitoring
- **Tools**: kirktower.go (built in Phase 1)
- **Note**: Ready for jobs, fully deployed from Phase 1
- **Status**: Operational

---

## Architecture Extension

```
         D-Class Triangle
        /       |       \
       /        |        \
    D1         D2         D3
     |          |          |
     |          |          |
  [B-Class Layer]─────────────
     |    |     |     |
    B1   B2   B3    B4
   Raw  Vision Concrete Kirktower
```

### MCP Monolith Structure
All Phase 2 tools plug into the single mcp_server.go:

```
mcp_server.go
├── Phase 1 Tools
│   ├── neovim-mcp (D1)
│   ├── github-narnia-mcp (D2)
│   └── fabric-mcp (D3)
└── Phase 2 Tools
    ├── selenium-playwright-mcp (B1)
    ├── figma-mcp (B2)
    └── amazon-mcp (B3)
```

---

## Deployment Sequence

### Step 1: Deploy B-Class Agent Infrastructure

```bash
# On VPS, continuing from Phase 1
cd ~/librarian-agent-deploy/librarian-agent

# Deploy B1 Raw
cd agents/B/Raw
python3 -m venv venv
source venv/bin/activate
pip install selenium playwright beautifulsoup4 lxml
playwright install chromium

export RAW_API_KEY="your-api-key"
export RAW_MODEL="gpt-4"

# Start B1 as service
python3 -m raw.main --mode scraper-service &
```

### Step 2: Configure Specialized MCP Tools

#### B1 Raw: Selenium + Playwright MCP

**Service Name**: selenium-playwright-mcp  
**Description**: Unified browser automation with Selenium and Playwright  
**Purpose**: Web scraping, data extraction, browser testing

**Authentication**: None (local browser control)

**API Documentation**:
- Selenium: https://www.selenium.dev/documentation/
- Playwright: https://playwright.dev/python/docs/api/class-playwright

**Configuration** (add to mcp_server.go):
```json
{
  "tool": "selenium-playwright-mcp",
  "agent": "B1-Raw",
  "capabilities": {
    "selenium": {
      "driver": "chromium",
      "headless": true,
      "user_agent_rotation": true,
      "proxy_support": true
    },
    "playwright": {
      "browser": "chromium",
      "context_options": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0..."
      },
      "anti_detection": true
    }
  },
  "output_formats": ["json", "csv", "xml", "structured_dict"],
  "data_extraction": {
    "css_selectors": true,
    "xpath": true,
    "regex_patterns": true,
    "ai_structure_inference": true
  }
}
```

**Output Preferences**:
```python
{
    "raw_html": False,  # Don't return raw HTML
    "structured_data": True,  # Always return structured JSON
    "screenshots": "on_error",  # Capture screenshots only on errors
    "trace": "on_failure",  # Playwright trace on failures
    "cache_strategy": "aggressive"  # Work with Diplo's caching
}
```

**Installation**:
```bash
# Add to mcp_server.go
cd ~/librarian-agent-deploy/librarian-agent/go/kernel

# Create MCP tool registration
cat >> mcp_tools.go <<EOF
func RegisterSeleniumPlaywrightMCP() {
    tool := MCPTool{
        Name: "selenium-playwright-mcp",
        Agent: "B1-Raw",
        Endpoint: "http://localhost:9001/browser",
        Type: "browser-automation",
    }
    RegisterTool(tool)
}
EOF

# Restart MCP server
pkill mcp_server
go build -o mcp_server *.go
./mcp_server --port 8080 &
```

---

#### B2 Vision: Figma MCP

**Service Name**: figma-mcp  
**Description**: Figma design tool integration  
**Purpose**: UI/UX design, component generation, asset management

**Authentication**: Figma Personal Access Token

**API Documentation**: https://www.figma.com/developers/api

**Configuration**:
```json
{
  "tool": "figma-mcp",
  "agent": "B2-Vision",
  "auth": {
    "token": "${FIGMA_ACCESS_TOKEN}",
    "token_type": "personal"
  },
  "capabilities": {
    "read_files": true,
    "export_assets": true,
    "create_components": true,
    "update_designs": true,
    "version_control": true
  },
  "export_formats": ["svg", "png", "jpg", "pdf"],
  "component_library": {
    "team_id": "${FIGMA_TEAM_ID}",
    "project_id": "${FIGMA_PROJECT_ID}"
  }
}
```

**Output Preferences**:
```python
{
    "format": "svg",  # Prefer vector graphics
    "resolution": "2x",  # High-DPI exports
    "include_metadata": True,  # Component names, styles
    "css_generation": True,  # Auto-generate CSS from designs
    "component_tree": True,  # Return hierarchical structure
    "design_tokens": True  # Extract design system tokens
}
```

**Setup**:
```bash
# Get Figma token
echo "Visit: https://www.figma.com/developers/api#access-tokens"
read -p "Enter Figma token: " FIGMA_TOKEN

export FIGMA_ACCESS_TOKEN="$FIGMA_TOKEN"
export FIGMA_TEAM_ID="your-team-id"
export FIGMA_PROJECT_ID="your-project-id"

# Deploy B2 Vision
cd ~/librarian-agent-deploy/librarian-agent/agents/B/Vision
python3 -m venv venv
source venv/bin/activate
pip install requests pillow

export VISION_API_KEY="your-api-key"
python3 -m vision.main --mode design-service &
```

---

#### B3 Concrete: Amazon MCP

**Service Name**: amazon-mcp-server  
**Description**: Amazon product data and e-commerce integration  
**Purpose**: Testing Visual Sovereign with real e-commerce data

**Authentication**: Amazon API credentials (Product Advertising API)

**API Documentation**: 
- https://mcpservers.org/servers/r123singh/amazon-mcp-server
- https://webservices.amazon.com/paapi5/documentation/

**Configuration**:
```json
{
  "tool": "amazon-mcp-server",
  "agent": "B3-Concrete",
  "auth": {
    "access_key": "${AMAZON_ACCESS_KEY}",
    "secret_key": "${AMAZON_SECRET_KEY}",
    "partner_tag": "${AMAZON_PARTNER_TAG}",
    "region": "us-east-1"
  },
  "capabilities": {
    "search_products": true,
    "get_product_details": true,
    "get_pricing": true,
    "get_reviews": true,
    "get_images": true
  },
  "rate_limiting": {
    "requests_per_second": 1,
    "burst_capacity": 5
  }
}
```

**Visual Sovereign Integration**:
```bash
# Visual Sovereign location
VS_PATH="$HOME/DEV/GoRillah/PARAH"

# Link to B3 Concrete
export VISUAL_SOVEREIGN_PATH="$VS_PATH"
export CONCRETE_AMAZON_MCP="enabled"

# Deploy B3 Concrete
cd ~/librarian-agent-deploy/librarian-agent/agents/B/Concrete
python3 -m venv venv
source venv/bin/activate
pip install boto3 requests

export CONCRETE_API_KEY="your-api-key"
python3 -m concrete.main --mode validator &
```

**Output Preferences**:
```python
{
    "product_data_format": "structured_json",
    "include_images": True,
    "image_processing": "resize_and_optimize",
    "price_tracking": True,
    "review_sentiment_analysis": True,
    "cache_product_data": True,  # Work with Diplo
    "visual_sovereign_feed": {
        "enabled": True,
        "format": "parah_compatible",
        "validation_rules": "strict"
    }
}
```

**Installation**:
```bash
# Install Amazon MCP Server
npm install -g @r123singh/amazon-mcp-server

# Configure
cat > ~/.amazon-mcp-config.json <<EOF
{
  "accessKey": "${AMAZON_ACCESS_KEY}",
  "secretKey": "${AMAZON_SECRET_KEY}",
  "partnerTag": "${AMAZON_PARTNER_TAG}",
  "region": "us-east-1"
}
EOF

# Start Amazon MCP
amazon-mcp-server --port 9002 &

# Register with main MCP server
curl -X POST http://localhost:8080/api/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "amazon-mcp-server",
    "agent": "B3-Concrete",
    "endpoint": "http://localhost:9002"
  }'
```

---

## Diplo's Smart Caching Implementation

### Phase 2 Caching Priorities

D2 Diplo implements intelligent caching for all B-class data operations:

```python
# In agents/D/Diplo/brain/caching.py

CACHE_STRATEGIES = {
    "B1_Raw_Scraping": {
        "ttl": 3600,  # 1 hour for scraped data
        "compression": "zstd",
        "storage": "redis",
        "invalidation": "time_based"
    },
    "B2_Vision_Assets": {
        "ttl": 86400,  # 24 hours for Figma assets
        "compression": "gzip",
        "storage": "filesystem",
        "invalidation": "version_based"
    },
    "B3_Amazon_Products": {
        "ttl": 7200,  # 2 hours for product data
        "compression": "zstd",
        "storage": "redis",
        "invalidation": "smart"  # Price changes trigger invalidation
    },
    "Logs": {
        "build_logs": {
            "compression": "gzip",
            "retention": "30_days",
            "rotation": "daily"
        },
        "error_logs": {
            "compression": "zstd",
            "retention": "90_days",
            "rotation": "weekly"
        },
        "change_logs": {
            "compression": "gzip",
            "retention": "1_year",
            "rotation": "monthly"
        }
    }
}
```

**Setup**:
```bash
# Install Redis for caching
sudo apt-get update
sudo apt-get install redis-server

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Update Diplo configuration
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Diplo
pip install redis zstandard

# Restart Diplo with caching enabled
pkill -f diplo.main
python3 -m diplo.main --daemon --mode git-monitor --enable-caching
```

---

## Practice Jobs for B-Class

### B1 Raw: Browser Automation Practice
```bash
# Test 1: Scrape a simple website
curl -X POST http://localhost:8080/api/agents/B1/task \
  -d '{
    "type": "scrape",
    "url": "https://example.com",
    "extract": ["title", "links", "text"]
  }'

# Test 2: Convert scraped data to structured format
curl -X POST http://localhost:8080/api/agents/B1/task \
  -d '{
    "type": "structure",
    "input": "raw_html_data",
    "schema": "auto_infer"
  }'
```

### B2 Vision: Figma Integration Practice
```bash
# Test 1: Export a Figma component
curl -X POST http://localhost:8080/api/agents/B2/task \
  -d '{
    "type": "export",
    "figma_file_id": "your-file-id",
    "node_id": "component-node-id",
    "format": "svg"
  }'

# Test 2: Generate CSS from Figma design
curl -X POST http://localhost:8080/api/agents/B2/task \
  -d '{
    "type": "generate_css",
    "figma_file_id": "your-file-id",
    "component": "button-primary"
  }'
```

### B3 Concrete: Visual Sovereign Testing
```bash
# Test 1: Fetch product data via Amazon MCP
curl -X POST http://localhost:8080/api/agents/B3/task \
  -d '{
    "type": "fetch_product",
    "asin": "B08N5WRWNW",
    "details": ["price", "reviews", "images"]
  }'

# Test 2: Feed data to Visual Sovereign
curl -X POST http://localhost:8080/api/agents/B3/task \
  -d '{
    "type": "test_visual_sovereign",
    "data_source": "amazon",
    "product_count": 10,
    "validation_mode": "strict"
  }'
```

---

## Checkpoint 2 Success Criteria

### MCP Tool Integration
- [ ] Selenium/Playwright MCP operational on B1 Raw
- [ ] Figma MCP operational on B2 Vision
- [ ] Amazon MCP operational on B3 Concrete
- [ ] All three tools registered in mcp_server.go
- [ ] Diplo's smart caching active for all B-class operations

### Agent Functionality
- [ ] B1 successfully scrapes and structures web data
- [ ] B2 successfully exports Figma assets
- [ ] B3 successfully fetches Amazon product data
- [ ] B4 Kirktower coordinates B-class agents
- [ ] All B-class agents communicate through triangular D-class pipeline

### Visual Sovereign Test
- [ ] Visual Sovereign tool accessible at ~/DEV/GoRillah/PARAH
- [ ] B3 Concrete successfully feeds data to Visual Sovereign
- [ ] First child build test completes without errors
- [ ] Results validated and cached by Diplo

---

## Terminal Notification

When Checkpoint 2 is reached, Puckfairy (D1) will notify the user:

```
═══════════════════════════════════════════════════════════
  CHECKPOINT 2 REACHED - B-RANK DEPLOYMENT COMPLETE
═══════════════════════════════════════════════════════════

✓ B1 Raw: Browser automation active (Selenium + Playwright)
✓ B2 Vision: Figma integration active
✓ B3 Concrete: Amazon MCP + Visual Sovereign testing complete
✓ B4 Kirktower: Infrastructure coordination operational

✓ MCP Monolith extended with 3 new tools:
  - selenium-playwright-mcp
  - figma-mcp
  - amazon-mcp-server

✓ Diplo smart caching implemented:
  - Scraped data compression
  - Build log management
  - Business data caching

✓ First child build tested:
  - Visual Sovereign integration successful
  - Amazon product data validated
  
═══════════════════════════════════════════════════════════
  System Status: 7 agents deployed (D1-D3, B1-B4)
  Ready for Phase 3 (C-Rank Deployment)
═══════════════════════════════════════════════════════════

Continue building? (y/n): _
Stop and save? (s)
Stay at this level? (l)

Your choice: _
```

---

## Troubleshooting

### Issue: Selenium/Playwright browser won't start
```bash
# Install browser dependencies
sudo apt-get install -y \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libxcomposite1 libxdamage1

# Reinstall Playwright browsers
playwright install --with-deps chromium

# Test manually
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('OK')"
```

### Issue: Figma MCP authentication fails
```bash
# Verify token
curl -H "X-Figma-Token: ${FIGMA_ACCESS_TOKEN}" \
  https://api.figma.com/v1/me

# Regenerate token if needed
echo "Visit: https://www.figma.com/developers/api#access-tokens"
```

### Issue: Visual Sovereign not accessible
```bash
# Check if Visual Sovereign exists
ls -la ~/DEV/GoRillah/PARAH

# Clone if missing
mkdir -p ~/DEV/GoRillah
cd ~/DEV/GoRillah
git clone <visual-sovereign-repo-url> PARAH

# Build Visual Sovereign
cd PARAH
go build -o visual_sovereign
```

---

## Resources & Dependencies

### Additional Python Packages
```
selenium>=4.15.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
redis>=5.0.0
zstandard>=0.22.0
pillow>=10.0.0
```

### Additional System Packages
```bash
sudo apt-get install -y \
  chromium-browser \
  redis-server \
  libnss3 \
  libxss1 \
  libasound2
```

### API Keys & Credentials Required
- Figma Personal Access Token
- Amazon Product Advertising API credentials:
  - Access Key
  - Secret Key
  - Partner Tag

### External Resources
- Figma API: https://www.figma.com/developers/api
- Amazon PA API: https://webservices.amazon.com/paapi5/documentation/
- Amazon MCP Server: https://mcpservers.org/servers/r123singh/amazon-mcp-server
- Visual Sovereign: ~/DEV/GoRillah/PARAH

---

## Next Steps

After completing Checkpoint 2, user options:

1. **Continue Building**: Proceed to Phase 3 (C-Rank)
2. **Stop and Save**: Gracefully shut down, preserve state
3. **Stay at This Level**: Work with 7 agents without further deployment

Puckfairy (D1) will prompt and wait for user decision.

**If continuing, proceed to**: [PHASE_3_C_RANK_DEPLOYMENT.md](./PHASE_3_C_RANK_DEPLOYMENT.md)
