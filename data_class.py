def get_name():
        return  "player_stats.csv"
def fix_mojibake(text):
    try:
        return text.encode('latin1').decode('utf-8')
    except:
        return text
