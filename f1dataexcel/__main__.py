from f1dataexcel.f1_data_to_excel import get_f1_data
import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description='Get F1 data and save as excel file')

    parser.add_argument('year', type=int, action="store")
    parser.add_argument('-e','--event', type=str, action="store")
    parser.add_argument('-d', '--destination', action="store", default=str(pathlib.Path().resolve()))
    parser.add_argument('-n', '--no-cache', action="store_false", dest='cache') # default value is True
    args = parser.parse_args()
    print(args)
    ## location for saving data
    get_f1_data(year=args.year, data_destination=args.destination, cache=args.cache, event=args.event)

if __name__ == '__main__':
    main()