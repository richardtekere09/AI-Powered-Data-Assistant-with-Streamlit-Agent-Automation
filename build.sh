#!/bin/bash

# AI Data Assistant Build Script
# Builds Docker image with proper versioning and labels and Quick testing during development

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🏗️  Building AI Data Assistant Docker Image${NC}"
echo "=============================================="

# Get build information
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VERSION=${1:-"latest"}
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo -e "${BLUE}Build Information:${NC}"
echo "📅 Build Date: $BUILD_DATE"
echo "🏷️  Version: $VERSION"
echo "🔗 Git Commit: $GIT_COMMIT"
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found!${NC}"
    exit 1
fi

# Check if .dockerignore exists
if [ ! -f ".dockerignore" ]; then
    echo -e "${YELLOW}⚠️  .dockerignore not found - consider creating one${NC}"
fi

# Build the image
echo -e "${BLUE}🔨 Building Docker image...${NC}"

docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VERSION="$VERSION" \
    --build-arg VCS_REF="$GIT_COMMIT" \
    --tag ai-data-assistant:$VERSION \
    --tag ai-data-assistant:latest \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    
    # Show image information
    echo -e "\n${BLUE}📊 Image Information:${NC}"
    docker images ai-data-assistant:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    # Test the image
    echo -e "\n${BLUE}🧪 Testing image...${NC}"
    if docker run --rm ai-data-assistant:latest python --version; then
        echo -e "${GREEN}✅ Image test passed!${NC}"
    else
        echo -e "${RED}❌ Image test failed!${NC}"
    fi
    
    echo -e "\n${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo "• Test locally: docker-compose up -d"
    echo "• Create package: ./create-friend-package.sh"
    echo "• Push to registry: docker push ai-data-assistant:$VERSION"
    
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi