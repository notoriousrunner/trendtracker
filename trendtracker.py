import pandas as pd
import streamlit as st
from pytrends.request import TrendReq
import requests  # Per API extra, es. Reddit/TikTok proxy

pytrends = TrendReq(hl='it-IT', tz=60)  # Locale Italia/CH

def get_google_trends(keywords, days=7):
    pytrends.build_payload(keywords, timeframe=f'today {days}d')
    df_interest = pytrends.interest_over_time()
    if not df_interest.empty:
        velocity = df_interest[keywords[0]].iloc[-1] / df_interest[keywords[0]].iloc[0] if len(df_interest) > 1 else 1
        breakout = 'YES' if velocity > 2 else 'NO'
        return {'velocity': velocity, 'breakout': breakout}
    return {'velocity': 0, 'breakout': 'NO'}

def check_reddit_trend(keyword):
    # Proxy semplice Reddit (usa PRAW per full)
    url = f"https://www.reddit.com/search.json?q={keyword}&sort=new&limit=10"
    r = requests.get(url, headers={'User-Agent': 'TrendBot'})
    posts = r.json()['data']['children']
    new_posts = len([p for p in posts if 'created_utc' in p['data']])
    return 'YES' if new_posts > 5 else 'NO'  # Soglia arbitraria

def main():
    st.title("Trend Tracker per Side Hustle")
    keywords = st.text_input("Inserisci keyword/trend (es. 'pet rock moderno')").split(',')
    keywords = [k.strip() for k in keywords]
    
    if st.button('Analizza'):
        results = []
        for kw in keywords:
            gt = get_google_trends([kw])
            reddit = check_reddit_trend(kw)
            signals = sum([gt['breakout']=='YES', reddit=='YES'])  # Aggiungi altri
            alert = '🚨 ALERT' if signals >= 2 else 'OK'
            results.append({'Keyword': kw, 'GT Velocity': gt['velocity'], 'GT Breakout': gt['breakout'],
                           'Reddit Hot': reddit, 'Signals': signals, 'Alert': alert})
        
        df = pd.DataFrame(results)
        st.dataframe(df)
        st.bar_chart(df.set_index('Keyword')['Signals'])
        
        # Salva CSV
        df.to_csv('trend_alerts.csv', index=False)
        st.download_button('Scarica CSV', 'trend_alerts.csv')

if __name__ == "__main__":
    main()
