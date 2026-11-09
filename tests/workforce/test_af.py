"""Thử trọn vòng SETUP → RUNNING → LEARNING → UPDATE của workforce/af.py. Không gọi mạng."""
import json, os, subprocess, sys, zipfile
import pytest

GOC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(GOC, 'workforce'))
import af  # noqa: E402
from argparse import Namespace as N  # noqa: E402


@pytest.fixture
def w(tmp_path):
    d = str(tmp_path / 'wf')
    af.lenh_moi(N(thu_muc=d, ten='Thử', don_vi='Đơn vị thử', kho=os.path.join(GOC, 'skills'), skills='linhx-chuan'))
    tc = af.doc_json(os.path.join(d, 'to-chuc.json'))
    tc['nguoi'] += [{'ma': 'hang', 'ten': 'Hằng', 'vai': 'quan_ly'}, {'ma': 'an', 'ten': 'An', 'vai': 'nhan_vien'}]
    af.ghi_json(os.path.join(d, 'to-chuc.json'), tc)
    wf = af.doc_json(os.path.join(d, 'workflow', 'viec-chung.json'))
    wf['nguoi_duyet'] = 'hang'
    af.ghi_json(os.path.join(d, 'workflow', 'viec-chung.json'), wf)
    return af.WF(d)


def lam_xong_buoc(w, ma, noi_dung='Thư cảm ơn đối tác, nguồn: su-that#ten.'):
    d = w.p('viec', ma)
    af.ghi(os.path.join(d, 'dau-ra', 'ket-qua.md'), noi_dung)
    t = af.doc(os.path.join(d, 'TASK.md')).replace('- [ ] ', '- [x] ')
    af.ghi(os.path.join(d, 'TASK.md'), t)
    with open(os.path.join(d, 'nhat-ky.md'), 'a', encoding='utf-8') as f:
        f.write('- đã đối chiếu su-that.json\n')


def giao(w, viec='Soạn thư cảm ơn', ai='an'):
    return af.lenh_giao(N(workflow='viec-chung', viec=viec, nguoi_giao=ai), w)


def chuyen(w, ma, den, ai='tho', ly_do=None):
    af.lenh_chuyen(N(ma=ma, den=den, ai=ai, ly_do=ly_do), w)


def test_setup_kiem_dat(w):
    assert af.kiem(w) == []
    assert w.ban('skill:linhx-chuan') == '1.0.0'
    assert os.path.exists(w.p('.agents', 'skills', 'linhx-chuan', 'SKILL.md'))
    assert af.doc(w.p('CLAUDE.md')).strip() == '@AGENTS.md'


def test_moi_khong_ghi_de(w):
    with pytest.raises(af.Loi):
        af.lenh_moi(N(thu_muc=w.goc, ten='x', don_vi='y', kho=None, skills=None))


def test_moi_viec_mot_thu_muc(w):
    a, b = giao(w), giao(w, 'Việc hai')
    assert (a, b) == ('LX-0001', 'LX-0002')
    for m in (a, b):
        for x in ('TASK.md', 'viec.json', 'nhat-ky.md', 'dau-vao', 'dau-ra'):
            assert os.path.exists(w.p('viec', m, x))
    assert 'người duyệt hang' in af.doc(w.p('viec', a, 'TASK.md'))


def test_cong_chong_slop(w):
    ma = giao(w)
    chuyen(w, ma, 'dang_lam')
    with pytest.raises(af.Loi, match='dau-ra/ trống'):
        chuyen(w, ma, 'cho_duyet')
    lam_xong_buoc(w, ma, 'Kính gửi [điền tên], giá TODO')
    with pytest.raises(af.Loi, match='làm dở'):
        chuyen(w, ma, 'cho_duyet')
    lam_xong_buoc(w, ma)
    chuyen(w, ma, 'cho_duyet')
    assert w.viec(ma)['trang_thai'] == 'cho_duyet'


def test_fsm_chan_nhay_buoc(w):
    ma = giao(w)
    with pytest.raises(af.Loi, match='không chuyển được'):
        chuyen(w, ma, 'xong', 'hang')


def test_chi_nguoi_duyet_duoc_duyet(w):
    ma = giao(w); chuyen(w, ma, 'dang_lam'); lam_xong_buoc(w, ma); chuyen(w, ma, 'cho_duyet')
    with pytest.raises(af.Loi, match='chỉ hang'):
        chuyen(w, ma, 'xong', 'an')
    chuyen(w, ma, 'xong', 'hang')
    tk = w.thong_ke()
    assert tk['cong_nhan']['truong'] == {'dat_lan_dau': 1, 'xong': 1, 'tra_lai': 0}


def test_tra_lai_thanh_bai_hoc_roi_de_xuat(w):
    for i in range(2):
        ma = giao(w, f'Thư {i}')
        chuyen(w, ma, 'dang_lam'); lam_xong_buoc(w, ma); chuyen(w, ma, 'cho_duyet')
        with pytest.raises(af.Loi, match='ly-do'):
            chuyen(w, ma, 'tra_lai', 'hang')
        chuyen(w, ma, 'tra_lai', 'hang', 'Thư phải xưng em, gọi khách là bạn' + (' nhé' if i else ''))
        assert w.viec(ma)['vong'] == 2
    hoc = af.doc_dong(w.p('HOC.jsonl'))
    assert len(hoc) == 1, 'hai góp ý cùng ý phải gộp thành một bài học'
    assert hoc[0]['ung_ho'] == 2 and hoc[0]['dich'] == 'workflow:viec-chung'
    moi = af.lenh_hoc(N(), w)
    assert moi == ['DX-001']
    assert af.doc_dong(w.p('HOC.jsonl'))[0]['trang_thai'] == 'de_xuat'
    # việc mới thấy bài học trong TASK.md
    assert 'xưng em' in af.doc(w.p('viec', giao(w, 'Thư 3'), 'TASK.md'))


def test_mot_viec_chua_du_bang_chung(w):
    af.ghi_phan_hoi(w, 'skill:linhx-chuan', 'xau', 'Thiếu nguồn ở bảng số', 'LX-0009', 'hang')
    af.ghi_phan_hoi(w, 'skill:linhx-chuan', 'xau', 'Thiếu nguồn ở bảng số', 'LX-0009', 'hang')
    assert af.lenh_hoc(N(), w) == [], 'hai góp ý từ cùng một việc chưa đủ'


def test_tia_bai_hoc_bi_phan_doi(w):
    af.ghi_phan_hoi(w, 'he-thong', 'xau', 'Luôn trả lời dưới 3 câu', 'LX-1', 'an')
    h = af.doc_dong(w.p('HOC.jsonl'))[0]
    for i in range(2):
        af.ghi_phan_hoi(w, 'he-thong', 'tot', 'Luôn trả lời dưới 3 câu', f'LX-{i + 2}', 'hang')
    assert af.doc_dong(w.p('HOC.jsonl'))[0]['phan_doi'] == 2
    af.lenh_hoc(N(), w)
    assert af.doc_dong(w.p('HOC.jsonl'))[0]['trang_thai'] == 'tia'
    assert h['id'] == 'H001'


def dung_de_xuat(w):
    for i in range(2):
        af.ghi_phan_hoi(w, 'skill:linhx-chuan', 'xau', 'Bảng số phải có cột nguồn', f'LX-{i}', 'hang')
    ma = af.lenh_hoc(N(), w)[0]
    d = w.p('de-xuat', ma)
    p = os.path.join(d, 'moi', '.agents', 'skills', 'linhx-chuan', 'SKILL.md')
    cu = af.doc(w.p('.agents', 'skills', 'linhx-chuan', 'SKILL.md'))
    af.ghi(p, cu + '\n- Bảng số phải có cột nguồn (vì H001: hai lần bị trả do thiếu nguồn).\n')
    return ma, d, cu


def test_thang_cap_can_thu_va_quyen(w):
    ma, d, cu = dung_de_xuat(w)
    with pytest.raises(af.Loi, match='quyền'):
        af.lenh_thang_cap(N(ma=ma, duyet='an'), w)
    with pytest.raises(af.Loi, match='ket-qua-thu'):
        af.lenh_thang_cap(N(ma=ma, duyet='chu'), w)
    af.ghi_json(os.path.join(d, 'ket-qua-thu.json'), {'tong': 5, 'dat_moi': 4, 'dat_cu': 4, 'nguoi_cham': 'cham'})
    with pytest.raises(af.Loi, match='hồi quy'):
        af.lenh_thang_cap(N(ma=ma, duyet='chu'), w)
    af.ghi_json(os.path.join(d, 'ket-qua-thu.json'), {'tong': 5, 'dat_moi': 5, 'dat_cu': 4, 'nguoi_cham': ''})
    with pytest.raises(af.Loi, match='người chấm'):
        af.lenh_thang_cap(N(ma=ma, duyet='chu'), w)
    assert w.ban('skill:linhx-chuan') == '1.0.0'


def test_thang_cap_roi_lui(w):
    ma, d, cu = dung_de_xuat(w)
    af.lenh_hoc(N(), w)
    af.ghi_json(os.path.join(d, 'ket-qua-thu.json'), {'tong': 5, 'dat_moi': 5, 'dat_cu': 4, 'nguoi_cham': 'cham'})
    af.lenh_hoc(N(), w)
    assert af.doc_json(os.path.join(d, 'de-xuat.json'))['trang_thai'] == 'cho_duyet'
    af.lenh_thang_cap(N(ma=ma, duyet='chu'), w)
    p = w.p('.agents', 'skills', 'linhx-chuan', 'SKILL.md')
    assert w.ban('skill:linhx-chuan') == '1.1.0'
    assert 'cột nguồn' in af.doc(p)
    assert os.path.exists(w.p('phat-hanh', 'ban', 'skill-linhx-chuan', '1.0.0', 'SKILL.md'))
    assert af.doc_dong(w.p('HOC.jsonl'))[0]['trang_thai'] == 'da_ap'
    af.lenh_lui(N(dich='skill:linhx-chuan', ly_do='bản mới làm chậm'), w)
    assert w.ban('skill:linhx-chuan') == '1.0.0'
    assert af.doc(p) == cu
    log = af.doc_dong(w.p('phat-hanh', 'CHANGELOG.jsonl'))
    assert [x['den'] for x in log] == ['1.1.0', '1.0.0']


def test_lui_workflow_mot_file(w):
    af.luu_ban(w, 'workflow:viec-chung', '1.0.0')
    k = w.kenh(); k['workflow:viec-chung'] = {'production': '1.1.0', 'truoc': ['1.0.0']}
    af.ghi_json(w.p('phat-hanh', 'kenh.json'), k)
    p = w.p('workflow', 'viec-chung.json'); cu = af.doc(p)
    af.ghi(p, cu.replace('"tran_phut": 40', '"tran_phut": 99'))
    af.lenh_lui(N(dich='workflow:viec-chung', ly_do=None), w)
    assert af.doc(p) == cu


def test_lenh_chat_quyen_trong_code(w):
    L = lambda tu, tin: af.lenh_lenh(N(tu=tu, tin=tin), w)
    assert L('nguoi-la', '/giao viec-chung làm hộ') is None, 'người lạ thì im'
    assert L('an', 'chào Nụ') is None, 'không phải lệnh thì để bên trả lời nhanh'
    assert L('an', '/giao viec-chung Soạn thư mời') == 'Em nhận, mã LX-0001'
    assert 'Chưa có workflow' in L('an', '/giao khong-co việc')
    assert 'quyền' in L('an', '/duyet LX-0001')
    chuyen(w, 'LX-0001', 'dang_lam'); lam_xong_buoc(w, 'LX-0001'); chuyen(w, 'LX-0001', 'cho_duyet')
    assert L('hang', '/tra LX-0001 thiếu ngày giờ') == 'LX-0001: đã trả lại'
    assert L('an', '/gopy LX-0001 thư nên ngắn hơn').startswith('Em ghi bài học')
    assert 'LX-0001' in L('an', '/bang')
    ra = af.doc_dong(w.p('hop-thu', 'ra.jsonl'))
    assert any('bị trả lại' in x['noi_dung'] and x['cho'] == 'an' for x in ra)


def test_nho_co_tran(w):
    af.lenh_nho(N(noi_dung='Khách gọi là bạn'), w)
    with pytest.raises(af.Loi, match='vượt'):
        af.lenh_nho(N(noi_dung='x' * 2300), w)


def test_kiem_bat_loi(w):
    tc = af.doc_json(w.p('to-chuc.json'))
    tc['cong_nhan'][1]['chiu_trach_nhiem'] = 'truong'
    tc['cong_nhan'][0]['bao_cao_cho'] = 'cham'
    tc['cong_nhan'][1]['bao_cao_cho'] = 'truong'
    af.ghi_json(w.p('to-chuc.json'), tc)
    af.ghi(w.p('01-nguon', 'ghi-chu.md'), 'khoá sk-ant-' + 'a' * 30)
    af.ghi(w.p('01-nguon', 'mat.env'), 'X=1')
    loi = af.kiem(af.WF(w.goc))
    s = '\n'.join(loi)
    assert 'chiu_trach_nhiem phải là người thật' in s
    assert 'vòng báo cáo' in s
    assert 'giống khoá API' in s and 'file bí mật' in s


def test_dong_goi_va_mot_file(w, tmp_path):
    ma = giao(w)
    z = str(tmp_path / 'goi.zip'); m = str(tmp_path / 'GOI.md')
    af.lenh_dong_goi(N(thu_muc=w.goc, ra=z, kem_viec=False, mot_file=m))
    ten = zipfile.ZipFile(z).namelist()
    assert 'af.py' in ten and 'AGENTS.md' in ten and '.agents/skills/linhx-chuan/SKILL.md' in ten
    assert not any(x.startswith('viec/' + ma) for x in ten), 'mặc định không kèm việc đang chạy'
    g = af.doc(m)
    assert 'Hiến chương' in g and 'viec-chung' in g and 'linhx-chuan' in g


def test_goi_giai_nen_chay_duoc(w, tmp_path):
    """Gói zip tự đủ: giải nén ở chỗ khác, chạy af.py trong đó vẫn kiem DAT và giao được việc."""
    z = str(tmp_path / 'goi.zip')
    af.lenh_dong_goi(N(thu_muc=w.goc, ra=z, kem_viec=False, mot_file=None))
    d = tmp_path / 'giai'
    zipfile.ZipFile(z).extractall(d)
    r = subprocess.run([sys.executable, str(d / 'af.py'), 'kiem', str(d)], capture_output=True, text=True)
    assert r.stdout.startswith('DAT'), r.stdout + r.stderr
    r = subprocess.run([sys.executable, str(d / 'af.py'), 'giao', str(d), '--workflow', 'viec-chung', '--viec', 'x'],
                       capture_output=True, text=True)
    assert r.stdout.strip() == 'LX-0001', r.stderr


def test_mau_ifagent_event_dat(tmp_path):
    """Mẫu trong repo không kèm skill; chép ra, nạp skill từ kho, phải kiem DAT và giao được cả 5 workflow."""
    import shutil
    nguon = os.path.join(GOC, 'workforce', 'mau', 'ifagent-event')
    d = str(tmp_path / 'ifa')
    shutil.copytree(nguon, d)
    w = af.WF(d)
    nap = af.lenh_nap_skill(N(kho=os.path.join(GOC, 'skills')), w)
    assert 'skill:proposal-studio' in nap or os.path.exists(w.p('.agents', 'skills', 'proposal-studio', 'SKILL.md'))
    assert af.kiem(w) == []
    for t in w.ds_workflow():
        af.lenh_giao(N(workflow=t, viec='thử ' + t, nguoi_giao='sales'), w)
    assert len(w.ds_viec()) == 5
    ma = next(v['ma'] for v in w.ds_viec() if v['workflow'] == 'tra-ho-so')
    assert 'dưới 60 giây' in af.doc(w.p('viec', ma, 'TASK.md')), 'bài học từ lần thử 1 phải vào TASK của việc tra-ho-so'
