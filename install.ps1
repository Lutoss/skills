# Install a skill pack (claude or codex) globally or into a project.
# PowerShell 5.1 compatible.
param(
    [Parameter(Position = 0)][string]$Pack,
    [Parameter(Position = 1)][string]$Scope = "global",
    [Parameter(Position = 2)][string]$TargetDir = "."
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host @"
Usage: install.ps1 <pack> [scope] [target-dir]

  pack        claude | codex
  scope       global (default) | project
  target-dir  project scope only: target directory (default: current dir)

Destinations:
  claude global    `$HOME\.claude\skills
  claude project   <target-dir>\.claude\skills
  codex  global    `$HOME\.agents\skills
  codex  project   <target-dir>\.agents\skills

Examples:
  .\install.ps1 claude
  .\install.ps1 codex project C:\path\to\repo
"@
}

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path

switch ($Pack) {
    "claude" { $SubDir = Join-Path ".claude" "skills" }
    "codex"  { $SubDir = Join-Path ".agents" "skills" }
    default {
        Write-Host "Error: pack must be 'claude' or 'codex'."
        Write-Host ""
        Show-Usage
        exit 1
    }
}

switch ($Scope) {
    "global" {
        $Dest = Join-Path $HOME $SubDir
    }
    "project" {
        if (-not (Test-Path -Path $TargetDir -PathType Container)) {
            Write-Host "Error: target directory '$TargetDir' does not exist."
            exit 1
        }
        $Dest = Join-Path (Resolve-Path -Path $TargetDir).Path $SubDir
    }
    default {
        Write-Host "Error: scope must be 'global' or 'project'."
        Write-Host ""
        Show-Usage
        exit 1
    }
}

if (-not (Test-Path -Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}

$Installed = @()
$Overwritten = 0

$PackDir = Join-Path $RepoDir $Pack
# Directories only: loose files (README, ...) are skipped.
foreach ($SkillDir in (Get-ChildItem -Path $PackDir | Where-Object { $_.PSIsContainer })) {
    $Name = $SkillDir.Name
    $Target = Join-Path $Dest $Name
    if (Test-Path -Path $Target) {
        Write-Host "Overwriting existing skill: $Name"
        Remove-Item -Path $Target -Recurse -Force
        $Overwritten++
    }
    Copy-Item -Path $SkillDir.FullName -Destination $Target -Recurse
    $Installed += $Name
}

Write-Host ""
Write-Host "Installed $($Installed.Count) skill(s) to $Dest ($Overwritten overwritten):"
foreach ($Name in $Installed) {
    Write-Host "  - $Name"
}
Write-Host ""
Write-Host "Optional companion: the skills reference mattpocock/skills (code-review, tdd, handoff, ...)."
Write-Host "Install them separately from https://github.com/mattpocock/skills for the full flow."
