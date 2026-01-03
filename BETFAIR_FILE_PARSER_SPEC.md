# Betfair File Parser v1.0 - Technical Specification

**Project**: PROJECT CHIMERA - IntakeHub v3.0.0 Integration Module  
**Date**: January 2026  
**Status**: Strategic Planning & Implementation

---

## Executive Summary

The Betfair File Parser is a standalone, production-ready application designed to parse, visualize, and export Betfair historical data files. It serves as a critical component of the IntakeHub data ingestion pipeline, enabling reliable parsing of multiple Betfair data formats (Market Odds, Event Files, etc.) with proper field mapping and data integrity validation.

The application follows the "pure open architecture" philosophy with zero mock data tolerance and comprehensive error handling.

---

## 1. System Architecture

### 1.1 Technology Stack

**Frontend**
- React (JavaScript, not TypeScript) 
- Tailwind CSS for styling
- Modern glassmorphic UI with Ascot Wealth Management branding
- Deployed on Cloudflare Pages

**Backend**
- Python 3.11+
- FastAPI framework
- Cloud Run deployment (Google Cloud Platform)
- Docker containerization

**Data Processing**
- betfairlightweight (official Betfair library)
- BZip2 decompression for historical data files
- JSON serialization for API responses
- PostgreSQL for future data persistence

**Infrastructure**
- Google Cloud Run (backend API)
- Cloudflare Pages (frontend hosting)
- Cloudflare Tunnel (for geo-restriction bypass when needed)
- Docker Registry (image storage)

### 1.2 Supported File Formats

1. **BZip2 Compressed Files** (.bz2)
   - Market Odds files (single market data)
   - Event files (all markets within an event)
   - Native compression format from Betfair

2. **Data Types**
   - Betfair historical market data
   - Runner information with odds
   - Market definition and metadata
   - In-play status and timestamps

---

## 2. Core Functional Requirements

### 2.1 File Selection & Upload

**Requirements**
- Multi-file selection from local filesystem
- Support for batch upload of 1-100 files
- File size validation (max 500MB per file)
- Real-time upload progress tracking
- Drag-and-drop file upload interface
- File validation before processing

**Processing Pipeline**
```
User Selection → Validation → Upload → Queue → Processing → Storage
```

### 2.2 File Parsing & Data Extraction

**Core Data Elements to Extract**

**Market-Level Data:**
- Market ID
- Market Name
- Market Type
- Event ID
- Event Name
- Competition/Race details
- Market Status (OPEN, SUSPENDED, CLOSED, etc.)
- In-Play Status
- Total Matched
- Total Available
- Market Definition
- BSP (Starting Price) data
- Publication Time
- Last Match Time

**Runner-Level Data:**
- Selection ID
- Runner Name
- BSP (Back/Lay prices)
- Exchange (EX) data:
  - Available to Back prices
  - Available to Lay prices
  - Traded Volume
- Runner Status (ACTIVE, LOSER, WINNER, PLACED)
- Adjustment Factor (for dead heats)
- SP Near/Far prices
- Status details

**Price Ladder Data:**
- Back odds available (with stake volumes)
- Lay odds available (with liability volumes)
- Traded volume at each price point

### 2.3 Data Visualization

**Display Options**

**Option 1: Detailed View (Single File)**
- Hierarchical data structure
- Market header with key metadata
- Runner list with individual selection details
- Expandable sections for pricing data
- Timestamp and version information
- Proper field labeling with descriptions

**Option 2: Summary View (Multiple Files)**
- File listing with metadata
- Quick statistics per file
- Processing status indicators
- Aggregated statistics

**Option 3: Market Browser**
- Search/filter by market name, type, country
- Event grouping
- Date range filtering
- Quick preview of market contents

### 2.4 Export Functionality

**Export Formats**

**CSV Export**
- Single market export with all runners
- Flattened structure for Excel compatibility
- Configurable column selection
- Standardized headers matching Betfair documentation

**JSON Export**
- Full data structure preservation
- Pretty-printed for readability
- Metadata included
- Validated schema

**Bulk Export**
- Multiple files to ZIP archive
- Format selection (CSV, JSON, or both)
- Compression optimization
- Progress tracking

### 2.5 Data Quality & Validation

**Validation Rules**
- File format validation (BZip2 header check)
- Betfair data schema validation
- Mandatory field presence check
- Data type validation
- Timestamp validity
- Numeric range validation

**Error Handling**
- Graceful degradation
- User-friendly error messages
- Detailed error logging
- Recovery suggestions

---

## 3. Backend API Specification

### 3.1 API Endpoints

**Health & Status**
```
GET /health
GET /status
```

**File Operations**
```
POST /api/files/upload
  - Multipart form data
  - Returns: {file_id, status, file_name, size}

GET /api/files/{file_id}
  - Returns: file metadata and processing status

GET /api/files/{file_id}/data
  - Returns: parsed market data

POST /api/files/{file_id}/export
  - Body: {format: 'csv'|'json', options: {...}}
  - Returns: download URL

DELETE /api/files/{file_id}
  - Cleanup and removal
```

**Batch Operations**
```
POST /api/batch/upload
  - Multiple files
  - Returns: batch_id, file_list

POST /api/batch/{batch_id}/export
  - Bulk export all files
  - Returns: download URL for ZIP
```

### 3.2 Data Models

**File Metadata**
```python
{
    file_id: str (UUID)
    file_name: str
    size_bytes: int
    upload_time: datetime
    processing_status: str ('pending'|'processing'|'completed'|'error')
    error_message: str (optional)
    parsed_data: dict (when completed)
}
```

**Market Data**
```python
{
    market_id: str
    market_name: str
    market_type: str
    event_id: str
    event_name: str
    event_date: datetime
    country_code: str (optional)
    market_status: str
    inplay: bool
    total_matched: float
    total_available: float
    number_of_runners: int
    number_of_winners: int
    publish_time: datetime
    version: int
    
    runners: [
        {
            selection_id: int
            runner_name: str
            status: str
            bsp: {
                near_price: float
                far_price: float
                actual_sp: float
                back_stake_taken: [(price, stake)]
                lay_liability_taken: [(price, liability)]
            }
            ex: {
                available_to_back: [(price, stake)]
                available_to_lay: [(price, liability)]
                traded_volume: [(price, volume)]
            }
            last_price_traded: float (optional)
            adjustment_factor: float (optional)
        }
    ]
}
```

### 3.3 Error Responses

```python
{
    error: str
    error_code: str
    details: dict (optional)
    timestamp: datetime
}
```

---

## 4. Frontend Specification

### 4.1 Page Structure

**Layout Components**
- Header with Ascot Wealth Management branding
- Navigation sidebar
- Main content area
- Footer with version/status

**Pages**

**1. Dashboard**
- Quick stats (files uploaded, last 10 files)
- Recent activities
- Quick action buttons
- Status indicators

**2. File Upload**
- Drag-and-drop zone
- File browser button
- Upload progress bars
- File queue display
- Validation feedback

**3. File Viewer**
- File list with sorting/filtering
- File details panel
- Data preview
- Export options
- Delete confirmation

**4. Market Data Browser**
- Interactive market selection
- Runner list with pricing
- Price ladder visualization
- Search and filter controls
- Export from viewer

**5. Export Center**
- Export history
- Format selection
- Batch export interface
- Download management

### 4.2 UI Components

**Reusable Components**
- FileUploadZone
- FileList
- MarketViewer
- RunnerDetails
- PriceLadder
- DataTable
- ExportDialog
- StatusIndicator
- ErrorAlert

### 4.3 Styling Guide

**Color Scheme**
- Primary: Ascot gold/royal blue
- Secondary: Regal purples/deep teals
- Accent: Emerald green (success), Ruby red (errors)
- Glassmorphic effects with transparency layers

**Typography**
- Headings: Elegant serif for titles
- Body: Clean sans-serif for readability
- Monospace: Code/data display

---

## 5. Data Processing Pipeline

### 5.1 File Ingestion

```
1. Receive uploaded file
2. Validate file format (BZip2 magic bytes)
3. Check file integrity
4. Decompress to memory or temp storage
5. Parse JSON stream
6. Validate Betfair schema
7. Extract market data
8. Store in memory cache
9. Return success/error response
```

### 5.2 Parser Implementation

**BZip2 Decompression**
```python
import bz2
with bz2.BZ2File(file_path, 'rb') as f:
    decompressed_data = f.read()
```

**Data Stream Processing**
- Line-by-line JSON parsing
- Betfairlightweight resource instantiation
- Error recovery and logging
- Data validation

**Resource Mapping**
- Stream data → betfairlightweight objects
- Object serialization → API response format
- Field name normalization

### 5.3 Output Serialization

**JSON Output**
```python
{
    file_metadata: {...},
    markets: [
        {
            market_id: str,
            market_name: str,
            # ... full market data structure
        }
    ],
    processing_stats: {
        total_records: int,
        total_runners: int,
        processing_time_ms: int,
        compressed_size_bytes: int,
        decompressed_size_bytes: int
    }
}
```

---

## 6. Deployment Architecture

### 6.1 Docker Configuration

**Backend Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Image Registry**
- Google Container Registry (GCR)
- Automated builds on GitHub push
- Version tagging strategy

### 6.2 Cloud Run Deployment

**Configuration**
- Memory: 2GB minimum (for large file processing)
- Timeout: 3600 seconds (1 hour for large files)
- Concurrent requests: 100
- CPU: 2 vCPUs
- Autoscaling: 1-10 instances

**Environment Variables**
```
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=524288000 (500MB)
TEMP_STORAGE_PATH=/tmp
GCS_BUCKET=PROJECT_CHIMERA-betfair-files
```

### 6.3 Cloudflare Pages Deployment

**Configuration**
- Framework: React
- Build command: `npm run build`
- Build output directory: `dist`
- Environment: Production
- Caching: 30 days for static assets

**Environment Variables**
```
VITE_API_BASE_URL=https://backend-api.domain.com
VITE_APP_ENV=production
```

---

## 7. Security & Compliance

### 7.1 Data Security

**In Transit**
- TLS 1.3 for all API communication
- Certificate pinning for API endpoints
- CORS restrictions to known domains

**At Rest**
- Temporary files encrypted with AES-256
- No persistent storage of raw file contents
- Auto-cleanup of temp files after 24 hours

**Authentication**
- API key validation for endpoints (optional for MVP)
- CSRF protection on forms
- Rate limiting: 100 requests/minute per IP

### 7.2 Data Privacy

**User Data**
- No personal user data collected
- Anonymized error logs
- GDPR compliance for EU users
- Data retention policy: 30 days for temporary files

### 7.3 Input Validation

**File Validation**
- Magic byte checking for BZip2
- Size limits enforcement
- Content-type validation
- Malicious payload detection

**API Input**
- Schema validation on all requests
- SQL injection prevention
- XSS protection
- Rate limiting

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Backend Tests**
- Parser functionality with sample BZip2 files
- API endpoint responses
- Error handling scenarios
- Data validation rules

**Frontend Tests**
- Component rendering
- User interactions
- File upload flow
- Export functionality

### 8.2 Integration Tests

**End-to-End Flow**
- File upload → parsing → visualization → export
- Batch operations
- Error recovery
- Edge cases (empty files, corrupted data)

### 8.3 Test Data

**Sample Files**
- Various market types (WIN, PLACE, ASIAN HANDICAP)
- Different sports (Horse Racing, Greyhounds)
- Various file sizes (1KB to 100MB)
- Edge cases and corrupted data

---

## 9. Monitoring & Logging

### 9.1 Metrics

**Application Metrics**
- File upload success rate
- Average parsing time
- Export count and formats
- Error rates by type
- API response times

**Infrastructure Metrics**
- CPU/Memory utilization
- Request latency
- Error rate (5xx)
- Concurrent user count

### 9.2 Logging

**Log Levels**
- ERROR: Failures, exceptions, validation errors
- WARN: Retry attempts, deprecated features
- INFO: File uploads, exports, key operations
- DEBUG: Detailed processing steps, data values

**Log Aggregation**
- Google Cloud Logging
- Structured JSON format
- Searchable and filterable
- 30-day retention

### 9.3 Alerting

**Alert Triggers**
- Error rate > 5%
- Response time > 5 seconds
- File processing failure
- API downtime
- Storage quota exceeded

---

## 10. Future Enhancements

### Phase 2 Features
- Real-time market data streaming
- Machine learning insights on pricing patterns
- Advanced filtering and search
- Historical data trending
- Automated data quality reports
- Integration with Google Cloud Storage for persistence
- PostgreSQL database for queryable data
- Multi-user authentication
- Data warehouse integration

### Phase 3 Features
- AI agent for intelligent data analysis
- Predictive pricing models
- Anomaly detection
- Comparative market analysis
- API for programmatic access

---

## 11. Success Metrics

**Functional Metrics**
- Parse 99%+ of Betfair file formats correctly
- Export functionality available for all data types
- User interface intuitive (< 5 clicks to export)
- Zero data loss in processing pipeline

**Performance Metrics**
- File upload: < 30 seconds for 100MB
- Parsing: < 500ms for average market file
- Export generation: < 2 seconds for CSV
- API response time: < 500ms (p95)

**Reliability Metrics**
- 99.5% uptime target
- Error rate < 0.5%
- Automatic recovery from transient failures
- Data validation pass rate > 99.9%

---

## 12. Implementation Timeline

**Week 1: Foundation**
- Backend API structure
- Core parser implementation
- Basic error handling

**Week 2: Frontend & Integration**
- React frontend setup
- File upload component
- Data viewer component

**Week 3: Polish & Deployment**
- UI refinement and styling
- Cloud Run deployment
- Cloudflare Pages deployment
- Testing and QA

**Week 4: Documentation & Launch**
- API documentation
- User guide
- Monitoring setup
- Production launch

---

## Appendix A: Betfair Data Field Reference

### Market Fields
```
marketId        - Unique market identifier (ISO format)
marketName      - Human-readable market name
marketType      - Type of market (WIN, PLACE, etc.)
status          - Market status (OPEN, SUSPENDED, CLOSED)
inplay          - Boolean, market in-play flag
totalMatched    - Total amount matched (GBP)
totalAvailable  - Total available liquidity
numberOfRunners - Count of active runners
numberOfWinners - Expected number of winners
```

### Runner Fields
```
selectionId     - Unique runner identifier (integer)
runnerName      - Horse/Dog name
status          - Runner status (ACTIVE, WINNER, LOSER)
bsp.nearPrice   - BSP near price (Betfair Starting Price)
bsp.farPrice    - BSP far price
ex.availableToBack   - List of [price, stake] available
ex.availableToLay    - List of [price, liability] available
ex.tradedVolume      - List of [price, volume] traded
```

### Timestamp Formats
- All timestamps in milliseconds since epoch
- UTC timezone
- Serialized as ISO 8601 strings in JSON

---

## Appendix B: Example Response Structure

```json
{
  "file_metadata": {
    "file_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "1.189142695.bz2",
    "size_bytes": 7531,
    "upload_time": "2026-01-03T12:00:00Z",
    "processing_status": "completed",
    "processed_at": "2026-01-03T12:00:05Z"
  },
  "markets": [
    {
      "market_id": "1.189142695",
      "market_name": "Chennai Super Kings v Kolkata Knight Riders - Match Odds",
      "market_type": "WIN",
      "event_id": "31002968",
      "event_name": "Chennai Super Kings v Kolkata Knight Riders",
      "event_date": "2021-10-15T19:30:00Z",
      "market_status": "CLOSED",
      "inplay": false,
      "total_matched": 1234567.89,
      "total_available": 456789.01,
      "number_of_runners": 2,
      "number_of_winners": 1,
      "publish_time": "2021-10-15T19:42:30Z",
      "version": 4294967296,
      "runners": [
        {
          "selection_id": 2954263,
          "runner_name": "Chennai Super Kings",
          "status": "WINNER",
          "bsp": {
            "near_price": 1.95,
            "far_price": 2.05,
            "actual_sp": 2.00,
            "back_stake_taken": [[1.95, 100000]],
            "lay_liability_taken": [[2.05, 50000]]
          },
          "ex": {
            "available_to_back": [[2.00, 50000], [1.98, 100000]],
            "available_to_lay": [[2.02, 50000]],
            "traded_volume": [[1.95, 500000], [2.00, 300000], [2.05, 200000]]
          },
          "last_price_traded": 2.00,
          "adjustment_factor": 1.0
        },
        {
          "selection_id": 2954260,
          "runner_name": "Kolkata Knight Riders",
          "status": "LOSER",
          "bsp": {
            "near_price": 1.95,
            "far_price": 2.05,
            "actual_sp": 2.00,
            "back_stake_taken": [[1.95, 50000]],
            "lay_liability_taken": [[2.05, 100000]]
          },
          "ex": {
            "available_to_back": [[2.06, 30000]],
            "available_to_lay": [[2.00, 80000], [2.02, 50000]],
            "traded_volume": [[2.00, 200000], [2.02, 150000], [2.05, 100000]]
          },
          "last_price_traded": 2.00,
          "adjustment_factor": 1.0
        }
      ]
    }
  ],
  "processing_stats": {
    "total_records": 1,
    "total_runners": 2,
    "processing_time_ms": 150,
    "compressed_size_bytes": 7531,
    "decompressed_size_bytes": 45000
  }
}
```

---

**Document Version**: 1.0  
**Last Updated**: January 3, 2026  
**Next Review**: Upon completion of Week 1 implementation
