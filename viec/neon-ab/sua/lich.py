"""Bản có lỗi: tìm và sửa. Đặc tả ở viec/neon-ab/DE-BAI.md."""
import re, unicodedata
from datetime import datetime, timedelta
def bo_dau(s):
    s=s.replace('đ','d').replace('Đ','D')
    return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
BUOI={'sang':8,'trua':12,'chieu':14,'toi':19}
THU={'2':0,'3':1,'4':2,'5':3,'6':4,'7':5}
def doc_gio(chuoi, goc):
    s=' '.join(bo_dau(chuoi).lower().split())
    if not s: raise ValueError('rong')
    m=re.fullmatch(r'(\d+) (tieng|gio|phut) nua',s)
    if m:
        n=int(m.group(1)); return goc+(timedelta(minutes=n) if m.group(2)=='phut' else timedelta(hours=n))
    ngay=None; gio=None; phut=0; buoi=None; co_ngay=False
    def cat(p):
        nonlocal s
        m=re.search(p,s)
        if m: s=(s[:m.start()]+' '+s[m.end():]).strip(); s=' '.join(s.split())
        return m
    m=cat(r'\b(\d{1,2})/(\d{1,2})\b')
    if m:
        d,mo=int(m.group(1)),int(m.group(2))
        try: ngay=datetime(goc.year,mo,d)
        except ValueError: raise ValueError('ngay sai')
        if ngay.date()<goc.date(): ngay=datetime(goc.year+1,mo,d)
        co_ngay=True
    m=cat(r'\b(\d{1,2})(?::(\d{2})|h(\d{2})?| gio(?: (\d{2}))?)')
    if m:
        gio=int(m.group(1)); phut=int(m.group(2) or m.group(3) or m.group(4) or 0)
        if gio>23 or phut>59: raise ValueError('gio sai')
    m=cat(r'\b(sang|trua|chieu|toi)\b')
    if m: buoi=m.group(1)
    m=not co_ngay and cat(r'\bthu (\d)\b')
    if m:
        if m.group(1) not in THU: raise ValueError('thu sai')
        wd=THU[m.group(1)]; delta=(wd-goc.weekday())%7 or 7; ngay=datetime.combine((goc+timedelta(days=delta)).date(),datetime.min.time()); co_ngay=True
    elif not co_ngay and cat(r'\bchu nhat\b'):
        delta=(6-goc.weekday())%7 or 7; ngay=datetime.combine((goc+timedelta(days=delta)).date(),datetime.min.time()); co_ngay=True
    elif not co_ngay and cat(r'\bngay kia\b'): ngay=datetime.combine((goc+timedelta(days=2)).date(),datetime.min.time()); co_ngay=True
    elif not co_ngay and cat(r'\bmai\b'): ngay=datetime.combine((goc+timedelta(days=1)).date(),datetime.min.time()); co_ngay=True
    elif not co_ngay and cat(r'\bnay\b'): ngay=datetime.combine(goc.date(),datetime.min.time()); co_ngay=True
    if s: raise ValueError('du: '+s)
    if gio is None and buoi is None and not co_ngay: raise ValueError('trong')
    if gio is None: gio=BUOI[buoi] if buoi else 9
    elif buoi in ('chieu','toi') and gio<12: gio+=12
    if ngay is None:
        kq=datetime(goc.year,goc.month,goc.day,gio,phut)
        if kq<=goc: kq+=timedelta(days=1)
        return kq
    return ngay.replace(hour=gio,minute=phut)
