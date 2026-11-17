# lks-apps - LKS Kota Malang 2025 (Automation with CI/CD)

Aplikasi User Management: Flask (port 5000) -> API Gateway -> 5 Lambda -> RDS MariaDB.

| Folder/File | Fungsi |
|---|---|
| `app.py`, `templates/index.html` | aplikasi web (proxy ke API Gateway, upload gambar ke S3, log ke EFS) |
| `Dockerfile`, `requirements.txt`, `.env` | container aplikasi |
| `lambda/*.py` | 5 fungsi Lambda + `init_db.py` (buat DB `techno-rds` dan tabel `users`) |
| `infra/lks-infra.yaml` | CloudFormation: VPC, NAT Instance, SG, S3, RDS, EFS |
| `scripts/create-lambda.sh`, `scripts/create-apigw.sh` | membuat 5 Lambda dan API Gateway lewat CLI |
| `scripts/preflight.sh` | cek akun AWS sebelum mulai (LabRole, vockey, AMI NAT, RDS, platform EB, Block Public Access) |
| `scripts/smoke-test.sh` | uji otomatis API Gateway dan aplikasi setelah deploy |
| `.github/workflows/lks-cicd.yml` | pipeline 4 job |
| `tests/` | skrip uji lokal (butuh MariaDB lokal, lihat di bawah) |

Ikuti urutan di tutorial. Ganti `API_ID` dan `yourname` di `.env` sebelum push.

## Uji lokal (opsional)
```
pip install -r requirements.txt pymysql moto[server]
# jalankan MariaDB lokal dengan user admin / Technobrain2025!
python tests/test_lambda.py          # uji 5 Lambda ke database
```
