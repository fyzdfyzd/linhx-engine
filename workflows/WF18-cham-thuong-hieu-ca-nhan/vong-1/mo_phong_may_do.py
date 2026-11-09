# Mô phỏng máy đo WF18: điểm "có mặt" giữa 2 lần chạy lệch bao nhiêu, và luật "lỗi chắc >=2/n"
import random, math
random.seed(9)
def lan_chay(p, cau, luot, mohinh):
    tong = cau*luot*mohinh
    return 100*sum(random.random()<p for _ in range(tong))/tong
print("A. Lệch |run1-run2| (điểm %), p95, theo cấu hình (câu x lượt x 3 mô hình), p=0.5 (xấu nhất)")
for cau,luot in [(12,1),(12,3),(12,5),(25,5),(25,10)]:
    d=sorted(abs(lan_chay(.5,cau,luot,3)-lan_chay(.5,cau,luot,3)) for _ in range(4000))
    print(f"  {cau}x{luot}x3={cau*luot*3:4d} ô: p50={d[2000]:.1f} p95={d[3800]:.1f}  tỉ lệ lệch<=5: {sum(x<=5 for x in d)/40:.0f}%  <=10: {sum(x<=10 for x in d)/40:.0f}%")
print("B. Luật 'lỗi chắc' = lặp >=2 trên n lượt. P(lọt vào báo cáo)")
def p_at_least(k,n,q): return sum(math.comb(n,i)*q**i*(1-q)**(n-i) for i in range(k,n+1))
for q in [.1,.2,.4,.6]:
    print(f"  lỗi xuất hiện {int(q*100)}% số lượt: n=3 {p_at_least(2,3,q):.2f} · n=5 {p_at_least(2,5,q):.2f} · n=10 (>=3) {p_at_least(3,10,q):.2f}")
