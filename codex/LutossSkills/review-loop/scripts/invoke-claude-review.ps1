param(
  [string]$PromptPath,
  [string]$OutputPath,
  [int]$TimeoutSeconds = 1800,
  [string]$Model = "opus",
  [string]$Effort = "max",
  [switch]$SkipSmokeTest,
  [switch]$DryRun,
  [switch]$Help
)

if ($Help) {
  @"
invoke-claude-review.ps1

Runs a Claude review prompt with direct prompt arguments, optional smoke test,
and a timeout. Claude output is written to OutputPath.

Required:
  -PromptPath  Path to a UTF-8 text/Markdown prompt
  -OutputPath  Path where stdout should be written

Optional:
  -TimeoutSeconds  Default 1800
  -Model           Default opus, the nearest stable CLI alias for requested Opus 4.8 Max
  -Effort          Default max
  -SkipSmokeTest   Skip CLAUDE_OK smoke test
  -DryRun          Validate inputs and print the planned invocation only
"@
  exit 0
}

if (-not $PromptPath -or -not $OutputPath) {
  throw "PromptPath and OutputPath are required. Use -Help for usage."
}

$resolvedPrompt = Resolve-Path -LiteralPath $PromptPath -ErrorAction Stop
$prompt = Get-Content -Raw -LiteralPath $resolvedPrompt
if ([string]::IsNullOrWhiteSpace($prompt)) {
  throw "Prompt file is empty: $resolvedPrompt"
}
if ($prompt.Length -gt 7000) {
  throw "Prompt is too long for a stable direct CLI argument. Use a compact, path-oriented prompt under 7000 characters."
}

$outputParent = Split-Path -Parent $OutputPath
if ($outputParent) {
  New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}

$claude = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claude) {
  $claude = Get-Command claude.exe -ErrorAction SilentlyContinue
}
if (-not $claude) {
  throw "Claude CLI not found on PATH."
}

function Invoke-ClaudeProcess {
  param(
    [string[]]$Arguments,
    [int]$Timeout
  )

  $psi = [System.Diagnostics.ProcessStartInfo]::new()
  $psi.FileName = $claude.Source
  foreach ($arg in $Arguments) {
    [void]$psi.ArgumentList.Add($arg)
  }
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false

  $process = [System.Diagnostics.Process]::Start($psi)
  # Drain both streams asynchronously; reading only after WaitForExit can
  # deadlock once the child fills an undrained pipe buffer.
  $stdoutTask = $process.StandardOutput.ReadToEndAsync()
  $stderrTask = $process.StandardError.ReadToEndAsync()

  if (-not $process.WaitForExit($Timeout * 1000)) {
    $process.Kill()
    $process.WaitForExit()
    throw "Claude timed out after $Timeout seconds."
  }
  # Second, untimed WaitForExit flushes pending async output.
  $process.WaitForExit()

  [pscustomobject]@{
    ExitCode = $process.ExitCode
    Stdout = $stdoutTask.GetAwaiter().GetResult()
    Stderr = $stderrTask.GetAwaiter().GetResult()
  }
}

if ($DryRun) {
  "Claude: $($claude.Source)"
  "Prompt: $resolvedPrompt"
  "Output: $OutputPath"
  "TimeoutSeconds: $TimeoutSeconds"
  "Args: -p --model $Model --effort $Effort <prompt>"
  exit 0
}

if (-not $SkipSmokeTest) {
  $smoke = Invoke-ClaudeProcess -Arguments @("-p", "--model", $Model, "--effort", $Effort, "Reply exactly: CLAUDE_OK") -Timeout 120
  if ($smoke.ExitCode -ne 0 -or ($smoke.Stdout -notmatch "CLAUDE_OK")) {
    throw "Claude smoke test failed. Exit=$($smoke.ExitCode) Stderr=$($smoke.Stderr)"
  }
}

$result = Invoke-ClaudeProcess -Arguments @("-p", "--model", $Model, "--effort", $Effort, $prompt) -Timeout $TimeoutSeconds
$result.Stdout | Set-Content -LiteralPath $OutputPath -Encoding UTF8

if ($result.ExitCode -ne 0) {
  throw "Claude review failed. Exit=$($result.ExitCode) Stderr=$($result.Stderr)"
}

"Wrote Claude review output to $OutputPath"
