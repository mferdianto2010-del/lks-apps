#!/bin/bash
# Pemeriksaan akun AWS SEBELUM mulai. Jalankan di CloudShell: bash preflight.sh
REGION=${AWS_DEFAULT_REGION:-$(aws configure get region 2>/dev/null)}
bad=0
ok()   { echo "PASS  $1"; }
warn() { echo "WARN  $1  ->  $2"; }
ng()   { echo "FAIL  $1  ->  $2"; bad=1; }

ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
[ -n "$ACCOUNT" ] && ok "kredensial AWS valid (akun $ACCOUNT)" || { ng "kredensial AWS" "login ulang / perbarui token lab"; exit 1; }
[ "$REGION" = "us-east-1" ] && ok "region us-east-1" || ng "region ($REGION)" "pakai us-east-1 (export AWS_DEFAULT_REGION=us-east-1)"

aws iam get-role --role-name LabRole >/dev/null 2>&1 && ok "IAM role LabRole ada" || ng "LabRole" "dipakai Lambda dan Beanstalk, harus ada di akun lab"
aws iam get-instance-profile --instance-profile-name EMR_EC2_DefaultProfile >/dev/null 2>&1 && ok "instance profile EMR_EC2_DefaultProfile ada" || ng "EMR_EC2_DefaultProfile" "diminta soal untuk Beanstalk"
aws ec2 describe-key-pairs --key-names vockey >/dev/null 2>&1 && ok "key pair vockey ada" || ng "key pair vockey" "diminta soal untuk Beanstalk"

N=$(aws ec2 describe-images --image-ids ami-0015c0130d6cc5da7 --query 'length(Images)' --output text 2>/dev/null)
[ "$N" = "1" ] && ok "AMI natInstance ami-0015c0130d6cc5da7 terlihat di akun" || ng "AMI ami-0015c0130d6cc5da7" "tidak terlihat; pastikan region us-east-1 dan AMI dibagikan ke akun ini"

N=$(aws rds describe-orderable-db-instance-options --engine mariadb --db-instance-class db.t3.micro --query 'length(OrderableDBInstanceOptions)' --output text 2>/dev/null)
[ "${N:-0}" -gt 0 ] 2>/dev/null && ok "RDS MariaDB db.t3.micro tersedia" || ng "RDS db.t3.micro" "coba db.t4g.micro (ubah DBInstanceClass di template)"

S=$(aws elasticbeanstalk list-available-solution-stacks --query "SolutionStacks[?contains(@, 'Docker running on 64bit Amazon Linux 2023')]|[0]" --output text 2>/dev/null)
[ -n "$S" ] && [ "$S" != "None" ] && ok "platform Beanstalk: $S" || ng "platform Beanstalk Docker AL2023" "tidak tersedia di region ini"

BPA=$(aws s3control get-public-access-block --account-id $ACCOUNT --query 'PublicAccessBlockConfiguration.[BlockPublicAcls,IgnorePublicAcls,BlockPublicPolicy,RestrictPublicBuckets]' --output text 2>/dev/null)
if echo "$BPA" | grep -qi true; then warn "Block Public Access tingkat akun AKTIF ($BPA)" "matikan: aws s3control delete-public-access-block --account-id $ACCOUNT"; else ok "Block Public Access tingkat akun tidak menghalangi bucket publik"; fi

command -v docker >/dev/null && ok "docker terpasang" || warn "docker tidak ada di mesin ini" "tidak masalah untuk pipeline; perlu hanya untuk build manual (CloudShell sudah ada)"
command -v git >/dev/null && ok "git terpasang" || ng "git" "dibutuhkan untuk clone dan push"
echo; [ $bad -eq 0 ] && echo "Pre-flight SELESAI: siap mulai." || echo "Pre-flight: ada yang GAGAL, perbaiki dulu sebelum lanjut."
exit $bad
