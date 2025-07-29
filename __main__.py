from f1dataexcel.f1_data_to_excel import get_f1_data
import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description='Get F1 data and save as excel file')

    parser.add_argument('year', action="store")
    parser.add_argument('-d', '--destination', action="store", default=pathlib.Path().resolve())
    parser.add_argument('-c', '--cache', action="store_false") # default value is True
    args = parser.parse_args()
    print(args)
    ## location for saving data
    # get_f1_data(year=args.year, data_destination=args.destination, cache=args.cache)

if __name__ == '__main__':
    main()