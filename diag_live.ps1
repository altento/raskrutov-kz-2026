$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

function Probe($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 30 -MaximumRedirection 0
        return "$($r.StatusCode) len=$($r.RawContentLength)"
    } catch {
        $resp = $_.Exception.Response
        if ($resp) {
            $code = [int]$resp.StatusCode
            $loc = $resp.Headers['Location']
            return "$code -> $loc"
        }
        return "ERR $($_.Exception.Message)"
    }
}

Write-Host "== homepage markers (is latest deploy live on ps.kz?) =="
$gh = Invoke-WebRequest -Uri "https://altento.github.io/raskrutov-kz-2026/?nc=1" -UseBasicParsing -TimeoutSec 40
$kz = Invoke-WebRequest -Uri "https://raskrutov.kz/?nc=1" -UseBasicParsing -TimeoutSec 40
Write-Host ("github len: " + $gh.RawContentLength)
Write-Host ("raskrutov len: " + $kz.RawContentLength)
foreach ($marker in @('data-page-link="pages/faq.html"', 'href="pages/web-studiya_sozdanie-saitov_landing.html"', 'player.kinescope.io', 't.me/Raskrutov_web', 'index.htmlindex.html', '../https://')) {
    $g = $gh.Content.Contains($marker)
    $k = $kz.Content.Contains($marker)
    Write-Host ("marker [{0}] github={1} raskrutov={2}" -f $marker, $g, $k)
}

Write-Host ""
Write-Host "== menu target URLs on raskrutov.kz =="
foreach ($u in @(
    "https://raskrutov.kz/pages/web-studiya_sozdanie-saitov_landing.html",
    "https://raskrutov.kz/pages/faq.html",
    "https://raskrutov.kz/pages/crm.html",
    "https://raskrutov.kz/pages/keysy.html",
    "https://raskrutov.kz/pages/web-studiya.html"
)) {
    Write-Host ("{0}  {1}" -f (Probe $u), $u)
}

Write-Host ""
Write-Host "== asset spot checks on raskrutov.kz =="
foreach ($u in @(
    "https://raskrutov.kz/assets/m-files.cdn1.cc/web/build/pages/public.bundle__q_v_1784122059.css",
    "https://raskrutov.kz/assets/m-files.cdn1.cc/web/user/fonts/montserrat/montserrat_normal.woff",
    "https://raskrutov.kz/assets/m-files.cdn1.cc/lpfile/2/7/e/27e940bfca13c46588cbb867b1d4c3d6/-/resize/1000/f__q_80115761.webp"
)) {
    Write-Host ("{0}  {1}" -f (Probe $u), $u)
}
