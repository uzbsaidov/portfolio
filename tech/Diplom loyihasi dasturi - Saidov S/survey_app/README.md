<<<<<<< HEAD
# So'rovnoma Tahlil Tizimi
## Diplom loyihasi – Saidov Suhrob Alisherovich, TDTU 178-22

---

## O'rnatish va ishga tushirish

### 1. Python va kutubxonalar
```bash
# Python 3.10+ talab qilinadi
pip install -r requirements.txt
```

### 2. Ilovani ishga tushirish
```bash
python app.py
```

### 3. Brauzerda ochish
```
http://localhost:5000
```

### 4. Login
- Foydalanuvchi nomi: `admin`
- Parol: `admin123`

---

## Foydalanish

1. **Fayl yuklash** → CSV yoki Excel faylni yuklang
2. **Maqsad ustun** tanlab (ixtiyoriy, klassifikatsiya uchun)
3. **Tahlilni boshlash** → tugmasini bosing
4. **Natijalar** sahifasida ko'ring:
   - Random Forest klassifikatsiya natijalari
   - K-means klaster taqsimoti
   - VADER sentiment tahlili
   - Interaktiv grafiklar

---

## Deployment

Bu loyiha Flask backend bilan to‘liq to‘plamdir. Netlify faqat statik saytlarni bevosita joylashtiradi, shuning uchun to‘liq ilova uchun quyidagi xizmatlardan birini tanlang:

- Render: https://render.com
- Railway: https://railway.app
- Fly.io: https://fly.io

### Render uchun tayyorlash
1. `requirements.txt` faylini saqlang.
2. `Procfile` va `runtime.txt` qo‘shildi.
3. Render-da yangi Python Web Service yarating va GitHub reponi ulang.

> Agar faqat frontend sahifani Netlify-ga joylashtirmoqchi bo‘lsangiz, backend API uchun boshqa xizmatdan URL oling va `index.html` ichidagi `fetch('/api/...')` chaqiruvlarini to‘g‘ri domenga yo‘naltiring.

---

## Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | Python 3.10, Flask 2.3 |
| ML | scikit-learn (Random Forest, K-means) |
| NLP | vaderSentiment 3.3 |
| Frontend | HTML5, Bootstrap 5.3, Chart.js 4.4 |
| DB | SQLite |

---

## Loyiha tuzilmasi

```
survey_app/
├── app.py                  ← Asosiy Flask ilovasi
├── requirements.txt
├── survey.db               ← SQLite (avtomatik yaratiladi)
├── models/
│   ├── classifier.py       ← Random Forest
│   ├── clustering.py       ← K-means
│   └── sentiment.py        ← VADER
├── utils/
│   └── preprocessor.py     ← Ma'lumotlar tayyorlash
├── database/
│   └── db_manager.py       ← SQLite manager
└── templates/
    └── index.html          ← Frontend (SPA)
```

