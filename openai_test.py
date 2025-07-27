from api.openai_api import OpenAIAnalyzer
from api.oanda_api import OandaApi
from typing import Optional


class RealTimeAnalyzer:
    """
    Real-time forex market analysis and trading signal generation.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the real-time analyzer.

        Args:
            openai_api_key: OpenAI API key
        """
        self.openai_analyzer = OpenAIAnalyzer(openai_api_key)
        self.oanda_api = OandaApi()

    def _generate_trading_signal(self) -> Optional[str]:
        """Generate trading signal using OpenAI analysis."""
        try:
            # Simple test prompt to check connection
            analysis_prompt = "Say hi"
            print(f"🔍 Sending prompt to OpenAI: {analysis_prompt}")

            # Get OpenAI analysis
            response = self.openai_analyzer.client.chat.completions.create(
                
                model=self.openai_analyzer.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful trading assistant."
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )

            result = response.choices[0].message.content.strip()
            print(f"✅ OpenAI response: {result}")
            return result

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return None
if __name__ == "__main__":
    analyzer = RealTimeAnalyzer(openai_api_key="xx")
    signal = analyzer._generate_trading_signal()
    print("Signal:", signal)
