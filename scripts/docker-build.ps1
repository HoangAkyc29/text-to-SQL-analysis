# Docker build helper — layered monorepo images (abstract-base/*)
# Usage: .\scripts\docker-build.ps1 [bases|service <name>|all|stack]
param(
    [Parameter(Position = 0)]
    [ValidateSet("bases", "service", "all", "stack")]
    [string]$Command = "all",
    [Parameter(Position = 1)]
    [string]$ServiceName = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

# TODO: keep in sync with docker/images.yaml when adding services
$ServiceList = @(
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
    foreach ($s in $ServiceList) {
        Build-Service $s
    }
}

switch ($Command) {
    "bases" {
        Build-Bases
    }
    "service" {
        Build-Service $ServiceName
    }
    "all" {
        Build-Bases
        Build-AllServices
    }
    "stack" {
        Build-Bases
        Build-AllServices
        docker compose up -d base-mcp-server base-agent
        Write-Host "Runner (poll loop): docker compose --profile runner up -d base-runner"
    }
}
