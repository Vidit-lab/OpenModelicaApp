"""Reader for OpenModelica binary result files (Atrajectory v1.1, 'binTrans').

scipy.io.loadmat hands these back raw, and two things make the raw form
unreadable:

* `name` / `description` are char matrices stored TRANSPOSED, so a plain
  loadmat yields one string per *character position* ('tttddtttt...') rather
  than one per variable.
* values live in two matrices -- `data_1` (constants, 2 samples) and `data_2`
  (trajectories) -- and `dataInfo` maps each name onto (matrix, row), where a
  negative row means "negate this row" (alias variables).
"""

import numpy as np
from scipy.io import loadmat


def _names(chars):
    """Transposed, null-padded char matrix -> one string per variable."""
    return [''.join(col).split('\x00')[0].strip() for col in np.asarray(chars).T]


def read_mat(path):
    """Return {variable_name: values}, every array on the same time grid.

    Parameters are broadcast to the time grid so callers never special-case
    them. 'time' is always present.
    """
    mat = loadmat(str(path), chars_as_strings=False)
    layout = ''.join(mat['Aclass'][3]).strip('\x00 ')
    if layout != 'binTrans':
        raise ValueError(f"unsupported result layout {layout!r}; expected 'binTrans'")

    info = mat['dataInfo']
    steps = mat['data_2'].shape[1]

    out = {}
    for i, name in enumerate(_names(mat['name'])):
        matrix, row = info[0, i], info[1, i]
        if matrix == 1:  # parameter / constant, stored as [start, stop]
            values = np.full(steps, mat['data_1'][abs(row) - 1, 0])
        else:
            values = mat['data_2'][abs(row) - 1]
        out[name] = -values if row < 0 else values
    return out


if __name__ == '__main__':
    from pathlib import Path

    v = read_mat(Path(__file__).resolve().parent.parent / 'bin' / 'TwoConnectedTanks_res.mat')

    t = v['time']
    assert t[0] == 0 and np.all(np.diff(t) >= 0), 'time axis is not sorted from zero'
    assert v['tank1.A'].std() == 0, 'parameter did not broadcast as a constant'

    # every alias of the connector must resolve to the same trajectory
    flow = ['tank1.Qo', 'tank1.flowConnect.F', 'tank2.flowConnect.F', 'tank2.Q1']
    for name in flow[1:]:
        assert np.array_equal(v[name], v[flow[0]]), f'alias {name} does not match {flow[0]}'

    # dataInfo row mapping is right only if der(h) really is dh/dt.
    # Events are written as two samples sharing one timestamp -- drop those.
    keep = np.r_[True, np.diff(t) > 0]
    for h in ['tank1.h', 'tank2.h']:
        numeric = np.gradient(v[h][keep], t[keep])
        assert np.allclose(numeric, v[f'der({h})'][keep], atol=1e-6), f'der({h}) does not match d{h}/dt'

    print(f'ok: {len(v)} variables, {len(t)} samples, t={t[0]}..{t[-1]}')
