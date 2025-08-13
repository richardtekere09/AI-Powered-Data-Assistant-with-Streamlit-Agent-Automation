#!/bin/bash

# AI Data Assistant - One-Click Setup Script
# This script sets up and runs the AI Data Assistant for testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ERROR="❌"
INFO="ℹ️"
PACKAGE="📦"
GLOBE="🌐"
USER="👤"
STOP="🛑"

echo -e "${BLUE}${ROCKET} AI Data Assistant - One-Click Setup${NC}"
echo "================================================="

# Function to print colored output
print_success() { echo -e "${GREEN}${CHECK} $1${NC}"; }
print_warning() { echo -e "${YELLOW}${WARNING} $1${NC}"; }
print_error() { echo -e "${RED}${ERROR} $1${NC}"; }
print_info() { echo -e "${CYAN}${INFO} $1${NC}"; }

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for services
wait_for_services() {
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "Up"; then
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo ""
    return 1
}

# Check prerequisites
echo -e "\n${CYAN}🔍 Checking prerequisites...${NC}"

if ! command_exists docker; then
    print_error "Docker is not installed or not in PATH"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    echo "Please start Docker Desktop or Docker daemon and try again"
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Check for required files
echo -e "\n${CYAN}📋 Checking required files...${NC}"

required_files=("ai-data-assistant-image.tar.gz" "docker-compose.yml" "init.sql" ".env.template")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found $file"
    else
        print_error "Missing $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    print_error "Missing required files. Please ensure you have the complete package."
    exit 1
fi

# Handle environment configuration
echo -e "\n${CYAN}⚙️ Setting up environment configuration...${NC}"

if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp .env.template .env
    print_success ".env file created"
    
    echo -e "\n${YELLOW}${WARNING} IMPORTANT: You need to configure your API keys!${NC}"
    echo -e "${CYAN}Required steps:${NC}"
    echo "1. Get GROQ API key from: https://console.groq.com/"
    echo "2. Edit .env file and replace 'your_groq_api_key_here' with your actual key"
    echo "3. (Optional) Configure email settings for password reset functionality"
    
    echo -e "\n${CYAN}Would you like to:${NC}"
    echo "a) Open .env file now for editing"
    echo "b) Continue with setup (you can edit later)"
    echo "c) Exit to configure manually"
    
    read -p "Choose option (a/b/c): " env_choice
    
    case $env_choice in
        a|A)
            if command_exists nano; then
                nano .env
            elif command_exists vim; then
                vim .env
            elif command_exists code; then
                code .env
            else
                print_info "Please edit .env file with your preferred editor"
                read -p "Press Enter when you're done editing..."
            fi
            ;;
        c|C)
            print_info "Please edit .env file and run this script again"
            exit 0
            ;;
        b|B|*)
            print_warning "Continuing with template values - update .env later if needed"
            ;;
    esac
else
    print_success ".env file already exists"
fi

# Load Docker image
echo -e "\n${CYAN}${PACKAGE} Loading AI Data Assistant Docker image...${NC}"

if [ -f "ai-data-assistant-image.tar.gz" ]; then
    print_info "Loading compressed Docker image (this may take a few minutes)..."
    
    # Show progress while loading
    gunzip -c ai-data-assistant-image.tar.gz | docker load
    
    if [ $? -eq 0 ]; then
        print_success "Docker image loaded successfully"
    else
        print_error "Failed to load Docker image"
        exit 1
    fi
else
    print_error "Docker image file 'ai-data-assistant-image.tar.gz' not found"
    exit 1
fi

# Stop any existing services
echo -e "\n${CYAN}🧹 Cleaning up any existing services...${NC}"
docker-compose down > /dev/null 2>&1 || true
print_success "Cleaned up existing services"

# Start services
echo -e "\n${CYAN}${ROCKET} Starting AI Data Assistant services...${NC}"

print_info "Starting PostgreSQL database..."
docker-compose up -d postgres

print_info "Starting Redis cache..."
docker-compose up -d redis

print_info "Starting AI Data Assistant application..."
docker-compose up -d app

# Wait for services to be ready
if wait_for_services; then
    print_success "All services are running!"
else
    print_error "Services failed to start properly"
    echo -e "\n${CYAN}Checking service status:${NC}"
    docker-compose ps
    
    echo -e "\n${CYAN}Recent logs:${NC}"
    docker-compose logs --tail=20
    
    print_error "Setup failed. Check the logs above for details."
    exit 1
fi

# Verify services
echo -e "\n${CYAN}🔍 Verifying service health...${NC}"

# Check if app is responding
sleep 5  # Give app a moment to fully start

if curl -s http://localhost:8501 > /dev/null 2>&1; then
    print_success "Application is responding on port 8501"
elif curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    print_success "Application health check passed"
else
    print_warning "Application may still be starting up..."
fi

# Success message
echo -e "\n${GREEN}🎉 AI Data Assistant Setup Complete!${NC}"
echo "================================================="

echo -e "\n${CYAN}${GLOBE} Access Information:${NC}"
echo "🌐 Open your web browser and go to: http://localhost:8501"
echo ""

echo -e "${CYAN}${USER} Login Credentials:${NC}"
echo "📋 You can login with any of these accounts:"
echo "   • Username: admin     | Password: admin123     (Administrator)"
echo "   • Username: richard   | Password: richard09    (Power User)"  
echo "   • Username: testuser  | Password: test123      (Test Account)"
echo ""


echo -e "${CYAN} Management Commands:${NC}"
echo "• View running services: docker-compose ps"
echo "• View logs: docker-compose logs -f"
echo "• Restart services: docker-compose restart"
echo "• Stop services: docker-compose down"
echo "• Reset everything: docker-compose down -v"
echo ""

echo -e "${CYAN} Configuration:${NC}"
echo "• Environment file: .env (edit to customize settings)"
echo "• GROQ API key: Required for AI analysis features"
echo "• Email settings: Optional, for password reset functionality"
echo ""

# Check if GROQ API key looks configured
if grep -q "your_groq_api_key_here" .env 2>/dev/null; then
    echo -e "${YELLOW}${WARNING} Remember to configure your GROQ API key in .env file!${NC}"
    echo "   Get your key from: https://console.groq.com/"
    echo "   Edit .env file and restart: docker-compose restart app"
fi

echo -e "${CYAN} Troubleshooting:${NC}"
echo "• Port 8501 in use: Change '8501:8501' to '8502:8501' in docker-compose.yml"
echo "• App won't start: Check logs with 'docker-compose logs app'"
echo "• Database issues: Reset with 'docker-compose down -v'"
echo "• Permission issues: Make sure Docker has proper permissions"
echo ""

echo -e "${GREEN}Ready to explore your data with AI! Happy analyzing!${NC}"

# Optionally open browser (commented out by default)
if command_exists open; then
    open http://localhost:8501
elif command_exists xdg-open; then
    xdg-open http://localhost:8501
fi