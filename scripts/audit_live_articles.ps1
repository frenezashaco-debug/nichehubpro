# Read canonical production URLs with Windows certificate validation enabled.
$articleAuditRoot = Split-Path -Parent $PSScriptRoot
$articleAuditRows = @(Get-ChildItem -LiteralPath (Join-Path $articleAuditRoot 'articles') -Filter '*.html' | ForEach-Object -Parallel {
    $articleFile = $_
    $articleUrl = 'https://nichehubpro.com/articles/' + $articleFile.Name
    try {
        $articleResponse = Invoke-WebRequest -Uri $articleUrl -TimeoutSec 25 -ErrorAction Stop
        $articleRemote = $articleResponse.Content.Replace("`r`n", "`n").Trim()
        $articleLocal = [System.IO.File]::ReadAllText($articleFile.FullName).Replace("`r`n", "`n").Trim()
        # Cloudflare inserts its own analytics script after GitHub Pages serves HTML.
        $articleRemoteComparable = [regex]::Replace($articleRemote, '<script\b[^>]*\bsrc="https://static\.cloudflareinsights\.com/[^\"]+"[^>]*>[\s\S]*?</script>', '')
        $articleRemoteComparable = [regex]::Replace($articleRemoteComparable, '>\s+<', '><')
        $articleLocalComparable = [regex]::Replace($articleLocal, '>\s+<', '><')
        $articleDecoded = [System.Net.WebUtility]::HtmlDecode($articleRemote)
        [pscustomobject]@{
            url = $articleUrl
            status = [int]$articleResponse.StatusCode
            matches_local = $articleRemoteComparable -ceq $articleLocalComparable
            em_dashes = ([regex]::Matches($articleDecoded, [string][char]0x2014)).Count
            ai_captions = ([regex]::Matches($articleDecoded, 'Images in this article are AI-generated illustrations', 'IgnoreCase')).Count
            cache_status = [string]::Join(',', $articleResponse.Headers['CF-Cache-Status'])
        }
    } catch {
        [pscustomobject]@{url = $articleUrl; error = $_.Exception.Message}
    }
} -ThrottleLimit 6)
$articleAuditReport = Join-Path $articleAuditRoot 'reports/live-article-audit.json'
$articleAuditRows | Sort-Object url | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $articleAuditReport -Encoding utf8
[pscustomobject]@{
    checked = $articleAuditRows.Count
    request_errors = @($articleAuditRows | Where-Object error).Count
    pages_with_em_dashes = @($articleAuditRows | Where-Object { $_.em_dashes -gt 0 }).Count
    pages_with_ai_captions = @($articleAuditRows | Where-Object { $_.ai_captions -gt 0 }).Count
    matches_local = @($articleAuditRows | Where-Object matches_local).Count
} | ConvertTo-Json
