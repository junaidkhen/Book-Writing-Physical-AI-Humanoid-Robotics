#!/bin/bash
# Test script to verify production build

echo "Testing production build..."

# Navigate to docs directory
cd docs

# Build the project
echo "Building production version..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
else
    echo "✅ Build successful"
fi

# Test serving the production build locally
echo "Starting local server for production build..."
npx serve -s build &

# Wait a moment for the server to start
sleep 3

# Check if the server is running
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Production build is accessible at http://localhost:3000"
    echo "✅ Local production test PASSED"
else
    echo "❌ Could not access production build locally"
    pkill -f "serve" 2>/dev/null
    exit 1
fi

# Kill the serve process
pkill -f "serve" 2>/dev/null

echo "All tests passed! Production build is working correctly."