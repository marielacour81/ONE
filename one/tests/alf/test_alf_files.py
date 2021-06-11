import unittest
import tempfile
from pathlib import Path
import shutil

import one.alf.files as files


class TestsAlfPartsFilters(unittest.TestCase):

    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.gettempdir()) / 'iotest'
        self.tmpdir.mkdir(exist_ok=True)

    def test_filter_by(self):
        file_names = [
            'noalf.file',
            '_ibl_trials.intervals.npy',
            '_ibl_trials.intervals_bpod.csv',
            'wheel.position.npy',
            'wheel.timestamps.npy',
            'wheelMoves.intervals.npy',
            '_namespace_obj.attr_timescale.raw.v12.ext']

        for f in file_names:
            (self.tmpdir / f).touch()

        # Test filter with None; should return files with no non-standard timescale
        alf_files, _ = files.filter_by(self.tmpdir, timescale=None)
        expected = [
            'wheel.position.npy',
            'wheel.timestamps.npy',
            'wheelMoves.intervals.npy',
            '_ibl_trials.intervals.npy']
        self.assertCountEqual(alf_files, expected, 'failed to filter with None attribute')

        # Test filtering by object; should return only 'wheel' ALF objects
        alf_files, parts = files.filter_by(self.tmpdir, object='wheel')
        expected = ['wheel.position.npy', 'wheel.timestamps.npy']
        self.assertCountEqual(alf_files, expected, 'failed to filter by object')
        self.assertEqual(len(alf_files), len(parts))

        # Test wildcards; should return 'wheel' and 'wheelMoves' ALF objects
        alf_files, _ = files.filter_by(self.tmpdir, object='wh*')
        expected = ['wheel.position.npy', 'wheel.timestamps.npy', 'wheelMoves.intervals.npy']
        self.assertCountEqual(alf_files, expected, 'failed to filter with wildcard')

        # Test filtering by specific timescale; test parts returned
        alf_files, parts = files.filter_by(self.tmpdir, timescale='bpod')
        expected = ['_ibl_trials.intervals_bpod.csv']
        self.assertEqual(alf_files, expected, 'failed to filter by timescale')
        expected = ('ibl', 'trials', 'intervals', 'bpod', None, 'csv')
        self.assertTupleEqual(parts[0], expected)
        self.assertEqual(len(parts[0]), len(files.ALF_EXP.groupindex))
        self.assertEqual(parts[0][files.ALF_EXP.groupindex['timescale'] - 1], 'bpod')

        # Test filtering multiple attributes; should return only trials intervals
        alf_files, _ = files.filter_by(self.tmpdir, attribute='intervals', object='trials')
        expected = ['_ibl_trials.intervals.npy', '_ibl_trials.intervals_bpod.csv']
        self.assertCountEqual(alf_files, expected, 'failed to filter by multiple attribute')

        # Test returning only ALF files
        alf_files, _ = files.filter_by(self.tmpdir)
        self.assertCountEqual(alf_files, file_names[1:], 'failed to return ALF files')

        # Test return empty
        out = files.filter_by(self.tmpdir, object=None)
        self.assertEqual(out, ([], []))

        # Test extras
        alf_files, _ = files.filter_by(self.tmpdir, extra='v12')
        expected = ['_namespace_obj.attr_timescale.raw.v12.ext']
        self.assertEqual(alf_files, expected, 'failed to filter extra attributes')

        alf_files, _ = files.filter_by(self.tmpdir, extra=['v12', 'raw'])
        expected = ['_namespace_obj.attr_timescale.raw.v12.ext']
        self.assertEqual(alf_files, expected, 'failed to filter extra attributes as list')

        alf_files, _ = files.filter_by(self.tmpdir, extra=['foo', 'v12'])
        self.assertEqual(alf_files, [], 'failed to filter extra attributes')

        # Assert kwarg validation; should raise TypeError
        with self.assertRaises(TypeError):
            files.filter_by(self.tmpdir, unknown=None)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir)


class TestAlfParse(unittest.TestCase):
    def test_filename_parts(self):
        verifiable = files.filename_parts('_namespace_obj.times_timescale.extra.foo.ext')
        expected = ('namespace', 'obj', 'times', 'timescale', 'extra.foo', 'ext')
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('spikes.clusters.npy', as_dict=True)
        expected = {
            'namespace': None,
            'object': 'spikes',
            'attribute': 'clusters',
            'timescale': None,
            'extra': None,
            'extension': 'npy'}
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('spikes.times_ephysClock.npy')
        expected = (None, 'spikes', 'times', 'ephysClock', None, 'npy')
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('_iblmic_audioSpectrogram.frequencies.npy')
        expected = ('iblmic', 'audioSpectrogram', 'frequencies', None, None, 'npy')
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('_spikeglx_ephysData_g0_t0.imec.wiring.json')
        expected = ('spikeglx', 'ephysData_g0_t0', 'imec', None, 'wiring', 'json')
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('_spikeglx_ephysData_g0_t0.imec0.lf.bin')
        expected = ('spikeglx', 'ephysData_g0_t0', 'imec0', None, 'lf', 'bin')
        self.assertEqual(expected, verifiable)

        verifiable = files.filename_parts('_ibl_trials.goCue_times_bpod.csv')
        expected = ('ibl', 'trials', 'goCue_times', 'bpod', None, 'csv')
        self.assertEqual(expected, verifiable)

        with self.assertRaises(ValueError):
            files.filename_parts('badfile')
        verifiable = files.filename_parts('badfile', assert_valid=False)
        self.assertFalse(any(verifiable))

    def test_rel_path_parts(self):
        alf_str = 'collection/#revision#/_namespace_obj.times_timescale.extra.foo.ext'
        verifiable = files.rel_path_parts(alf_str)
        expected = ('collection', 'revision', 'namespace', 'obj', 'times',
                    'timescale', 'extra.foo', 'ext')
        self.assertEqual(expected, verifiable)

        verifiable = files.rel_path_parts('spikes.clusters.npy', as_dict=True)
        expected = {
            'collection': None,
            'revision': None,
            'namespace': None,
            'object': 'spikes',
            'attribute': 'clusters',
            'timescale': None,
            'extra': None,
            'extension': 'npy'}
        self.assertEqual(expected, verifiable)

        with self.assertRaises(ValueError):
            files.rel_path_parts('bad/badfile')
        verifiable = files.filename_parts('bad/badfile', assert_valid=False)
        self.assertFalse(any(verifiable))


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
