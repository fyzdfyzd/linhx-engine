"""Máy đo QR: giải mã ảnh chụp màn QR, tách trường VietQR (EMVCo), kiểm CRC."""
import cv2, json, sys
def crc(b):
    c=0xFFFF
    for x in b:
        c^=x<<8
        for _ in range(8): c=((c<<1)^0x1021)&0xFFFF if c&0x8000 else (c<<1)&0xFFFF
    return f"{c:04X}"
def tlv(s):
    out={};i=0
    while i+4<=len(s):
        t,l=s[i:i+2],int(s[i+2:i+4]);out[t]=s[i+4:i+4+l];i+=4+l
    return out
def kiem(p):
    img=cv2.imread(p)
    if img is None: return {"anh":p,"loi":"không đọc được ảnh"}
    det=cv2.QRCodeDetector()
    v,_,_=det.detectAndDecode(img)
    if not v:
        # thử phóng to
        big=cv2.resize(img,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST)
        v,_,_=det.detectAndDecode(big)
    if not v: return {"anh":p,"giai_ma":False}
    f=tlv(v); m=tlv(f.get("38","")); acc=tlv(m.get("01","")); add=tlv(f.get("62",""))
    so=acc.get("01","")
    return {"anh":p.split('/')[-1],"giai_ma":True,"crc_dung":crc(v[:-4].encode())==v[-4:],
      "napas":m.get("00")=="A000000727","bin":acc.get("00"),"tk":(so[:2]+"***"+so[-2:]) if so else None,
      "dong":f.get("01")=="12","so_tien":f.get("54"),"tien_te":f.get("53"),"noi_dung":add.get("08")}
for p in sys.argv[1:]: print(json.dumps(kiem(p),ensure_ascii=False))
