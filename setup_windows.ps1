# setup_windows.ps1 - Complete setup script for Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smart Academic System - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Green
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install requirements
Write-Host "`nInstalling requirements..." -ForegroundColor Green
pip install -r requirements.txt

# Create necessary directories
Write-Host "`nCreating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "app\ml_models\models"
New-Item -ItemType Directory -Force -Path "uploads\audio"
New-Item -ItemType Directory -Force -Path "uploads\submissions"
New-Item -ItemType Directory -Force -Path "data"

# Check if MySQL is installed
$mysql = Get-Command mysql -ErrorAction SilentlyContinue
if ($mysql) {
    Write-Host "`nMySQL found. Creating database..." -ForegroundColor Green
    
    # You'll need to enter your MySQL root password
    $mysqlPassword = Read-Host "Enter MySQL root password" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword)
    $password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    
    # Create database
    mysql -u root -p$password -e "CREATE DATABASE IF NOT EXISTS smart_academic_system;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Failed to create database. Please create manually." -ForegroundColor Red
    }
} else {
    Write-Host "`nMySQL not found in PATH. Please install MySQL and create database manually." -ForegroundColor Yellow
    Write-Host "Run: mysql -u root -p -e 'CREATE DATABASE smart_academic_system;'" -ForegroundColor Yellow
}

# Generate sample data
Write-Host "`nGenerating sample data and training ML models..." -ForegroundColor Green
python ml_pipeline.py

# Load sample data
Write-Host "`nLoading sample data into database..." -ForegroundColor Green
python load_data.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTo run the application:" -ForegroundColor Yellow
Write-Host "1. Make sure MySQL is running" -ForegroundColor White
Write-Host "2. Update database credentials in config.py if needed" -ForegroundColor White
Write-Host "3. Run: python run.py" -ForegroundColor White
Write-Host "4. Open browser to: http://localhost:5000" -ForegroundColor White
Write-Host "`nDefault credentials:" -ForegroundColor Cyan
Write-Host "Admin - username: admin, password: admin123" -ForegroundColor White
Write-Host "Lecturer - username: lecturer, password: lecturer123" -ForegroundColor White
Write-Host "Student - username: student, password: student123" -ForegroundColor White