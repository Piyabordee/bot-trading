# AI Trading Risk Analyzer

🤖 **วิเคราะห์ความเสี่ยงการเทรดด้วย AI — One-Click Analysis**

> **เป้าหมายสุดท้าย:** ใช้ผลวิเคราะห์นี้ไปหาเงินจริงอย่างชาญฉลาด

## 🎯 เป้าหมายโปรเจกต์

สร้างระบบวิเคราะห์ความเสี่ยงแบบ **One-Click** โดยให้ AI เป็นตัวคิด:

```
📊 ข้อมูลเก่า (Historical)  +  🌐 ข้อมูลจากเน็ต (Real-time)
              │                         │
              └──────────┬──────────────┘
                         ▼
                    🤖 AI ENGINE
                    (วิเคราะห์ คำนวณ)
                         │
                         ▼
                    📝 CONFIG OUTPUT
                    ┌─────────────────┐
                    │ risk_level: ..  │ ◄─── จุดแข็งหลัก!
                    │ confidence: ..  │
                    │ factors: [...]  │
                    └─────────────────┘
                         │
                         ▼
                    🐍 PYTHON ANALYZER
                    (อ่าน config → ตอบ: เสี่ยงไหม?)
```

| ส่วน | หน้าที่ |
|-----|---------|
| **คุณ** | รวบรวม + แปลงข้อมูล (Data Pipeline) |
| **AI** | วิเคราะห์ข้อมูล → สร้าง Config |
| **โปรเจกต์นี้** | **Config System + Risk Analysis Engine** |

## 💪 จุดแข็งของโปรเจกต์

| หมวด | จุดแข็ง |
|-----|---------|
| **📝 Config Schema** | โครงสร้างมาตรฐาน AI สร้างได้ง่าย + Python อ่านเข้าใจ |
| **🔌 Config Reader** | Validation แน่นหนา — Config พังระบบบอกทันที |
| **🧠 Risk Engine** | Algorithm คำนวณ risk score ที่แม่นยำ + อธิบายได้ |
| **🏗️ Modular Design** | แยกส่วนชัดเจน — ดูแล ทดสอบ ขยายได้ง่าย |

## สถานะการพัฒนา (Development Status)

### ✅ Phase 0: Foundation (เสร็จสมบูรณ์)

พื้นฐานสำหรับการเชื่อมต่อข้อมูลและ provider:

- ✅ Data models (Bar, EquityPoint, Account, Position, Order)
- ✅ Custom exceptions สำหรับการจัดการข้อผิดพลาด
- ✅ Base Provider Interface — รองรับหลายโบรกเกอร์
- ✅ Risk Limits Module — ตรวจสอบความเสี่ยงพื้นฐาน
- ✅ MockProvider — ทดสอบได้โดยไม่ต้องใช้ API จริง
- ✅ Integration tests พร้อมใช้งาน

**สถิติการทดสอบ:**
- 49 tests passed ✅
- 89% code coverage

### 🚧 Phase 1: Config System (กำลังทำ)

ส่วนที่เป็นหัวใจของโปรเจกต์:

- [ ] Config Schema Definition
- [ ] AI → Config Output Format
- [ ] Config Validation Module
- [ ] Risk Scoring Algorithm

## ความต้องการเบื้องต้น

- Python 3.11+
- pip หรือ uv สำหรับจัดการ packages

## การเริ่มต้นอย่างรวดเร็ว

```bash
# 1. Clone repository
git clone <your-repo>
cd bot-trading

# 2. ติดตั้ง dependencies
pip install -e ".[dev]"

# 3. ตั้งค่า environment
cp .env.example .env
# แก้ไข .env ตามความต้องการ

# 4. รัน tests
pytest tests/ -v
```

## โครงสร้างโปรเจกต์

```
bot-trading/
├── src/bot_trading/
│   ├── config.py          # Configuration loader
│   ├── exceptions.py      # Custom exceptions
│   ├── providers/         # Broker adapters (Base, Alpaca, Mock)
│   ├── strategy/          # Trading strategies
│   ├── execution/         # Order execution
│   └── risk/              # Risk limits & checks
├── tests/                 # ชุดทดสอบ
│   ├── test_providers/
│   └── integration/
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
```

## การตั้งค่า

Environment variables (ดู `.env.example`):

| Variable | คำอธิบาย | ค่าเริ่มต้น |
|----------|-----------|--------------|
| `ALPACA_API_KEY` | Alpaca API key | *จำเป็น* |
| `ALPACA_API_SECRET` | Alpaca API secret | *จำเป็น* |
| `ALPACA_BASE_URL` | Alpaca base URL | `https://paper-api.alpaca.markets` |
| `MAX_POSITION_SIZE` | ขนาดออเดอร์สูงสุดต่อครั้ง | `1000` |
| `MAX_PORTFOLIO_EXPOSURE` | สัดส่วน exposure สูงสุด | `0.2` |
| `DAILY_LOSS_LIMIT` | ขีดจำกัดการขาดทุนรายวัน | `500` |

## Roadmap

### Phase 0: Foundation ✅
- [x] Data models (Bar, EquityPoint, Account, Position, Order)
- [x] Custom exceptions
- [x] Base Provider Interface
- [x] Risk Limits Module
- [x] MockProvider
- [x] Integration tests

### Phase 1: Config System (Current)
- [ ] Config Schema Definition
- [ ] AI → Config Output Format
- [ ] Config Validation Module
- [ ] Risk Scoring Algorithm

### Phase 2: AI Integration
- [ ] AI Engine Connector
- [ ] Data Pipeline Interface
- [ ] Real-time Analysis

### Phase 3: Production
- [ ] Live Trading Support
- [ ] Performance Dashboard
- [ ] Alert System

## License

MIT License - ดูไฟล์ LICENSE สำหรับรายละเอียด

## ข้อจำกัดความรับผิดชอบ

ซอฟต์แวร์นี้เป็นเครื่องมือช่วยวิเคราะห์ความเสี่ยง การตัดสินใจสุดท้ายในการเทรดเป็นความรับผิดชอบของผู้ใช้ อย่าเทรดด้วยเงินที่คุณไม่สามารถสูญเสียได้
