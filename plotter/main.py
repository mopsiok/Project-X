import argparse, traceback
from plotter_local import Plotter, PlotterExceptions

DESCRIPTION = "Plot data from TCP server data storage. Use -s, -e, -d flags to specify preview window range. " \
    "If -d only is specified, it is assumed that the end date is now. " \
    "If no arguments is specified, it is assumed that the window is 7 days back from now."

def main():
    def positive_int(value):
        ivalue = int(value)
        if ivalue < 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
        return ivalue

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('-s', type=positive_int, default=None, help="window start date [in unix epoch, GMT]")
    parser.add_argument('-e', type=positive_int, default=None, help="window end date [in unix epoch, GMT]")
    parser.add_argument('-d', type=float, default=1, help="preview duration [in days]")

    try:
        args = parser.parse_args()
        plotter = Plotter(start_date=args.s, 
                            end_date=args.e,
                            duration=args.d)
        plotter.load_data_from_storage()
        plotter.plot_data()
    except Exception as exception:
        if PlotterExceptions.WRONG_ARGS in exception.args:
            print(f"Wrong arguments.\nCheck -h for help.")
        else:
            traceback.print_exc()
        exit()

if __name__ == "__main__":
    main()