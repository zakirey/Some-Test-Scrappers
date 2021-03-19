from requests_html import HTML, HTMLSession, AsyncHTMLSession
import requests


class TipicoApi():
    def __init__(self):
        self.session = HTMLSession()
        self.sports = {"basketball": "2101"}

    def get_events(self, name):
        data = {}
        sport_data = []
        league_data = []
        league_names = []
        r = self.session.get('https://sports.tipico.com/en/all/' + self.sports[name])
        r.html.render()
        events = r.html.find('.EventRow-styles-event-row')
        first = True
        current_league = None
        league_dict = {}
        for event in events:
            attrs_dict = event.attrs
            event_id = str(attrs_dict["href"]).split("?")[0].split('/')[-1]
            s_r = requests.get("https://sports.tipico.de/json/services/event/" + event_id)
            event_json = s_r.json()
            if not event_json['event']['live']:
                league_name = event_json['event']['group'][0]
                league_country = event_json['event']['group'][1]
                league = league_country + ", " + league_name
                # if first:
                #     current_league = league
                #     first = False
                #     league_dict = {current_league: []}
                #
                # if current_league != league:
                #     # league_dict = {current_league: league_data}
                #     # sport_data.append(league_dict)
                #     # league_data.clear()
                #     current_league = league
                #     league_dict = {current_league: []}
                team1 = event_json['event']['team1']
                team2 = event_json['event']['team2']
                event_date = event_json['event']['startDate']
                if list(event_json['categoryOddGroupMap'].keys())[0] == '0':
                    odd_group = event_json['categoryOddGroupMap']['0'][0]
                    winner_bet_id = event_json['oddGroups'][str(odd_group)]
                    if winner_bet_id["caption"] == 'Tipp':
                        group_results = event_json["oddGroupResultsMap"][str(odd_group)]
                        if len(group_results) == 2:
                            odd1_id = group_results[0]
                            odd2_id = group_results[1]
                            team1_odd = event_json['results'][str(odd1_id)]['quoteFloatValue']
                            team2_odd = event_json['results'][str(odd2_id)]['quoteFloatValue']
                            event_data = {"event_id": event_id,
                                          "teams": [team1, team2],
                                          "commence_time": event_date,
                                          "odds": {"winner": [team1_odd, team2_odd], "odd_ids": [odd1_id, odd2_id]},
                                          "site": "Tipico"
                                          }
                            # league_data.append(event_data)
                            if league not in league_names:
                                league_names.append(league)
                                league_dict = {league: []}
                                league_dict[league].append(event_data)
                            else:
                                league_dict[league].append(event_data)
                            league_dict[league].append(event_data)
        sport_data.append(league_dict)
        data[name] = sport_data
        print(data)


if __name__ == "__main__":
    api = TipicoApi()
    api.get_events("basketball")
