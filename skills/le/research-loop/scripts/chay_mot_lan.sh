# dùng: run.sh Yxxx "mô tả"  (đã sửa solution.py)
NK=${NK:-$HOME/.claude/skills/research-loop/scripts/nhat_ky.py}; D=runs; y=$1; desc=$2
if git diff --quiet; then echo "KHONG DOI CODE, bo qua"; exit 1; fi; git commit -qam "$y: $desc"; h=$(git rev-parse --short HEAD)
timeout 60 python3 eval.py > $D/run.log 2>&1; m=$(grep '^metric:' $D/run.log | cut -d' ' -f2)
best=$(python3 $NK tom $D | grep -o '→ tốt nhất [-0-9.e]*' | awk '{print $4}')
if [ -z "$m" ]; then tail -n 3 $D/run.log; python3 $NK ghi $D $y crash crash "$desc" --commit $h >/dev/null; git reset -q --hard $(python3 $NK tot $D); echo "$y CRASH";
elif [ -z "$best" ] || python3 -c "import sys;sys.exit(0 if $m<$best else 1)"; then python3 $NK ghi $D $y $m keep "$desc" --commit $h >/dev/null; echo "$y $m KEEP (trước $best)";
else python3 $NK ghi $D $y $m discard "$desc" --commit $h >/dev/null; git reset -q --hard $(python3 $NK tot $D); echo "$y $m discard (best $best)"; fi
python3 $NK chon $D
