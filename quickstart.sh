#!/bin/bash

################################################################################
# Edge LLM System - Automated Quick Start Script
# This script automatically sets up everything you need to get started
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Emojis
CHECK="✓"
CROSS="✗"
ARROW="→"
ROCKET="🚀"
PACKAGE="📦"
WRENCH="🔧"
COMPUTER="💻"
PHONE="📱"
GLOBE="🌐"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BOLD}${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║  ${ROCKET} Edge LLM System - Quick Start Setup           ║${NC}"
    echo -e "${BOLD}${BLUE}║  Automated deployment for edge/mobile AI                  ║${NC}"
    echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

log_info() {
    echo -e "${BLUE}${ARROW}${NC} $1"
}

log_success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

log_error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

ask_yes_no() {
    while true; do
        read -p "$(echo -e ${CYAN}$1 [y/n]: ${NC})" yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

################################################################################
# System Checks
################################################################################

check_python() {
    print_section "1️⃣  Checking Python Installation"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python found: $PYTHON_VERSION"
        
        # Check version
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            log_success "Python version is compatible (3.9+)"
            return 0
        else
            log_error "Python 3.9+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        log_error "Python 3 not found"
        echo -e "\n${YELLOW}Please install Python 3.9+ from:${NC}"
        echo "  - macOS: brew install python3"
        echo "  - Ubuntu: sudo apt install python3 python3-pip"
        echo "  - Windows: https://python.org/downloads/"
        return 1
    fi
}

check_disk_space() {
    print_section "2️⃣  Checking Disk Space"
    
    AVAILABLE_GB=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    
    if [ $(echo "$AVAILABLE_GB > 10" | bc) -eq 1 ]; then
        log_success "Sufficient disk space: ${AVAILABLE_GB}GB available"
        return 0
    else
        log_warning "Low disk space: ${AVAILABLE_GB}GB available (10GB+ recommended)"
        if ask_yes_no "Continue anyway?"; then
            return 0
        else
            return 1
        fi
    fi
}

check_internet() {
    print_section "3️⃣  Checking Internet Connection"
    
    if ping -c 1 google.com &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "Internet connection verified"
        return 0
    else
        log_error "No internet connection detected"
        log_warning "Internet required for model downloads"
        return 1
    fi
}

################################################################################
# Platform Selection
################################################################################

select_platform() {
    print_section "4️⃣  Platform Selection"
    
    echo -e "${BOLD}Select your target platform:${NC}\n"
    echo "  1) ${COMPUTER} Desktop/Testing (Mac, Linux, Windows)"
    echo "  2) ${PHONE} iOS (iPhone, iPad)"
    echo "  3) ${PHONE} Android"
    echo "  4) ${GLOBE} Web/Browser"
    echo "  5) ${PACKAGE} All platforms"
    echo ""
    
    while true; do
        read -p "$(echo -e ${CYAN}Enter choice [1-5]: ${NC})" choice
        case $choice in
            1) PLATFORM="desktop"; break;;
            2) PLATFORM="ios"; break;;
            3) PLATFORM="android"; break;;
            4) PLATFORM="web"; break;;
            5) PLATFORM="all"; break;;
            *) echo "Invalid choice. Please enter 1-5.";;
        esac
    done
    
    log_success "Selected platform: $PLATFORM"
}

################################################################################
# Environment Setup
################################################################################

setup_virtualenv() {
    print_section "5️⃣  Setting Up Python Environment"
    
    if [ -d "venv" ]; then
        log_warning "Virtual environment already exists"
        if ask_yes_no "Recreate it?"; then
            rm -rf venv
        else
            log_info "Using existing virtual environment"
            source venv/bin/activate
            return 0
        fi
    fi
    
    log_info "Creating virtual environment..."
    python3 -m venv venv
    
    log_info "Activating virtual environment..."
    source venv/bin/activate
    
    log_success "Virtual environment ready"
}

install_dependencies() {
    print_section "6️⃣  Installing Dependencies"
    
    log_info "Upgrading pip..."
    pip install --upgrade pip --quiet
    
    log_info "Installing Python packages (this may take 5-10 minutes)..."
    
    # Install dependencies with progress
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --quiet &
        spinner $!
        
        if [ $? -eq 0 ]; then
            log_success "All dependencies installed successfully"
        else
            log_error "Dependency installation failed"
            log_info "Trying with verbose output..."
            pip install -r requirements.txt
            return 1
        fi
    else
        log_error "requirements.txt not found"
        return 1
    fi
}

verify_installation() {
    print_section "7️⃣  Verifying Installation"
    
    log_info "Testing imports..."
    
    if python -c "from llm_edge_router import LLMEdgeRouter" 2>/dev/null; then
        log_success "Core modules imported successfully"
    else
        log_error "Import verification failed"
        return 1
    fi
    
    log_info "Checking CLI tool..."
    if [ -f "edge-llm-cli.py" ]; then
        chmod +x edge-llm-cli.py
        log_success "CLI tool ready"
    fi
}

################################################################################
# Model Selection and Download
################################################################################

select_models() {
    print_section "8️⃣  Model Selection"
    
    echo -e "${BOLD}Recommended models for $PLATFORM:${NC}\n"
    
    case $PLATFORM in
        "desktop"|"all")
            echo "  ${CHECK} Phi-3.5-mini Q4 (2GB) - Best all-around"
            echo "  ${CHECK} Qwen2.5 3B Q4 (1.9GB) - Best for coding"
            MODELS="phi-3.5-mini-q4 qwen2.5-3b-q4"
            ;;
        "ios")
            echo "  ${CHECK} Phi-3.5-mini Q4 (2GB) - Optimized for iOS"
            echo "  ${CHECK} Qwen2.5 3B Q4 (1.9GB) - Coding support"
            MODELS="phi-3.5-mini-q4 qwen2.5-3b-q4"
            ;;
        "android")
            echo "  ${CHECK} Phi-3.5-mini Q4 (2GB) - Works great on Android"
            echo "  ${CHECK} Llama 3.2 3B Q4 (1.7GB) - Fast alternative"
            MODELS="phi-3.5-mini-q4 llama-3.2-3b-q4"
            ;;
        "web")
            echo "  ${CHECK} Gemma 2 2B Q4 (1.4GB) - Smallest, fastest"
            MODELS="gemma-2-2b-q4"
            ;;
    esac
    
    echo ""
    if ask_yes_no "Download recommended models?"; then
        DOWNLOAD_MODELS=true
    else
        DOWNLOAD_MODELS=false
    fi
}

download_models() {
    if [ "$DOWNLOAD_MODELS" = false ]; then
        log_info "Skipping model downloads"
        return 0
    fi
    
    print_section "9️⃣  Downloading Models"
    
    log_warning "This will download ~2-4GB of data"
    log_info "Downloads will take 10-30 minutes depending on internet speed"
    echo ""
    
    if ! ask_yes_no "Continue with download?"; then
        log_info "Skipping downloads (you can download later)"
        return 0
    fi
    
    log_info "Starting downloads..."
    
    for model in $MODELS; do
        echo ""
        log_info "Downloading $model..."
        python download_models.py --download $model
        
        if [ $? -eq 0 ]; then
            log_success "$model downloaded successfully"
        else
            log_error "$model download failed"
        fi
    done
}

################################################################################
# Cloud API Setup
################################################################################

setup_cloud_apis() {
    print_section "🔟  Cloud API Setup (Optional)"
    
    echo -e "${BOLD}Cloud APIs provide fallback for complex tasks${NC}"
    echo "All services offer generous free tiers:"
    echo "  • Gemini Flash: 1M tokens/day free"
    echo "  • Groq: 14K tokens/day free"
    echo "  • Together.ai: $1/month free credits"
    echo ""
    
    if ask_yes_no "Configure cloud APIs now?"; then
        python edge-llm-cli.py config
    else
        log_info "Skipping cloud API setup (can configure later with: ./edge-llm-cli.py config)"
    fi
}

################################################################################
# Testing
################################################################################

run_tests() {
    print_section "1️⃣1️⃣  Testing Installation"
    
    if ask_yes_no "Run quick test?"; then
        log_info "Running system test..."
        
        ./edge-llm-cli.py status
        
        echo ""
        log_info "Testing model routing..."
        python -c "
from llm_edge_router import LLMEdgeRouter
router = LLMEdgeRouter()
decision = router.route_request('What is machine learning?')
print(f'✓ Router working - Selected: {decision.selected_model}')
"
        
        if [ $? -eq 0 ]; then
            log_success "All tests passed!"
        else
            log_error "Some tests failed"
        fi
    fi
}

################################################################################
# Platform-Specific Instructions
################################################################################

show_next_steps() {
    print_section "🎉 Setup Complete!"
    
    echo -e "${GREEN}${BOLD}Your Edge LLM System is ready!${NC}\n"
    
    case $PLATFORM in
        "desktop"|"all")
            echo -e "${BOLD}Try these commands:${NC}"
            echo "  ./edge-llm-cli.py chat              # Interactive chat"
            echo "  ./edge-llm-cli.py models            # List models"
            echo "  ./edge-llm-cli.py benchmark         # Run benchmarks"
            echo "  python example_integration.py       # Run demos"
            echo ""
            ;;
        "ios")
            echo -e "${BOLD}Next steps for iOS:${NC}"
            echo "  1. Open Xcode"
            echo "  2. Follow guide: STEP_BY_STEP_DEPLOYMENT.md (iOS section)"
            echo "  3. Models are in: ./models/"
            echo ""
            ;;
        "android")
            echo -e "${BOLD}Next steps for Android:${NC}"
            echo "  1. Open Android Studio"
            echo "  2. Follow guide: STEP_BY_STEP_DEPLOYMENT.md (Android section)"
            echo "  3. Models are in: ./models/"
            echo ""
            ;;
        "web")
            echo -e "${BOLD}Next steps for Web:${NC}"
            echo "  1. cd edge-llm-web"
            echo "  2. npm install"
            echo "  3. npm run dev"
            echo "  4. Open: http://localhost:5173"
            echo ""
            ;;
    esac
    
    echo -e "${BOLD}Documentation:${NC}"
    echo "  README.md                      # Full documentation"
    echo "  STEP_BY_STEP_DEPLOYMENT.md     # Detailed deployment guide"
    echo "  platform_implementations.md    # Platform-specific code"
    echo ""
    
    echo -e "${BOLD}Quick start:${NC}"
    echo -e "  ${CYAN}./edge-llm-cli.py chat${NC}       # Start chatting now!"
    echo ""
}

################################################################################
# Cleanup on Error
################################################################################

cleanup_on_error() {
    log_error "Setup failed"
    log_info "Check the error messages above for details"
    
    echo -e "\n${BOLD}Common issues:${NC}"
    echo "  • Python version too old (need 3.9+)"
    echo "  • No internet connection"
    echo "  • Insufficient disk space"
    echo "  • Missing system dependencies"
    
    exit 1
}

trap cleanup_on_error ERR

################################################################################
# Main Execution
################################################################################

main() {
    clear
    print_header
    
    # System checks
    check_python || exit 1
    check_disk_space || exit 1
    check_internet || exit 1
    
    # Platform selection
    select_platform
    
    # Environment setup
    setup_virtualenv || exit 1
    install_dependencies || exit 1
    verify_installation || exit 1
    
    # Models
    select_models
    download_models
    
    # Optional: Cloud APIs
    setup_cloud_apis
    
    # Testing
    run_tests
    
    # Success!
    show_next_steps
    
    # Summary
    print_section "📊 Setup Summary"
    echo "  Platform: $PLATFORM"
    echo "  Python: $PYTHON_VERSION"
    echo "  Models: $(ls -1 models/*.gguf 2>/dev/null | wc -l) downloaded"
    echo "  Status: ${GREEN}Ready to use!${NC}"
    echo ""
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" -eq "${0}" ]; then
    main
fi
