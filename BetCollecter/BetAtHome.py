from bs4 import BeautifulSoup
from AdvanceSeleniumBrowser.ChromeBrowser import get_chromedriver
from time import time, sleep
import concurrent.futures
import pytest

MAX_THREADS = 30
s = time()


class BetAtHomeAPI:
    def __init__(self):
        self.bet_at_home = get_chromedriver()
        self.bet_at_home.get("https://www.bet-at-home.com/en/sport")
        self.sports = {"basketball": 5, "tennis": 2}
        self.bet_types = {"basketball_winner": "5422, 501", "tennis_winner": "5503, 200"}

    def get_sport(self, name):
        sport = self.bet_at_home.execute_script(r"""
        var addsport = fetch("https://www.bet-at-home.com/svc/sport/AddSport", {
          "headers": {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru,en;q=0.9,az;q=0.8",
            "content-type": "application/json;charset=UTF-8",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-bah-channel": "10",
            "x-bah-platformtype": "1",
            "x-requested-with": "XMLHttpRequest"
          },
          "referrer": "https://www.bet-at-home.com/en/sport",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body": "{\"sportId\":""" + str(self.sports[name]) + """}",
          "method": "POST",
          "mode": "cors",
          "credentials": "include"
        })
        
        return addsport;""")

    def filter_bet_type(self, name):
        bet_type = self.bet_at_home.execute_script(r"""
                    var setfilter = fetch("https://www.bet-at-home.com/svc/sport/SetSportFilterBetTypes", {
                      "headers": {
                        "accept": "application/json, text/plain, */*",
                        "accept-language": "ru,en;q=0.9,az;q=0.8",
                        "content-type": "application/json;charset=UTF-8",
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-origin",
                        "x-bah-channel": "10",
                        "x-bah-platformtype": "1",
                        "x-requested-with": "XMLHttpRequest"
                      },
                      "referrer": "https://www.bet-at-home.com/en/sport",
                      "referrerPolicy": "strict-origin-when-cross-origin",
                      "body": "{\"selectedSportFilterIds\": [5503, 200], \"selectedBetTypeGroupId\":1}",
                      "method": "POST",
                      "mode": "cors",
                      "credentials": "include"
                    })
                    return setfilter;""")

    def get_list(self):
        print_list = self.bet_at_home.execute_script(r"""
                        var print = fetch("https://www.bet-at-home.com/en/sport/print", {
                          "headers": {
                            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                            "accept-language": "ru,en;q=0.9,az;q=0.8",
                            "cache-control": "max-age=0",
                            "sec-fetch-dest": "document",
                            "sec-fetch-mode": "navigate",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-user": "?1",
                            "upgrade-insecure-requests": "1"
                          },
                          "referrer": "https://www.bet-at-home.com/en/sport",
                          "referrerPolicy": "strict-origin-when-cross-origin",
                          "body": null,
                          "method": "GET",
                          "mode": "cors",
                          "credentials": "include"
                        })
                        .then(response => response.text())
                        return print;
                        """)
        return print_list

    def bet_at_home_parser(self, game):
        data = {}
        sport_data = []
        bet_at_home.get_sport(game)
        bet_at_home.filter_bet_type("tennis_winner")
        html = bet_at_home.get_list()
        soup = BeautifulSoup(html, 'html.parser')
        league_names = soup.find_all("div", {"class": "hea ods-hea h-icon"})
        league_blocks = soup.find_all("div", {"class": "rB S22G h-bG-FFFFFF l-mb3 l-dInlineBlock l-fullWidth"})
        for league, block in zip(league_names, league_blocks):
            league_data = []
            live_counter = 0
            tbody = block.tbody
            tr = tbody.find_all("tr")
            for item in tr:
                td_class = item.td.attrs["class"]
                if len(td_class) > 2:
                    live_counter += 1
                    continue
                else:
                    td = item.find_all("td")
                    event_id = item.attrs["data-event"]
                    team1 = str(td[0].text).split(" - ")[0]
                    team2 = str(td[0].text).split(" - ")[1]
                    event_date = str(td[1].text)
                    odd1_id = str(td[2].a.attrs["id"]).strip("O_")
                    odd2_id = str(td[3].a.attrs["id"]).strip("O_")
                    team1_odd = td[2].a.text
                    team2_odd = td[3].a.text
                    event_data = {"event_id": event_id,
                                  "teams": [team1, team2],
                                  "commence_time": event_date,
                                  "odds": {"winner": [team1_odd, team2_odd], "odd_ids": [odd1_id, odd2_id]},
                                  "site": "Bet-At-Home"
                                  }
                    league_data.append(event_data)
            if live_counter == len(tr):
                continue
            else:
                league_name = league.h2.text
                league_dict = {str(league_name): league_data}
                sport_data.append(league_dict)
        data[game] = sport_data
        return data


if __name__ == "__main__":
    # bet_at_home = BetAtHomeAPI()
    # data = bet_at_home.bet_at_home_parser("tennis")
    # print(data)
    e = time()
    print(e - s)

# var = {"basketball": [
#     {"NBA": [
#         {"event_id": 20974810,
#          "teams": ["BC Avtodor Saratov", "CSKA Moscow"],
#          "commence_time": "18.01.21 16:00",
#          "odds": {"winner": ["7.60", "1.04"], "odd_ids": ["323810283_1, 323810283_2"]},
#          "site": "Bet-At-Home"
#          }
#     ]
#     }
# ]
# }


