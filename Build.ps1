Param(
  [switch]$Frontend,
  [switch]$Backend
)

$next_api_base = ""


if ($Frontend) {
    Write-Host "[*] Compile Frontend"
    $next_env = "NEXT_PUBLIC_API_BASE_URL=$next_api_base"
    Write-Host $next_env
    cd .\frontend
    # Write-Output $next_env > .env
    pnpm build
    cd ..
}

if ($Backend){
  Write-Host "[*] Compile Backend"
  pyinstaller src/main.py `
    --name tinyRAG `
    --onedir `
    --add-data "frontend/out;frontend/out" `
    --collect-submodules chromadb `
    --collect-data chromadb `
    --noconfirm


  New-Item -ItemType Directory -Force -Path "dist/tinyRAG/data" | Out-Null
  Copy-Item -Force "data/CONFIG.toml" "dist/tinyRAG/data/CONFIG.toml"
}
