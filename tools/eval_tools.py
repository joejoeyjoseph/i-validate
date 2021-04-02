# This script contains tools for the codebase.

import importlib


def get_module_class(d, c):
    """Load module m in directory d with the class name c."""

    m = importlib.import_module('.'.join([d, c]))

    return getattr(m, c)


def apply_trans(ts, modlist):
    """Apply a series of transformative modules."""

    for m in modlist:

        ts = m.apply(ts)

    return ts


def append_results(results, base, c, conf):
    """Append results before calculating metrics."""

    results.append({'truth name': base['name'],
                    'model name': c['name'],
                    'path': c['path'],
                    'location': conf['location'],
                    'var': c['var']}
                   )

    return results
