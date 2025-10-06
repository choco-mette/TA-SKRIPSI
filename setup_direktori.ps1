# Nama folder utama proyek
$root = "rag_backend"

# Daftar folder yang akan dibuat
$folders = @(
    "$root/app",
    "$root/app/api",
    "$root/app/core",
    "$root/app/db",
    "$root/app/db/models",
    "$root/app/db/crud",
    "$root/app/rag",
    "$root/app/sentiment",
    "$root/app/schemas",
    "$root/app/services",
    "$root/data/documents",
    "$root/data/embeddings",
    "$root/models/indobertweet",
    "$root/tests"
)

# Buat semua folder
foreach ($f in $folders) {
    New-Item -ItemType Directory -Force -Path $f | Out-Null
}

# Tambahkan file penting kosong di root
New-Item -ItemType File "$root/.env" | Out-Null
New-Item -ItemType File "$root/requirements.txt" | Out-Null
New-Item -ItemType File "$root/README.md" | Out-Null
New-Item -ItemType File "$root/run.sh" | Out-Null

Write-Host "✅ Struktur folder proyek '$root' berhasil dibuat!"
