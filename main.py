from api.oanda_api import OandaApi
from api.openai_api import OpenAIAnalyzer
from infrastructure.instrument_collection import instrumentCollection 
from stream_bot.stream_bot import run_bot
from stream_example.streamer import run_streamer
from db.db import DataDB
from infrastructure.collect_data import run_collection
from analysis.openai_analysis import ForexOpenAIAnalysis


def db_tests():
    d = DataDB()

    #d.add_one(DataDB.SAMPLE_COLL, dict(age=12, name='paddy', street='elm'))
    #print(d.query_single(DataDB.SAMPLE_COLL, age=34))
    print(d.query_distinct(DataDB.SAMPLE_COLL, 'age'))

def openai_analysis_demo():
    """
    Demonstrate OpenAI analysis capabilities
    """
    try:
        print("=== OpenAI Analysis Demo ===")
        
        # Initialize the analysis system
        analyzer = ForexOpenAIAnalysis()
        
        # Generate a comprehensive market report
        print("Generating comprehensive market report...")
        report = analyzer.comprehensive_market_report(
            currency_pairs=['EUR_USD', 'GBP_USD', 'USD_JPY'],
            include_news=True,
            analysis_types=['general', 'technical']
        )
        
        if 'error' not in report:
            print(f"✅ Report generated at: {report['timestamp']}")
            
            # Display key insights from each analysis
            for analysis_name, analysis_data in report['analyses'].items():
                print(f"\n--- {analysis_name.upper().replace('_', ' ')} ---")
                if 'error' in analysis_data:
                    print(f"❌ Error: {analysis_data['error']}")
                else:
                    # Extract key insights (first 200 characters)
                    if 'analysis' in analysis_data:
                        content = analysis_data['analysis'][:200] + "..."
                        print(f"Analysis: {content}")
                    elif 'strategy' in analysis_data:
                        content = analysis_data['strategy'][:200] + "..."
                        print(f"Strategy: {content}")
        else:
            print(f"❌ Error generating report: {report['error']}")
            
    except Exception as e:
        print(f"❌ Error in OpenAI analysis demo: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable")

if __name__ == '__main__':
    api = OandaApi()    
    instrumentCollection.LoadInstruments("./data")
    # instrumentCollection.CreateDB(api.get_account_instruments())
    # instrumentCollection.LoadInstrumentsDB()
    # print(instrumentCollection.instruments_dict)
    # d = DataDB()
    # d.test_connection()
    # db_tests()
    
    # Uncomment the following line to run OpenAI analysis demo
    # openai_analysis_demo()
    
    run_collection(instrumentCollection, api)
    # print(api.get_account_instruments())
