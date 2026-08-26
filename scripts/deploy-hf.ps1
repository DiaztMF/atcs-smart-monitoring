param (
    [Parameter(Mandatory=$true)]
    [string]$HfUsername,
    [string]$HfToken = "",
    [string]$SpaceName = "atcs-smart-monitoring-backend"
)

if ($HfToken -ne "") {
    $HfRemoteUrl = "https://$($HfUsername):$($HfToken)@huggingface.co/spaces/$HfUsername/$SpaceName"
} else {
    $HfRemoteUrl = "https://huggingface.co/spaces/$HfUsername/$SpaceName"
}

Write-Host "Menyiapkan deployment backend ke Hugging Face Spaces: https://huggingface.co/spaces/$HfUsername/$SpaceName" -ForegroundColor Cyan

# Split subfolder backend ke temporary branch
Write-Host "Mengekstrak folder backend ke temporary branch..." -ForegroundColor Yellow
if (git branch --list hf-deploy) {
    git branch -D hf-deploy
}
git subtree split --prefix backend -b hf-deploy

# Force push ke remote main HF Space
Write-Host "Melakukan push ke Hugging Face Space..." -ForegroundColor Green
git push $HfRemoteUrl hf-deploy:main --force

# Hapus branch sementara
git branch -D hf-deploy

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deployment berhasil dikirim ke Hugging Face Spaces!" -ForegroundColor Green
    Write-Host "Backend URL: https://$HfUsername-$SpaceName.hf.space" -ForegroundColor Cyan
    Write-Host "WebSocket URL: wss://$HfUsername-$SpaceName.hf.space/ws/metrics" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Gagal melakukan push. Pastikan Access Token dan nama Space sudah benar." -ForegroundColor Red
}
