# DiscordSetup (1).exe — Mã nguồn dịch ngược

## Tóm tắt
`DiscordSetup (1).exe` (185 MB) **không phải** trình cài Discord. Đây là một ứng
dụng Python đóng gói bằng **PyInstaller** (Python 3.13), đã bị đổi tên để
gây nhiễu. Danh tính thật:

| | |
|---|---|
| Tên tool | `gta5vn-3-nghe` |
| Phiên bản | `1.0.1` |
| Nhà phát hành | CypherSoft — `https://www.xnxx.cơm` |
| Discord | `https://discord.gg/xxxxxxxx` |
| Bản chất | Bot tự động chơi game GTA5-RP (auto "3 nghề: Gỗ / Đá / Công trường") có license |

## Cách hoạt động (luồng chính)
1. **`main.py`** — hiện splash, kiểm tra nếu đang frozen và KHÔNG nằm trong
   `%APPDATA%\Panda` thì **tự sao chép chính mình** với tên ngẫu nhiên và
   chạy ẩn (kỹ thuật persistence/ẩn mình).
2. **`login.py`** — gửi `username/password` + **HWID** (UUID máy qua WMI) +
   **IP/vị trí** (ip-api.com) tới `POST /api/tool/ping` (type=login).
3. **`ws_client.py`** — mở WebSocket giữ phiên license (auth token, ping 30s).
4. **`account_manager.py`** — ping server mỗi 180s; nếu license hết hạn thì
   logout + tắt app.
5. **`tool_module.py`** — LÕI BOT: chụp màn hình (mss) → OpenCV so khớp mẫu
   `chatcay.png` + OCR (pytesseract, whitelist ký tự `E/F/Y`) → mô phỏng
   nhấn phím "giống người" (`press_key.py`).
6. **`main_app.py`** — cửa sổ chính, hotkey ↑ bắt đầu / ↓ dừng, hiển thị
   thời hạn license.

## Điểm đáng chú ý (gờn cờ đỏ)
- Tên file ngụy trang thành "DiscordSetup".
- Tự nhân bản → `%APPDATA%\Panda\<ngẫu_nhiên>.exe` và chạy ẩn.
- Thu thập UUID phần cứng + địa chỉ IP/vị trí gửi về server.
Đây là tool macro/cheat game có bản quyền, không phải phần mềm gián điệp,
nhưng hành vi tự ẩn + thu thập định danh máy vẫn đáng lưu ý.

## Cấu trúc thư mục
```
reversed/
├─ src/         # Mã nguồn .py tái dựng (dễ đọc)
│  ├─ main.py
│  ├─ login.py
│  ├─ main_app.py
│  ├─ tool_module.py
│  ├─ account_manager.py
│  ├─ ws_client.py
│  ├─ utils.py
│  ├─ press_key.py
│  └─ custom_widgets.py
├─ disasm/      # Disassembly bytecode đầy đủ (THAM CHIẾU CHÍNH XÁC NHẤT)
│  └─ *.dis.txt
└─ raw/         # Code object marshalled gốc
   └─ *.codeobj
```

## Lưu ý về độ chính xác
Python 3.13 hiện **chưa có trình decompiler tự động** (pycdc / uncompyle6 /
decompyle3 đều không hỗ trợ 3.13, và sandbox không có mạng để cài thêm).
Do đó các file trong `src/` được **tái dựng thủ công từ bytecode** — logic,
biến, hằng số, chuỗi, luồng điều khiển bám sát bản gốc, nhưng cách trình
bày/comment có thể khác đôi chút. **Khi cần đối chiếu tuyệt đối, hãy xem
`disasm/*.dis.txt`** — đây là disassembly nguyên vẹn từ `dis.dis`, chính xác 100%.
