# Paper Trading Bot

บอทเทรดด้วยเงินจำลองสำหรับ **ทดสอบกลยุทธ์และการจัดการความเสี่ยง** เท่านั้น

> **⚠️ คำเตือนสำคัญ:** บอทนี้ใช้สำหรับการเทรดกระดาษ (Paper Trading) เพื่อการสาธิตเท่านั้น ไม่รองรับการเทรดจริง และไม่มีการใช้เงินจริง

## 🎯 เป้าหมายโปรเจกต์

บอทเทรดฉบับนี้ถูกสร้างขึ้นเพื่อ **เป็นสนามทดสอบที่ปลอดภัย** สำหรับ:

| เป้าหมาย | คำอธิบาย |
|----------|----------|
| **🧪 ทดสอบกลยุทธ์** | ตรวจสอบว่ากลยุทธ์การเทรดทำงานได้จริงหรือไม่ ก่อนนำไปใช้กับเงินจริง |
| **🛡️ ตรวจสอบความเสี่ยง** | ยืนยันว่าระบบควบคุมความเสี่ยง (risk controls) ทำงานถูกต้องและเข้มงวดพอ |
| **🔄 ทดสอบการดำเนินการ** | ตรวจสอบ flow การส่งออเดอร์และการจัดการตำแหน่ง (positions) ว่าราบรื่นหรือไม่ |
| **📚 เรียนรู้และทดลอง** | เป็นแหล่งศึกษาและทดลองกลยุทธ์ใหม่ๆ โดยไม่ต้องกังวลเรื่องเงิน |

**หลักการ:** เราเชื่อว่า "ทดสอบให้ดีในกระดาษ ก่อนลงสนามจริง" — กลยุทธ์ที่ผ่านการทดสอบอย่างเข้มงวดจะมีโอกาสสำเร็จในการเทรดจริงสูงกว่า

## คุณสมบัติ

- **เทรดกระดาษเท่านั้น** - ปิดการเทรดจริงโดยค่าเริ่มต้น
- **การแยก Provider** - สามารถเปลี่ยนโบรกเกอร์ได้ง่าย (รองรับ Alpaca Paper Trading เป็นหลัก)
- **การจัดการความเสี่ยง** - มีการตั้งค่าขีดจำกัดขนาดออเดอร์, การเปิดโพย์ชั่น, และการขาดทุนรายวัน
- **ป้องกันออเดอร์ซ้ำ** - ป้องกันการส่งออเดอร์ซ้ำโดยไม่ตั้งใจ
- **การออกแบบแบบโมดูล** - แยกส่วนกลยุทธ์, การดำเนินการ, ความเสี่ยง และข้อมูลออกจากกันอย่างชัดเจน

## สถานะการพัฒนา (Development Status)

### ✅ Phase 0: Foundation API (เสร็จสมบูรณ์)

พื้นฐาน API สำหรับการเชื่อมต่อ Alpaca พร้อมใช้งานแล้ว:

- ✅ โครงสร้างข้อมูล Bar และ EquityPoint สำหรับข้อมูลราคาย้อนหลัง
- ✅ Exception ที่กำหนดเองสำหรับการจัดการข้อผิดพลาด
- ✅ เมธอด `get_historical_bars()` สำหรับดึงข้อมูล OHLCV ย้อนหลัง
- ✅ เมธอด `get_order_history()` สำหรับดึงประวัติออเดอร์
- ✅ MockProvider สำหรับทดสอบโดยไม่ต้องใช้ API จริง
- ✅ Integration tests พร้อมใช้งาน

**สถิติการทดสอบ:**
- 49 tests passed ✅
- 89% code coverage (เป้าหมาย: 80%)
- 3 integration tests skipped (ต้องการ API credentials)

## ความต้องการเบื้องต้น

- Python 3.11+
- pip หรือ uv สำหรับจัดการ packages

## การเริ่มต้นอย่างรวดเร็ว

1. **ติดตั้ง dependencies:**

```bash
git clone <your-repo>
cd bot-trading
pip install -e ".[dev]"
```

2. **ตั้งค่า environment:**

```bash
cp .env.example .env
# แก้ไข .env ด้วย Alpaca Paper Trading credentials ของคุณ
```

รับ credentials สำหรับเทรดกระดาษฟรีได้ที่: https://alpaca.markets/paper

3. **รัน tests:**

```bash
pytest tests/ -v
```

4. **รันบอท (paper mode):**

```bash
python -m bot_trading.main
```

## โครงสร้างโปรเจกต์

```
bot-trading/
├── src/bot_trading/
│   ├── config.py          # การโหลด configuration (PAPER เป็นค่าเริ่มต้น)
│   ├── exceptions.py      # Custom exceptions
│   ├── providers/         # Broker adapters
│   │   ├── base.py        # Abstract interface + Bar/EquityPoint models
│   │   ├── alpaca.py      # Alpaca Paper Trading (เชื่อมต่อ API จริง)
│   │   └── mock.py        # Mock provider สำหรับทดสอบ
│   ├── strategy/          # กลยุทธ์การเทรด
│   ├── execution/         # การดำเนินการส่งออเดอร์
│   └── risk/              # การจัดการความเสี่ยง
├── tests/                 # ชุดทดสอบ
│   ├── test_providers/    # ทดสอบ providers
│   └── integration/       # ทดสอบการเชื่อมต่อจริง
├── config/                # ไฟล์ configuration
├── pyproject.toml         # Project dependencies
└── README.md
```

## คำสั่งที่ใช้ได้

```bash
# ติดตั้ง dependencies
pip install -e ".[dev]"

# รัน tests ทั้งหมด
pytest tests/ -v

# รัน tests พร้อม coverage
pytest tests/ --cov=bot_trading --cov-report=html

# ตรวจสอบ code quality
ruff check src/ tests/

# จัดรูปแบบ code
ruff format src/ tests/

# รัน integration tests (ต้องมี credentials)
pytest tests/integration/ -v
```

## คุณสมบัติความปลอดภัย

- ✅ PAPER mode เป็นค่าเริ่มต้นและรองรับเท่านั้น
- ✅ ตรวจสอบ provider (ปฏิเสธ URL ที่ไม่ใช่ paper trading)
- ✅ บังคับใช้ค่า limit ความเสี่ยงก่อนทุกออเดอร์
- ✅ ตรวจจับออเดอร์ซ้ำ
- ✅ ไม่มี secrets ใน repository
- ✅ ครอบคลุม test coverage สูง

## การตั้งค่า

Environment variables (ดู `.env.example`):

| Variable | คำอธิบาย | ค่าเริ่มต้น |
|----------|-----------|--------------|
| `TRADING_MODE` | โหมดการเทรด (paper เท่านั้น) | `paper` |
| `ALPACA_API_KEY` | Alpaca API key | *จำเป็น* |
| `ALPACA_API_SECRET` | Alpaca API secret | *จำเป็น* |
| `ALPACA_BASE_URL` | Alpaca base URL | `https://paper-api.alpaca.markets` |
| `MAX_POSITION_SIZE` | ขนาดออเดอร์สูงสุดต่อครั้ง | `1000` |
| `MAX_PORTFOLIO_EXPOSURE` | สัดส่วน exposure สูงสุด | `0.2` |
| `DAILY_LOSS_LIMIT` | ขีดจำกัดการขาดทุนรายวัน | `500` |

## การทดสอบ

โปรเจกต์นี้ทำตามหลักการ TDD (Test-Driven Development) แนะนำให้รัน tests บ่อยๆ:

```bash
# รัน tests ทั้งหมด
pytest tests/ -v

# รัน test เฉพาะไฟล์
pytest tests/test_providers/test_alpaca.py -v

# รัน tests ด้วย coverage report
pytest tests/ --cov=bot_trading --cov-report=term-missing
```

## Roadmap

### Phase 0: Foundation API ✅
- [x] สร้าง data models (Bar, EquityPoint)
- [x] สร้าง custom exceptions
- [x] implement `get_historical_bars()` ใน AlpacaProvider
- [x] implement `get_order_history()` ใน AlpacaProvider
- [x] สร้าง MockProvider สำหรับทดสอบ
- [x] เขียน integration tests

### Phase 1: Technical Indicators (ถัดไป)
- [ ] สร้างโมดูล technical indicators
- [ ] เพิ่ม indicators: SMA, EMA, RSI, MACD, Bollinger Bands
- [ ] สร้าง data pipeline สำหรับคำนวณ indicators

### Phase 2: Strategy Management
- [ ] สร้าง base strategy class
- [ ] implement sample strategies
- [ ] สร้าง strategy configuration system

### Phase 3: Backtesting
- [ ] สร้าง backtesting engine
- [ ] เพิ่ม performance metrics
- [ ] สร้าง equity curve visualization

## License

MIT License - ดูไฟล์ LICENSE สำหรับรายละเอียด

## ข้อจำกัดความรับผิดชอบ

ซอฟต์แวร์นี้สร้างขึ้นเพื่อการศึกษาและการสาธิตเท่านั้น ผลการเทรดกระดาษไม่สามารถรับประกันผลลัพธ์ที่เหมือนกันในการเทรดจริงได้ อย่าเทรดด้วยเงินที่คุณไม่สามารถสูญเสียได้
