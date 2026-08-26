param (
    [Parameter(Mandatory=$true)]
    [string]$HfUsername,
    [string]$SpaceName = "atcs-smart-monitoring-backend"
)

$HfRemoteUrl = "https://huggingface.co/spaces/$HfUsername/$SpaceName"

Write-Host "Menyiapkan deployment backend ke Hugging Face Spaces: $HfRemoteUrl" -ForegroundColor Cyan

# Cek apakah remote 'hf' sudah ada
$existingRemote = git remote | Where-Object { $_ -eq "hf" }
if ($existingRemote) {
    Write-Host "Mengupdate remote git 'hf'..." -ForegroundColor Yellow
    git remote set-url hf $HfRemoteUrl
} else {
    Write-Host "Menambahkan remote git 'hf'..." -ForegroundColor Yellow
    git remote add hf $HfRemoteUrl
}

Write-Host "Melakukan push subfolder backend ke Hugging Face Space..." -ForegroundColor Green
git subtree push --prefix backend hf main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deployment berhasil dikirim ke Hugging Face Spaces!" -ForegroundColor Green
    Write-Host "Backend URL: https://$HfUsername-$SpaceName.hf.space" -ForegroundColor Cyan
    Write-Host "WebSocket URL: wss://$HfUsername-$SpaceName.hf.space/ws/metrics" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Gagal melakukan push. Pastikan Space sudah dibuat di Hugging Face dan token akses git memiliki izin Write." -ForegroundColor Red
}
