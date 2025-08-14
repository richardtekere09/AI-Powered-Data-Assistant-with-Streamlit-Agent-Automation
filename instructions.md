# 🚀 AI Data Assistant - Complete Setup Guide

Welcome to AI Data Assistant! This guide will help you set up and test the application quickly and easily.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Docker Desktop** installed and running
- **GROQ API Key** (free at https://console.groq.com/)
- **8GB+ RAM** recommended for optimal performance
- **2GB disk space** for the application

### Installing Docker (if needed)

- **Windows/Mac**: Download Docker Desktop from https://www.docker.com/products/docker-desktop/
- **Linux**: Install Docker Engine and Docker Compose from your package manager

## ⚡ Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
# 1. Extract the package and navigate to the folder
unzip ai-data-assistant-package-*.zip
cd ai-data-assistant-package

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Follow the prompts to configure your API key
# 4. Open your browser to http://localhost:8501
```

### Option 2: Manual Setup

```bash
# 1. Create environment file
cp .env.template .env

# 2. Edit .env file with your GROQ API key
nano .env  # or use your preferred editor

# 3. Load Docker image
gunzip -c ai-data-assistant-image.tar.gz | docker load

# 4. Start services
docker-compose up -d

# 5. Open http://localhost:8501 in your browser
```

## 🔑 Login Credentials

The application comes with pre-configured test accounts:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Administrator | Full access to all features |
| `testuser` | `test123` | Test Account | Basic user for testing |

## ⚙️ Configuration

### Required: GROQ API Key

1. **Get API Key**: Visit https://console.groq.com/
2. **Create Account**: Sign up for a free account
3. **Generate Key**: Go to API Keys section and create a new key
4. **Configure**: Edit `.env` file and replace `your_groq_api_key_here` with your actual key

```bash
# Example .env configuration
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### Optional: Email Configuration

For password reset functionality, configure Gmail SMTP:

```bash
# In .env file
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
FROM_EMAIL=your_email@gmail.com
```

**Note**: Use Gmail App Passwords, not your regular password. Enable 2FA first, then generate an app password.

## 🧪 Testing the Application

### Step 1: Login and Navigation
1. Open http://localhost:8501
2. Login with `admin` / `admin123`
3. Explore the dashboard and sidebar options

### Step 2: Upload Data
1. Click the file uploader in the sidebar
2. Upload a CSV or Excel file (sample data recommended for first test)
3. Verify data loads correctly in the preview

### Step 3: Basic Analysis
- **Data Overview**: Check dataset statistics and preview
- **Quick Questions**: Try asking "Show me the first 10 rows"
- **Column Info**: Ask "What are the column names and data types?"

### Step 4: Advanced Features
- **EDA Report**: Click "Generate EDA Report" button
- **Visualizations**: Try "Quick Visualizations" 
- **AI Analysis**: Ask complex questions like "Find correlations in my data"

### Step 5: Natural Language Queries

Try these example questions:
```
"Create a histogram of the sales column"
"Show me statistics for all numeric columns"
"What are the missing values in my dataset?"
"Plot revenue by month"
"Find outliers in the price data"
"Generate a correlation matrix"
```

## 🛠️ Management Commands

### Service Management
```bash
# View running services
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View app-only logs
docker-compose logs -f app

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove all data (complete reset)
docker-compose down -v
```

### Update Configuration
```bash
# After editing .env file
docker-compose restart app

# Force rebuild (if needed)
docker-compose up -d --force-recreate app
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port 8501 Already in Use
```bash
# Change port in docker-compose.yml
# Replace "8501:8501" with "8502:8501"
# Then access via http://localhost:8502
```

#### 2. Application Won't Start
```bash
# Check application logs
docker-compose logs app

# Common causes:
# - Missing GROQ API key
# - Database connection issues
# - Port conflicts
```

#### 3. Database Connection Error
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

#### 4. Docker Image Loading Issues
```bash
# Verify image file integrity
ls -la ai-data-assistant-image.tar.gz

# Try manual loading
gunzip -c ai-data-assistant-image.tar.gz | docker load

# Check loaded images
docker images | grep ai-data-assistant
```

#### 5. Permission Issues (Linux)
```bash
# Fix permissions
sudo chmod +x setup.sh
sudo chown -R $USER:$USER .

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Performance Issues

#### High Memory Usage
- **Reduce dataset size**: Use sample of large datasets
- **Increase Docker memory**: In Docker Desktop settings
- **Close other applications**: Free up system resources

#### Slow Analysis
- **Check GROQ API limits**: Free tier has rate limits
- **Simplify queries**: Break complex questions into smaller parts

## 📈 Features Overview

### 🔍 Data Analysis Capabilities
- **Statistical Analysis**: Comprehensive summaries, correlations, distributions
- **Missing Value Analysis**: Detection and handling recommendations
- **Outlier Detection**: Identify anomalies in your data
- **Data Quality Assessment**: Automated data profiling

### 📊 Visualization Features
- **Interactive Charts**: Histograms, scatter plots, box plots, heatmaps
- **Custom Dashboards**: Create personalized data views
- **Correlation Matrices**: Understand variable relationships
- **Trend Analysis**: Time series and pattern recognition

### 🤖 AI-Powered Features
- **Natural Language Queries**: Ask questions in plain English
- **Automated Insights**: AI-generated observations and recommendations
- **Smart Suggestions**: Context-aware analysis recommendations
- **Code Generation**: Automatic Python code for complex analysis

### 📋 Report Generation
- **Automated EDA**: One-click exploratory data analysis
- **HTML Reports**: Professional, shareable analysis reports
- **Export Options**: Download reports and visualizations
- **Summary Statistics**: Key metrics and insights

## 🛡️ Security & Privacy

- **Local Processing**: All data analysis happens on your machine
- **No Data Upload**: Your data never leaves your environment
- **Secure Authentication**: Encrypted password storage
- **API Key Safety**: Credentials stored locally only

## 📞 Support & Feedback



## 🎯 Test Scenarios

### Scenario 1: Sales Data Analysis
1. Upload sales data with columns: Date, Product, Region, Sales, Price
2. Ask: "What are the top 5 products by sales?"
3. Generate visualization: "Create a sales trend by month"
4. Run EDA report for comprehensive analysis

### Scenario 2: Survey Data Processing
1. Upload survey data with ratings and categories
2. Ask: "Show me the distribution of ratings"
3. Analyze: "Find correlations between different survey questions"
4. Generate summary statistics

### Scenario 3: Financial Data Review
1. Upload financial data with metrics over time
2. Ask: "Identify outliers in the revenue data"
3. Visualize: "Plot revenue vs expenses over time"
4. Generate insights on trends and anomalies

## 🚀 Next Steps

After successful setup and testing:

1. **Explore Advanced Features**: Try complex analysis queries
2. **Test with Real Data**: Upload your actual datasets
3. **Generate Reports**: Create professional analysis reports
4. **Share Results**: Export visualizations and insights
5. **Provide Feedback**: Help improve the application

---

## 📝 Quick Reference

### Essential Commands
```bash
# Start everything
./setup.sh

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Reset everything
docker-compose down -v
./setup.sh
```

### Key URLs
- **Application**: http://localhost:8501
- **GROQ Console**: https://console.groq.com/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/

### Default Credentials
- **admin** / admin123
- **testuser** / test123

---
