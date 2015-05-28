from __future__ import print_function

import json
import os
import time

import matplotlib.pyplot as plt

from ipy_client_usage.view import setup_axes, update_job_artists


mpl_interrupted_exception = []
try:
    import Tkinter
    mpl_interrupted_exception.append(Tkinter.TclError)
except ImportError:
    pass
mpl_interrupted_exception = tuple(mpl_interrupted_exception)


def watch_dump(fname, frequency=0.1):
    fig = plt.figure()
    ax = setup_axes(fig)

    # Keep track of whether the figure has been closed. We do this by
    # attaching an attribute to the figure, and updating it based on a
    # mpl close_event.
    def handle_close(evt):
        evt.canvas.figure.closed = True

    fig.closed = False
    fig.canvas.mpl_connect('close_event', handle_close)

    plt.show(block=False)

    artists, engines = None, None
    last_mtime = 0

    while not fig.closed:
        mtime_now = os.path.getmtime(fname)

        if mtime_now != last_mtime:
            last_mtime = mtime_now

            # We allow multiple attempts to load the file in case the file
            # hasn't yet been fully written.
            n_retries = 5
            for count in range(n_retries):
                with open(fname, 'r') as fh:
                    try:
                        status = json.load(fh)
                    except ValueError:
                        if count >= n_retries:
                            print("The json file couldn't be loaded after "
                                  "{} attempts.".format(count))
                            raise
                    else:
                        break
                time.sleep(0.1)

            artists, engines = update_job_artists(ax, status, artists, engines)
            plt.draw()

        # Sleep, keeping mpl alive. Catch any backend exceptions which may be
        # raised from closing the figure (known cases: tkagg).
        try:
            plt.pause(frequency)
        except mpl_interrupted_exception:
            pass


if __name__ == '__main__':
    import argparse
    help_str = 'Watch an IPython client dump.'
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument('dump_file')
    parser.add_argument('--watch-frequency',
                        help=("The frequency to poll the file, and "
                              "potentially update the figure."),
                        type=float, default=0.25)
    args = parser.parse_args()

    watch_dump(args.dump_file, frequency=args.watch_frequency)
