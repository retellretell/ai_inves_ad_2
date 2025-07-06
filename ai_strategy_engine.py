# ai_strategy_engine.py - 새로운 파일 추가
class AIStrategyEngine:
    def __init__(self):
        self.models = {
            'sentiment_analyzer': self._load_sentiment_model(),
            'pattern_recognizer': self._load_pattern_model(),
            'risk_predictor': self._load_risk_model()
        }
    
    def generate_ai_insights(self, market_data, portfolio):
        """다층적 AI 분석"""
        # 1. 시장 심리 분석
        sentiment_score = self._analyze_market_sentiment(market_data)
        
        # 2. 패턴 인식
        patterns = self._detect_chart_patterns(market_data)
        
        # 3. 리스크 예측
        risk_forecast = self._predict_risk_scenarios(portfolio)
        
        # 4. HyperCLOVA X와 결합
        enhanced_prompt = self._build_enhanced_prompt(
            sentiment_score, patterns, risk_forecast
        )
        
        return self._get_hyperclova_analysis(enhanced_prompt)
