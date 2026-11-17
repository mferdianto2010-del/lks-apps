#!/bin/bash
# Pemakaian: ./smoke-test.sh <API_URL> [APP_URL]
#   API_URL = Invoke URL API Gateway, mis. https://abc123.execute-api.us-east-1.amazonaws.com/production
#   APP_URL = domain Beanstalk (opsional), mis. http://lks-eb-apps-xxx.us-east-1.elasticbeanstalk.com
API=${1%/}; APP=${2%/}
[ -z "$API" ] && { echo "Pemakaian: $0 <API_URL> [APP_URL]"; exit 2; }
pass=0; fail=0; OUT=$(mktemp)
check() { if [ "$2" = "$3" ]; then echo "PASS  $1"; pass=$((pass+1)); else echo "FAIL  $1 (diharapkan $3, dapat $2)"; fail=$((fail+1)); fi; }
code() { curl -s -m 30 -o "$OUT" -w '%{http_code}' "$@"; }
J='Content-Type: application/json'

echo "== API Gateway: $API"
check "POST   /users          (buat user)"    "$(code -X POST $API/users -H "$J" -d '{"name":"Smoke Test","email":"smoke@test.com","institution":"LKS","position":"Tester","phone":"000","image":""}')" 201
ID=$(sed -n 's/.*"id": *\([0-9][0-9]*\).*/\1/p' "$OUT")
[ -z "$ID" ] && { echo "FAIL  id user tidak terbaca, hentikan"; echo "Hasil: $pass lulus, $((fail+1)) gagal"; exit 1; }
check "GET    /users          (daftar)"       "$(code $API/users)" 200
check "GET    /users/$ID       (detail)"      "$(code $API/users/$ID)" 200
check "PUT    /users/$ID       (ubah)"        "$(code -X PUT $API/users/$ID -H "$J" -d '{"name":"Smoke Updated","email":"smoke@test.com","institution":"LKS","position":"Tester","phone":"000","image":""}')" 200
code $API/users/$ID >/dev/null; grep -q "Smoke Updated" "$OUT" && r=ok || r=salah; check "data hasil PUT tersimpan" "$r" ok
check "PUT    data sama persis (bukan 404)"   "$(code -X PUT $API/users/$ID -H "$J" -d '{"name":"Smoke Updated","email":"smoke@test.com","institution":"LKS","position":"Tester","phone":"000","image":""}')" 200
check "DELETE /users/$ID       (hapus)"       "$(code -X DELETE $API/users/$ID)" 200
check "GET    /users/$ID       (sudah hilang)" "$(code $API/users/$ID)" 404

if [ -n "$APP" ]; then
  echo "== Aplikasi web: $APP"
  check "GET /health" "$(code $APP/health)" 200
  check "GET /  (halaman User Management)" "$(code $APP/)" 200
  grep -q "User Management" "$OUT" && r=ok || r=salah; check "isi halaman memuat 'User Management'" "$r" ok
  check "POST /api/users (lewat aplikasi)" "$(code -X POST $APP/api/users -F name=SmokeApp -F email=a@b.c -F institution=LKS -F position=Tester -F phone=1)" 201
  AID=$(sed -n 's/.*"id": *\([0-9][0-9]*\).*/\1/p' "$OUT")
  check "GET  /api/users" "$(code $APP/api/users)" 200
  [ -n "$AID" ] && check "DELETE /api/users/$AID" "$(code -X DELETE $APP/api/users/$AID)" 200
fi
echo; echo "Hasil: $pass lulus, $fail gagal"; rm -f "$OUT"; [ $fail -eq 0 ]
