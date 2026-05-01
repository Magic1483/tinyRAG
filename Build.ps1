Param(
  [switch]$Frontend,
  [switch]$Backend
)

if ($Frontend) {
    Write-Host "[*] Compile Frontend"
    cd .\frontend
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
