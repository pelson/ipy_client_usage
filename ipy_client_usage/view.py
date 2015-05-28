from datetime import datetime, timedelta
import json

import matplotlib.pyplot as plt
import matplotlib.dates
import numpy as np


def plot_status(fig, status, n_engines=0):
    ax = setup_axes(fig, n_engines)
    return update_job_artists(ax, status)


def setup_axes(fig, n_engines=0):
    ax = fig.add_subplot(1, 1, 1)
    start = datetime.now() + timedelta(days=3000)

    locator = matplotlib.dates.AutoDateLocator(maxticks=8)
    ax.xaxis.set_major_locator(locator)
    fmtr = matplotlib.dates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(fmtr)

    # Plot something to put us into a sensible date frame.
    ax.plot([start, start + timedelta(seconds=1)],
            [0, n_engines or 1],
            alpha=0.)

    plt.xticks(rotation=30)

    ax.set_xmargin(0.1)
    ax.ignore_existing_data_limits = True
    ax.set_autoscale_on(True)
    return ax


def update_job_artists(ax, status,
                       existing_artists=None,
                       engine_positions=None):
    existing_artists = existing_artists or {}
    engine_positions = engine_positions or []

    for name, metadata in status.items():
        from_iso = lambda dt_str: datetime.strptime(dt_str,
                                                    "%Y-%m-%dT%H:%M:%S.%f")

        if metadata['started']:
            start = from_iso(metadata['started'])
            if metadata['completed']:
                stop = from_iso(metadata['completed'])
                message = '{}\n({}s)'.format(name, (stop - start).seconds)
            else:
                stop = from_iso(metadata['completed'])
                message = '{}\n(still working...)'.format(name)

            engine_id = metadata['engine_id']
            if engine_id not in engine_positions:
                engine_positions.append(engine_id)

            e_offset = engine_positions.index(engine_id)
            poly_x = [start, start, stop, stop, start]
            poly_y = np.array([0 + e_offset,
                               1 + e_offset,
                               1 + e_offset,
                               0 + e_offset,
                               0 + e_offset]) - 0.5

            if name in existing_artists:
                poly, text = existing_artists[name]
                poly._path.vertices[:, 0] = ax.convert_xunits(poly_x)
                text.set_text(message)
            else:
                poly, = ax.fill(poly_x, poly_y, facecolor='red', alpha=0.5)
                text = ax.text(start + (stop - start) / 2, e_offset, message,
                               va='center', ha='center')
                existing_artists[name] = [poly, text]
    return existing_artists, engine_positions


if __name__ == '__main__':
    import argparse
    help_str = 'View an IPython client dump.'
    parser = argparse.ArgumentParser(description=help_str)
    parser.add_argument('dump_file')
    args = parser.parse_args()

    with open(args.dump_file, 'r') as fh:
        status = json.load(fh)

    fig = plt.figure()
    plot_status(fig, status)
    plt.show()
