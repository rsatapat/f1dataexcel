import fastf1 as ff1
import logging
import numpy as np
import pandas as pd
import os
from datetime import datetime

## turn off unnecessary logging messages from FastF1
logging.getLogger("fastf1").setLevel(logging.WARNING)

def get_race_time(race_times):
    lead_driver_time = race_times[0]
    gaps = race_times[1:]
    gaps = np.insert(gaps,0, 0)
    final_race_times = gaps+np.ones(race_times.size)*lead_driver_time
    return np.round(final_race_times, 3)

def get_f1_data(year=2022, data_destination='', cache=True):
    if cache:
        if ff1.Cache.get_cache_info()[0]==data_destination:
            ff1.Cache.set_enabled()
            print('Cache enabled in '+data_destination)
        else:
            print('Cache enabled in '+data_destination)
            ff1.Cache.enable_cache(data_destination)
    else:
        print('Cache disabled, new data will be downloaded...')
        ff1.Cache.set_disabled()

    # get events schedule for a year
    schedule = ff1.get_event_schedule(year)

    ## dataframe for race and quali results
    season_results_summary = pd.DataFrame({'Driver':[0], 'Team':[0], 'Starting':[0], 
                                        'Finishing':[0], 'Classified':[0], 'Status':[0],
                                        'Points':[0], 'Time':[0], 'Date':[0], 'Event':[0], 'Round':[0]})
    season_quali_summary = pd.DataFrame({'Driver':[0], 'Team':[0], 'Starting':[0], 
                                        'Q1':[0], 'Q2':[0], 'Q3':[0], 'Date':[0], 'Event':[0], 'Round':[0]})

    ## iterate thorough all the races and load data
    for i, events in schedule.iterrows():
        if events['EventDate']>datetime.today():
            break
        if 'test' in events['EventFormat']:
            continue
        elif 'sprint' in events['EventFormat']:
            race = ff1.get_session(year, events['Location'], 'Race')
            sprint = ff1.get_session(year, events['Location'], 'Sprint')
            quali = ff1.get_session(year, events['Location'], 'Q')
            race.load(laps=False, weather=False, messages=False, telemetry=False, livedata=None)
            sprint.load(laps=False, weather=False, messages=False, telemetry=False, livedata=None)
            quali.load(laps=False, weather=False, messages=False, telemetry=False, livedata=None)

            if events['Session2'] == 'Sprint Qualifying':
                sprint_quali = ff1.get_session(year, events['Location'], 'Sprint Qualifying')
                sprint_quali.load(laps=True, weather=False, messages=False, telemetry=False, livedata=None)

            sprint_result=sprint.results[['Abbreviation', 'TeamName', 'GridPosition', 'Position', 
                                    'ClassifiedPosition', 'Status', 'Points']].copy()
            sprint_result.rename(columns={'Abbreviation':'Driver', 'TeamName':'Team', 'GridPosition':'Starting',
                                'Position':'Finishing', 'ClassifiedPosition':'Classified'}, inplace=True)
            sprint_result.loc[:, 'Date'] = sprint.event['Session3Date'].date().strftime('%Y-%m-%d')
            sprint_result.loc[:, 'Event'] = events['Location'] +' '+'Sprint'
            sprint_result['Time'] = get_race_time(sprint.results['Time'].apply(lambda x:x.total_seconds()).values)
            sprint_result.loc[:, 'Round'] = sprint.event['RoundNumber']
            season_results_summary = pd.concat([season_results_summary, sprint_result], ignore_index=True)

        elif 'conventional' in events['EventFormat']:
            race = ff1.get_session(year, events['Location'], 'Race')
            quali = ff1.get_session(year, events['Location'], 'Q')
            race.load(laps=False, weather=False, messages=False, telemetry=False, livedata=None)
            quali.load(laps=False, weather=False, messages=False, telemetry=False, livedata=None)

        race_result=race.results[['Abbreviation', 'TeamName', 'GridPosition', 'Position', 
                                'ClassifiedPosition', 'Status', 'Points']].copy()
        race_result.rename(columns={'Abbreviation':'Driver', 'TeamName':'Team', 'GridPosition':'Starting',
                            'Position':'Finishing', 'ClassifiedPosition':'Classified'}, inplace=True)
        race_result.loc[:, 'Date'] = race.event['Session5Date'].date().strftime('%Y-%m-%d')
        race_result.loc[:, 'Event'] = events['Location'] +' '+'Race'
        race_result['Time'] = get_race_time(race.results['Time'].apply(lambda x:x.total_seconds()).values)
        race_result.loc[:, 'Round'] = race.event['RoundNumber']
        season_results_summary = pd.concat([season_results_summary, race_result], ignore_index=True)

        if events['Session2'] == 'Sprint Qualifying':
            sprint_quali_result = sprint_quali.results[['Abbreviation', 'TeamName', 'Position', 'Q1', 'Q2']].copy()
            sprint_quali_result.rename(columns={'Abbreviation':'Driver', 'TeamName':'Team'}, inplace=True)
            ## since Ergast does not directly produce results for sprint quali, we have to do it ourselves
            sprint_quali_result['Q3'] = np.zeros(sprint_quali_result.shape[0])
            for driver in sprint_quali_result['Driver']:
                sprint_quali_result.loc[sprint_quali_result['Driver']==driver, 'Q3'] = \
                sprint_quali.laps.pick_drivers(driver).pick_fastest().LapTime.total_seconds()
            sprint_quali_result.sort_values(by=['Q3'], inplace=True, ascending=True, na_position='last')
            sprint_quali_result.loc[:, 'Position'] = np.arange(1, sprint_quali_result.shape[0]+1)
            sprint_quali_result.loc[:, 'Date'] = sprint_quali.event['Session2Date'].date().strftime('%Y-%m-%d')
            sprint_quali_result.loc[:, 'Event'] = events['Location'] +' '+'Sprint Qualifying'
            sprint_quali_result.loc[:, 'Round'] = quali.event['RoundNumber']
            season_quali_summary = pd.concat([season_quali_summary, sprint_quali_result], ignore_index=True)

        quali_result=quali.results[['Abbreviation', 'TeamName', 'Position']].copy()
        quali_result['Q1'] = quali.results['Q1'].apply(lambda x: x.total_seconds())
        quali_result['Q2'] = quali.results['Q2'].apply(lambda x: x.total_seconds())
        quali_result['Q3'] = quali.results['Q3'].apply(lambda x: x.total_seconds())
        quali_result = quali_result.copy()
        quali_result.rename(columns={'Abbreviation':'Driver', 'TeamName':'Team'}, inplace=True)
        quali_result.loc[:, 'Date'] = quali.event['Session4Date'].date().strftime('%Y-%m-%d')
        quali_result.loc[:, 'Event'] = events['Location'] +' '+'Race Qualifying'
        quali_result.loc[:, 'Round'] = quali.event['RoundNumber']
        season_quali_summary = pd.concat([season_quali_summary, quali_result], ignore_index=True)
        print(events['Location'] + ' Done')


    season_results_summary.drop(index=0, inplace=True)
    season_quali_summary.drop(index=0, inplace=True)
    event_num, _ = pd.factorize(season_quali_summary['Event'])
    season_quali_summary.loc[:, 'EventNumber'] = np.ones(event_num.shape[0])+event_num
    event_num, _ = pd.factorize(season_results_summary['Event'])
    season_results_summary.loc[:, 'EventNumber'] = np.ones(event_num.shape[0])+event_num

    with pd.ExcelWriter(os.path.join(data_destination, str(year)+' season results.xlsx')) as writer:
        season_results_summary.to_excel(writer, index=False)
    with pd.ExcelWriter(os.path.join(data_destination, str(year)+' season quali results.xlsx')) as writer:
        season_quali_summary.to_excel(writer, index=False)

    season_results_summary.to_csv(os.path.join(data_destination, str(year)+' season results.csv'), index=False)
    season_quali_summary.to_csv(os.path.join(data_destination, str(year)+' season quali results.csv'), index=False)


if __name__ == '__main__':
    import argparse
    import pathlib

    parser = argparse.ArgumentParser(description='Get F1 data and save as excel file')

    parser.add_argument('year', type=int, action="store")
    parser.add_argument('-d', '--destination', action="store", default=str(pathlib.Path().resolve()))
    parser.add_argument('-n', '--no-cache', action="store_false", dest='cache') # default value is True
    args = parser.parse_args()
    print(args)
    ## location for saving data
    get_f1_data(year=args.year, data_destination=args.destination, cache=args.cache)