# Betfair File Parser v1.0.0

A production-ready application for parsing, visualizing, and exporting Betfair historical data files. Built as a core component of **PROJECT CHIMERA** - IntakeHub v3.0.0.

![Ascot Wealth Management](https://img.shields.io/badge/Built%20by-Ascot%20Wealth%20Management-gold)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)

## 🎯 Overview

The Betfair File Parser provides a seamless experience for:

- **Uploading** BZip2-compressed Betfair historical data files
- **Parsing** market odds, event data, and runner information
- **Visualizing** data with proper field labels and hierarchical structure
- **Exporting** to CSV, JSON, or custom formats
- **Batch Processing** multiple files simultaneously

This application follows the "pure open architecture" philosophy with zero mock data and real Betfair API integration.

## ✨ Features

### Core Functionality

✅ **Multi-format Parsing**
- BZip2 decompression
- JSON stream parsing
- Market Odds files
- Event aggregation files

✅ **Comprehensive Data Extraction**
- Market-level metadata (ID, name, status, in-play status)
- Price ladder data (back/lay availability)
- Runner information (name, selection ID, status)
- BSP (Betfair Starting Price) data
- Exchange pricing and traded volumes

✅ **User-Friendly Interface**
- Drag-and-drop file upload
- Real-time parsing feedback
- Expandable market/runner details
- Search and filter capabilities
- Responsive glassmorphic design

✅ **Export Capabilities**
- CSV format with configurable columns
- JSON with full data preservation
- Batch export to ZIP
- Download management

✅ **Production Infrastructure**
- Google Cloud Run deployment
- Cloudflare Pages frontend
- Automatic failover support
- Comprehensive logging and monitoring
- RESTful API design

## 🏗️ Architecture

### Technology Stack

**Frontend**
- React 18.2.0
- Vite build tool
- Tailwind CSS (custom)
- Cloudflare Pages hosting

**Backend**
- Python 3.11+
- FastAPI framework
- betfairlightweight library
- Google Cloud Run

**Infrastructure**
- Docker containerization
- Google Cloud Storage
- Cloudflare Tunnel (geo-bypass)
- Cloud Logging & Monitoring

### Directory Structure

```
betfair-file-parser/
├── betfair_file_parser_backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Container configuration
├── betfair_file_parser_frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── App.css             # Styling with glassmorphic design
│   │   ├── main.jsx            # React entry point
│   │   ├── components/         # Reusable components
│   │   │   ├── Header.jsx
│   │   │   ├── Navigation.jsx
│   │   │   └── Footer.jsx
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── FileViewer.jsx
│   │   │   ├── MarketBrowser.jsx
│   │   │   └── ExportCenter.jsx
│   │   └── styles/             # Page-specific styles
│   ├── index.html              # HTML entry point
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
├── docker-compose.yml          # Local development
├── cloud-run-deploy.yaml       # Google Cloud Run config
├── BETFAIR_FILE_PARSER_SPEC.md # Technical specification
└── README.md                   # This file
```

## 🚀 Quick Start

### Local Development with Docker

**Prerequisites**
- Docker & Docker Compose
- Git

**Setup**

```bash
# Clone the repository
git clone https://github.com/charles-ascot/betfair-file-parser.git
cd betfair-file-parser

# Start services
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8080
# API Docs: http://localhost:8080/docs (Swagger)
```

### Manual Setup

**Backend**

```bash
cd betfair_file_parser_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Frontend**

```bash
cd betfair_file_parser_frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📊 API Documentation

### Health & Status

```bash
GET /health
GET /status
```

### File Operations

**Upload File**
```bash
POST /api/files/upload
Content-Type: multipart/form-data

# Response
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "1.189142695.bz2",
  "status": "completed",
  "size_bytes": 7531
}
```

**Get File Data**
```bash
GET /api/files/{file_id}

# Response - Complete FileParseResponse with markets and runners
```

**List All Files**
```bash
GET /api/files
```

**Delete File**
```bash
DELETE /api/files/{file_id}
```

**Export File**
```bash
POST /api/files/{file_id}/export
Content-Type: application/json

{
  "format": "csv",  # or "json"
  "include_prices": true
}
```

See `BETFAIR_FILE_PARSER_SPEC.md` for complete API documentation.

## 🎨 UI Features

### Dashboard
- File statistics
- Quick start guide
- Recent files list
- API status indicator

### File Upload
- Drag-and-drop zone
- File queue with size display
- Batch upload support
- Progress tracking

### File Viewer
- Hierarchical market/runner display
- Expandable sections for detailed data
- Price ladder visualization
- CSV/JSON export buttons
- File deletion

### Market Browser
- Filter by market type, event, date
- Search functionality
- Quick preview
- Bulk operations

### Export Center
- Format selection (CSV/JSON)
- Bulk export to ZIP
- Download history
- Export scheduling

## 🔧 Configuration

### Environment Variables

**Backend** (`.env` or in Docker)
```
PORT=8080
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_FILE_SIZE=524288000  # 500MB in bytes
PYTHONUNBUFFERED=1
GCS_BUCKET=project-chimera-betfair
```

**Frontend** (`.env.local`)
```
VITE_API_BASE_URL=http://localhost:8080
VITE_APP_ENV=development
```

## 📦 Deployment

### Google Cloud Run

**Build and Push Image**
```bash
# Configure gcloud
gcloud config set project PROJECT_ID

# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/betfair-file-parser:latest \
  --file betfair_file_parser_backend/Dockerfile \
  betfair_file_parser_backend/

# Deploy to Cloud Run
gcloud run deploy betfair-file-parser \
  --image gcr.io/PROJECT_ID/betfair-file-parser:latest \
  --platform managed \
  --region europe-west1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars PORT=8080,ENVIRONMENT=production
```

### Cloudflare Pages (Frontend)

1. Connect GitHub repository to Cloudflare Pages
2. Set build command: `npm run build`
3. Set build output: `betfair_file_parser_frontend/dist`
4. Add environment variable: `VITE_API_BASE_URL=<backend-url>`
5. Deploy

**Custom Domain Setup**
```
# Update DNS to point to Cloudflare
# Add CNAME record: www -> your-app.pages.dev
```

## 🧪 Testing

### API Testing

```bash
# Health check
curl http://localhost:8080/health

# Upload file
curl -X POST -F "file=@test.bz2" \
  http://localhost:8080/api/files/upload

# Get file data
curl http://localhost:8080/api/files/{file_id}

# Export as CSV
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"format":"csv"}' \
  http://localhost:8080/api/files/{file_id}/export \
  > export.csv
```

### Sample Data

Test files available from Betfair:
https://historicdata.betfair.com/#/home

Free and premium historical data available for:
- Horse Racing (WIN, PLACE, EACH_WAY)
- Greyhounds
- Football
- Tennis
- Cricket

## 📈 Performance Metrics

**Targets**
- File upload: < 30 seconds for 100MB
- Parsing: < 500ms for average market
- Export: < 2 seconds for CSV
- API response: < 500ms (p95)
- Uptime: 99.5%

**Monitoring**
- Google Cloud Logging integration
- Request latency tracking
- Error rate monitoring
- File processing statistics

## 🔐 Security

**Data Protection**
- TLS 1.3 for all communication
- Encrypted temp file storage
- Auto-cleanup after 24 hours
- No persistent file storage (default)

**API Security**
- CORS restrictions (configurable)
- Rate limiting: 100 req/min per IP
- Input validation on all endpoints
- XSS and SQL injection prevention

**Authentication** (Roadmap)
- API key validation
- JWT token support
- Multi-user authentication
- Role-based access control

## 🛣️ Roadmap

### Phase 1 ✅ Complete
- Core file parsing
- Basic visualization
- CSV/JSON export
- Docker deployment

### Phase 2 🔄 In Progress
- MarketBrowser enhancement
- Batch operations
- Cloud Storage integration
- Performance optimization

### Phase 3 📅 Planned
- Real-time streaming
- ML-based insights
- Advanced filtering
- PostgreSQL persistence
- Multi-user authentication
- Data warehouse integration

## 📚 Documentation

- **Technical Specification**: `BETFAIR_FILE_PARSER_SPEC.md`
- **API Documentation**: Available at `/docs` (Swagger UI)
- **Development Guide**: See this README
- **Architecture Decisions**: See specification document

## 🤝 Contributing

This project is part of PROJECT CHIMERA. For contributions:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests to main branch

## 📝 License

Copyright © 2026 Ascot Wealth Management. All rights reserved.

## 🆘 Support & Troubleshooting

### Common Issues

**File Upload Fails**
- Verify file is BZip2 format (.bz2 extension)
- Check file size < 500MB
- Ensure API is accessible

**Parser Errors**
- Check Betfair file format compatibility
- Review error logs: `curl http://localhost:8080/health`
- Validate BZip2 header (BZ magic bytes)

**API Connection Issues**
- Verify backend is running
- Check CORS settings for frontend URL
- Test with curl: `curl http://localhost:8080/health`

### Getting Help

- Check the technical specification document
- Review API error responses for details
- Check logs: Docker logs or Google Cloud Logging

## 📞 Contact

**Development Team**: Ascot Wealth Management  
**Project Lead**: Mark Insley (UK-based)  
**Technical Lead**: Sam (South Africa-based)

---

**Version**: 1.0.0  
**Last Updated**: January 3, 2026  
**Status**: Production Ready

For detailed technical information, see `BETFAIR_FILE_PARSER_SPEC.md`
