# Docker build helper — layered monorepo images (abstract-base/*)
# Usage:
#   .\scripts\docker-build.ps1 bases          # project-base + mcp-base + agent-base
#   .\scripts\docker-build.ps1 service chat-gateway
#   .\scripts\docker-build.ps1 all            # bases + all supermarket services
#   .\scripts\docker-build.ps1 stack          # build all + compose up core templates
param(
    [Parameter(Position = 0)]
    [ValidateSet("bases", "service", "all", "stack", "supermarket")]
    [string]$Command = "all",
    [Parameter(Position = 1)]
    [string]$ServiceName = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

# Keep in sync with docker/images.yaml supermarket services
$SupermarketServices = @(
    "sql-gateway",
    "conversational-router",
    "sql-planner",
    "risk-reviewer",
    "data-analyst",
    "chat-gateway"
)

$TemplateServices = @(
    "base-mcp-server",
    "base-agent",
    "base-runner"
)

function Build-ProjectBase {
    Write-Host "==> Building abstract-base/project-base:local"
    docker build -f docker/base/Dockerfile.project -t abstract-base/project-base:local .
}

function Build-McpBase {
    Write-Host "==> Building abstract-base/mcp-base:local"
    docker build -f docker/base/Dockerfile.mcp `
        --build-arg PROJECT_BASE=abstract-base/project-base:local `
        -t abstract-base/mcp-base:local .
}

function Build-AgentBase {
    Write-Host "==> Building abstract-base/agent-base:local"
    docker build -f docker/base/Dockerfile.agent `
        --build-arg PROJECT_BASE=abstract-base/project-base:local `
        -t abstract-base/agent-base:local .
}

function Build-Bases {
    Build-ProjectBase
    Build-McpBase
    Build-AgentBase
}

function Build-Service {
    param([string]$Name)
    if (-not $Name) {
        throw "Usage: docker-build.ps1 service <compose-service-name>"
    }
    Write-Host "==> Building service: $Name"
    docker compose build $Name
}

function Build-AllServices {
    param([string[]]$List)
    foreach ($s in $List) {
        Build-Service $s
    }
}

switch ($Command) {
    "bases" {
        Build-Bases
    }
    "service" {
        Build-Bases
        Build-Service $ServiceName
    }
    "all" {
        Build-Bases
        Build-AllServices $SupermarketServices
        Build-AllServices $TemplateServices
    }
    "supermarket" {
        Build-Bases
        Build-AllServices $SupermarketServices
    }
    "stack" {
        Build-Bases
        Build-AllServices $TemplateServices
        docker compose up -d base-mcp-server base-agent
        Write-Host "Runner (poll loop): docker compose --profile runner up -d base-runner"
    }
}
