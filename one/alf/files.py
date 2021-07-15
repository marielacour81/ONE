"""
Module for identifying and parsing ALF file names.

An ALF file has the following components (those in brackets are optional):
    (_namespace_)object.attribute(_timescale)(.extra.parts).ext

Note the following:
    Object attributes may not contain an underscore unless followed by 'times' or 'intervals'.
    A namespace must not contain extra underscores (i.e. `name_space` and `__namespace__` are not
    valid)
    ALF files must always have an extension

For more information, see the following documentation:
    https://int-brain-lab.github.io/iblenv/one_docs/one_reference.html#alf  # FIXME Change link

Created on Tue Sep 11 18:06:21 2018

@author: Miles
"""
import os
from fnmatch import fnmatch
from collections import OrderedDict
from datetime import datetime
from typing import Union, Optional
from pathlib import Path
import logging

from . import spec
from .spec import SESSION_SPEC, COLLECTION_SPEC, FILE_SPEC, REL_PATH_SPEC

_logger = logging.getLogger(__name__)


def filter_by(alf_path, **kwargs):
    """
    Given a path and optional filters, returns all ALF files and their associated parts. The
    filters constitute a logical AND.

    Parameters
    ----------
    alf_path : str, pathlib.Path
        A path to a folder containing ALF datasets
    object : str
        Filter by a given object (e.g. 'spikes')
    attribute : str
        Filter by a given attribute (e.g. 'intervals')
    extension : str
        Filter by extension (e.g. 'npy')
    namespace : str
        Filter by a given namespace (e.g. 'ibl') or None for files without one
    timescale : str
        Filter by a given timescale (e.g. 'bpod') or None for files without one
    extra : str, list
        Filter by extra parameters (e.g. 'raw') or None for files without extra parts
        NB: Wild cards not permitted here.

    Returns
    -------
    alf_files : str
        A Path to a directory containing ALF files
    attributes : list of dicts
        A list of parsed file parts

    Examples
    --------
    # Filter files with universal timescale
    filter_by(alf_path, timescale=None)

    # Filter files by a given ALF object
    filter_by(alf_path, object='wheel')

    # Filter using wildcard, e.g. 'wheel' and 'wheelMoves' ALF objects
    filter_by(alf_path, object='wh*')

    # Filter all intervals that are in bpod time
    filter_by(alf_path, attribute='intervals', timescale='bpod')
    """
    alf_files = [f for f in os.listdir(alf_path) if spec.is_valid(f)]
    attributes = [filename_parts(f, as_dict=True) for f in alf_files]

    if kwargs:
        # Validate keyword arguments against regex group names
        invalid = kwargs.keys() - spec.regex(FILE_SPEC).groupindex.keys()
        if invalid:
            raise TypeError("%s() got an unexpected keyword argument '%s'"
                            % (__name__, set(invalid).pop()))

        # Ensure 'extra' input is a list; if str split on dot
        if 'extra' in kwargs and isinstance(kwargs['extra'], str):
            kwargs['extra'] = kwargs['extra'].split('.')

        # Iterate over ALF files
        for file, attr in zip(alf_files.copy(), attributes.copy()):
            for k, v in kwargs.items():  # Iterate over attributes
                if v is None or attr[k] is None:
                    # If either is None, both should be None to match
                    match = v is attr[k]
                elif k == 'extra':
                    # Check all provided extra fields match those in ALF
                    match = all(elem in attr[k].split('.') for elem in v if elem)
                else:
                    # Check given attribute matches, allowing wildcards
                    match = fnmatch(attr[k], v)

                if not match:  # Remove file from list and move on to next file
                    alf_files.remove(file)
                    attributes.remove(attr)
                    break

    return alf_files, [tuple(attr.values()) for attr in attributes]


def rel_path_parts(rel_path, as_dict=False, assert_valid=True):
    """Parse a relative path into the relevant parts.  A relative path follows the pattern
    (collection/)(#revision#/)_namespace_object.attribute_timescale.extra.extension

    Parameters
    ----------
    rel_path : str
        A relative path string
    as_dict : bool
        If true, an OrderedDict of parts are returned with the keys ('lab', 'subject', 'date',
        'number'), otherwise a tuple of values are returned
    assert_valid : bool
        If true a ValueError is raised when the session cannot be parsed, otherwise an empty
        dict of tuple of Nones is returned

    Returns
    -------
        An OrderedDict if as_dict is true, or a tuple of parsed values
    """
    compiled = spec.regex(REL_PATH_SPEC)
    if hasattr(rel_path, 'as_posix'):
        rel_path = rel_path.as_posix()
    match = compiled.match(rel_path)  # py 3.8
    if match:
        return OrderedDict(**match.groupdict()) if as_dict else tuple(match.groupdict().values())
    elif assert_valid:
        raise ValueError('Invalid relative path')
    else:
        parts = compiled.groupindex.keys()
        return OrderedDict.fromkeys(parts) if as_dict else tuple([None] * len(parts))


def session_path_parts(session_path: str, as_dict=False, assert_valid=True):
    """Parse a session path into the relevant parts

    Parameters
    ----------
    session_path : str
        A session path string
    as_dict : bool
        If true, an OrderedDict of parts are returned with the keys ('lab', 'subject', 'date',
        'number'), otherwise a tuple of values are returned
    assert_valid : bool
        If true a ValueError is raised when the session cannot be parsed, otherwise an empty
        dict of tuple of Nones is returned

    Returns
    -------
        An OrderedDict if as_dict is true, or a tuple of parsed values
    """
    parsed = spec.regex(SESSION_SPEC).search(session_path)
    if parsed:
        return OrderedDict(**parsed.groupdict()) if as_dict else (*parsed.groupdict().values(),)
    elif assert_valid:
        raise ValueError('Invalid session path')
    empty = spec.regex(SESSION_SPEC).groupindex.keys()
    return OrderedDict.fromkeys(empty) if as_dict else tuple([None] * len(empty))


def filename_parts(filename, as_dict=False, assert_valid=True):
    """
    Return the parsed elements of a given ALF filename.

    Parameters
    ----------
    filename : str
        The name of the file
    as_dict : bool
        When true a dict of matches is returned
    assert_valid : bool
        When true an exception is raised when the filename cannot be parsed

    Returns
    -------
    namespace : str
        The _namespace_ or None if not present
    object : str
        ALF object
    attribute : str
        The ALF attribute
    timescale : str
        The ALF _timescale or None if not present
    extra : str
        Any extra parts to the filename, or None if not present
    extension : str
        The file extension

    Examples
    --------
    >>> filename_parts('_namespace_obj.times_timescale.extra.foo.ext')
    ('namespace', 'obj', 'times', 'timescale', 'extra.foo', 'ext')
    >>> filename_parts('spikes.clusters.npy', as_dict=True)
    {'namespace': None,
     'object': 'spikes',
     'attribute': 'clusters',
     'timescale': None,
     'extra': None,
     'extension': 'npy'}
    >>> filename_parts('spikes.times_ephysClock.npy')
    (None, 'spikes', 'times', 'ephysClock', None, 'npy')
    >>> filename_parts('_iblmic_audioSpectrogram.frequencies.npy')
    ('iblmic', 'audioSpectrogram', 'frequencies', None, None, 'npy')
    >>> filename_parts('_spikeglx_ephysData_g0_t0.imec.wiring.json')
    ('spikeglx', 'ephysData_g0_t0', 'imec', None, 'wiring', 'json')
    >>> filename_parts('_spikeglx_ephysData_g0_t0.imec0.lf.bin')
    ('spikeglx', 'ephysData_g0_t0', 'imec0', None, 'lf', 'bin')
    >>> filename_parts('_ibl_trials.goCue_times_bpod.csv')
    ('ibl', 'trials', 'goCue_times', 'bpod', None, 'csv')
    """
    pattern = spec.regex(FILE_SPEC)
    empty = OrderedDict.fromkeys(pattern.groupindex.keys())
    m = pattern.match(str(filename))
    if m:  # py3.8
        return OrderedDict(m.groupdict()) if as_dict else m.groups()
    elif assert_valid:
        raise ValueError(f'Invalid ALF filename: "{filename}"')
    else:
        return empty if as_dict else empty.values()


def path_parts(file_path: str) -> dict:
    pass


def folder_parts(folder_path: str) -> dict:
    pass


def _isdatetime(s: str) -> bool:
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def get_session_path(path: Union[str, Path]) -> Optional[Path]:
    """Returns the session path from any filepath if the date/number
    pattern is found"""
    if path is None:
        return
    if isinstance(path, str):
        path = Path(path)
    sess = None
    for i, p in enumerate(path.parts):
        if p.isdigit() and _isdatetime(path.parts[i - 1]):
            sess = Path().joinpath(*path.parts[:i + 1])

    return sess


def get_alf_path(path: Union[str, Path]) -> str:
    """Returns the ALF part of a path or filename
    Attempts to return the first valid part of the path, first searching for a session path,
    then relative path (collection/revision/filename), then just the filename.  If all invalid,
    None is returned.

    NB: There is no way to discern between lab/Subjects/subject/date/number and
    irrelevant/subject/date/number

    Parameters
    ----------
    path : str, pathlib.Path
        A path to parse

    Returns
    -------
    A string containing the full ALF path, session path, relative path or filename

    Examples
    --------
    get_alf_path('etc/etc/lab/subj/2021-01-21/001')
    'lab/subj/2021-01-21/001/collection/file.attr.ext'

    get_alf_path('subj/2021-01-21/001/collection/file.attr.ext')
    'file.attr.ext'

    get_alf_path('collection/file.attr.ext')
    'collection/file.attr.ext'
    """
    if not isinstance(path, str):
        path = Path(path).as_posix()
    path = path.strip('/')

    # Check if session path
    match_session = spec.regex(SESSION_SPEC).search(path)
    if match_session:
        return path[match_session.start():]

    # Check if filename / relative path (i.e. collection + filename)
    parts = path.rsplit('/', 1)
    match_filename = spec.regex(FILE_SPEC).match(parts[-1])
    if match_filename:
        return path if spec.regex(f'{COLLECTION_SPEC}{FILE_SPEC}').match(path) else parts[-1]


def add_uuid_string(file_path, uuid):
    """
    Add a UUID and an extra part to the filename of an ALF path

    Parameters
    ----------
    file_path : str, pathlib.Path
        An ALF path to add the UUID to
    uuid : str, uuid.UUID
        The UUID to add

    Returns
    -------
    A new Path object with a UUID in the filename
    """
    if isinstance(uuid, str) and not spec.is_uuid_string(uuid):
        raise ValueError('Should provide a valid UUID v4')
    uuid = str(uuid)
    # NB: Only instantiate as Path if not already a Path, otherwise we risk changing the class
    if isinstance(file_path, str):
        file_path = Path(file_path)
    name_parts = file_path.stem.split('.')
    if uuid == name_parts[-1]:
        _logger.warning(f'UUID already found in file name: {file_path.name}: IGNORE')
        return file_path
    return file_path.parent.joinpath(f"{'.'.join(name_parts)}.{uuid}{file_path.suffix}")


if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
