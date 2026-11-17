may: may-3
phieu: ev-hieu-nang-14-sua-1
viec: Đăng nhập GitHub cho Git trên may-3 (repo https://github.com/fyzdfyzd/ifagent trả HTTP 401, máy chưa có credential GitHub/SSH/gh CLI và system gitconfig đang bật helper-selector gây treo hộp thoại GUI khi git clone/fetch)
lenh: git config --global --replace-all credential.helper ""; git config --global --add credential.helper manager; git -c credential.interactive=true ls-remote https://github.com/fyzdfyzd/ifagent refs/heads/agy/ev-de-xuat-11
gio: 2026-11-17T19:51:21+0700
