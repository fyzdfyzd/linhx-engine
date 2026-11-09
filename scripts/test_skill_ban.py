"""Test cho skill_ban.py (chay: python -m pytest scripts/test_skill_ban.py -q)."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skill_ban as sb  # noqa: E402


def _kho(tmp_path, le_fm='name: a\ndescription: "Làm A: rõ ràng"\n', bo_ver='0.2.0'):
    g = tmp_path / 'skills'
    (g / 'le' / 'a').mkdir(parents=True)
    (g / 'le' / 'a' / 'SKILL.md').write_text(f'---\n{le_fm}---\n\n# A\n', encoding='utf-8')
    (g / 'bo' / 'b' / '.claude-plugin').mkdir(parents=True)
    (g / 'bo' / 'b' / '.claude-plugin' / 'plugin.json').write_text(
        json.dumps({'name': 'b', 'version': bo_ver, 'description': 'Bộ B'}), encoding='utf-8')
    (g / 'bo' / 'b' / 'skills' / 'x').mkdir(parents=True)
    (g / 'bo' / 'b' / 'skills' / 'x' / 'SKILL.md').write_text('---\nname: x\ndescription: X\n---\n', encoding='utf-8')
    return g


def _u(g, rel):
    return next(u for u in sb.don_vi(str(g)) if u['rel'] == rel)


def _cho(tmp_path, g):
    p = tmp_path / 'marketplace.json'
    p.write_text(json.dumps(sb.sinh_marketplace(sb.don_vi(str(g))), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return str(p)


def test_dat_va_doc_ban_le_khong_co_metadata(tmp_path):
    g = _kho(tmp_path)
    u = _u(g, 'le/a')
    assert sb.ban(u) == ''
    sb.dat_ban(u, '0.1.0')
    assert sb.ban(u) == '0.1.0'
    y = sb.yaml_fm((g / 'le' / 'a' / 'SKILL.md').read_text(encoding='utf-8'))
    assert y['metadata'] == {'version': '0.1.0'} and y['description'] == 'Làm A: rõ ràng'
    sb.dat_ban(u, '0.2.0')
    assert sb.ban(u) == '0.2.0'
    assert (g / 'le' / 'a' / 'SKILL.md').read_text(encoding='utf-8').count('version:') == 1


def test_dat_ban_le_metadata_co_san_giu_khoa_khac(tmp_path):
    g = _kho(tmp_path, le_fm='name: a\ndescription: A\nmetadata:\n    tac-gia: linh\n')
    u = _u(g, 'le/a')
    sb.dat_ban(u, '1.0.0')
    y = sb.yaml_fm((g / 'le' / 'a' / 'SKILL.md').read_text(encoding='utf-8'))
    assert y['metadata'] == {'tac-gia': 'linh', 'version': '1.0.0'}


def test_tang_bo_va_changelog(tmp_path):
    g = _kho(tmp_path)
    u = _u(g, 'bo/b')
    sb.dat_ban(u, sb.tang_so(sb.ban(u), 'minor'))
    sb.them_muc_cl(u, '0.3.0', 'Thêm', ['bước mới'])
    sb.them_muc_cl(u, '0.3.1', 'Sửa', ['lỗi nhỏ'])
    assert sb.ban(u) == '0.3.0'
    assert sb.muc_cl(u, '0.3.1').endswith('- lỗi nhỏ')
    assert sb.muc_cl(u, '0.3.0').endswith('- bước mới')
    cl = (g / 'bo' / 'b' / 'CHANGELOG.md').read_text(encoding='utf-8')
    assert cl.index('[0.3.1]') < cl.index('[0.3.0]')  # muc moi o tren


def test_tang_so():
    assert sb.tang_so('0.2.9', 'patch') == '0.2.10'
    assert sb.tang_so('0.2.9', 'minor') == '0.3.0'
    assert sb.tang_so('0.2.9', 'major') == '1.0.0'
    assert sb.so('0.10.0') > sb.so('0.9.9')


def test_kiem_bat_loi(tmp_path, capsys):
    g = _kho(tmp_path, le_fm='name: a\ndescription: Làm A: hỏng YAML\n')
    rc = sb.kiem(goc=str(g), cho=str(tmp_path / 'khong-co.json'))
    out = capsys.readouterr().out
    assert rc == 1
    assert 'không đọc được YAML' in out          # description co ': ' khong boc nhay
    assert 'không phải x.y.z' in out              # le/a chua co ban
    assert 'CHANGELOG.md: thiếu mục "## [0.2.0]"' in out
    assert 'marketplace.json chưa khớp' in out


def test_kiem_xanh_khi_du(tmp_path, capsys):
    g = _kho(tmp_path)
    for u in sb.don_vi(str(g)):
        if not sb.ban(u):
            sb.dat_ban(u, '0.1.0')
        sb.them_muc_cl(u, sb.ban(u), 'Thêm', ['mốc đầu'])
    assert sb.kiem(goc=str(g), cho=_cho(tmp_path, g)) == 0, capsys.readouterr().out


def test_kiem_bao_bom(tmp_path, capsys):
    g = _kho(tmp_path)
    p = g / 'bo' / 'b' / 'skills' / 'x' / 'SKILL.md'
    p.write_text('﻿' + p.read_text(encoding='utf-8'), encoding='utf-8')
    sb.kiem(goc=str(g), cho=str(tmp_path / 'x.json'))
    assert 'BOM' in capsys.readouterr().out


def test_kiem_kho_rong_phai_do(tmp_path, capsys):
    (tmp_path / 'skills').mkdir()
    assert sb.kiem(goc=str(tmp_path / 'skills'), cho=str(tmp_path / 'x.json')) == 1
    assert 'đếm 0' in capsys.readouterr().out


def test_marketplace_le_va_bo(tmp_path):
    g = _kho(tmp_path)
    m = sb.sinh_marketplace(sb.don_vi(str(g)))
    e = {p['name']: p for p in m['plugins']}
    assert e['b']['source'] == './skills/bo/b' and e['b']['version'] == '0.2.0'
    assert e['a']['skills'] == ['./skills/le/a'] and e['a']['strict'] is False
