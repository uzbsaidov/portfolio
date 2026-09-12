try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

class SentimentAnalyzer:
    def __init__(self):
        if VADER_AVAILABLE:
            self.sia = SentimentIntensityAnalyzer()
        else:
            self.sia = None

    def analyze(self, texts: list) -> list:
        results = []
        for text in texts:
            text = str(text).strip()
            if not text or text == 'nan':
                continue
            if self.sia:
                scores = self.sia.polarity_scores(text)
                c = scores['compound']
                label = 'ijobiy' if c >= 0.05 else 'salbiy' if c <= -0.05 else 'neytral'
                results.append({
                    'text':     text[:100],
                    'compound': round(c, 3),
                    'pos':      round(scores['pos'], 3),
                    'neg':      round(scores['neg'], 3),
                    'neu':      round(scores['neu'], 3),
                    'label':    label
                })
            else:
                # Fallback: oddiy kalit so'z asosidagi tahlil
                pos_words = ['yaxshi','ajoyib','zo\'r','a\'lo','maqtov','baxt','xursand','rivojlanish']
                neg_words = ['yomon','qiyin','muammo','xato','noto\'g\'ri','afsus','noxush']
                text_lower = text.lower()
                pos = sum(1 for w in pos_words if w in text_lower)
                neg = sum(1 for w in neg_words if w in text_lower)
                if pos > neg:   label = 'ijobiy'
                elif neg > pos: label = 'salbiy'
                else:           label = 'neytral'
                results.append({'text': text[:100], 'compound': 0.0, 'label': label})
        return results
