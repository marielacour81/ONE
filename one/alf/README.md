# ALyx Files (ALF)
ALF stands for "ALyx Files". It not a format but rather a format-neutral file-naming convention.
ALF is how IBL organizes files that will be loaded via the ONE protocol.

## Folder structure
In ALF, the measurements in an experiment are represented by collections of files in a directory.
Files should be organized in folders by subject name, date and session number, for example:
```
mouse_001/2021-05-27/001
```

Optionally the lab may also be present in the folder structure, for example:
```
lab_name/Subjects/mouse_001/2021-05-27/001
```

## Filenames

Each filename has three parts, for example `spikes.times.npy` or `spikes.clusters.npy`.
The first two correspond to the ONE dataset type, and we refer to them as the _object_ and the _attribute_.
The third part of the filename, the _extension_, specifies what physical format the file is in. 
Object, attribute and extension are each separated by a period.
For example a file called `spikes.times.npy` represents the _spikes_ object, with an _times_ attribute and an _npy_ extension.
We primarily use .npy in these examples, but you could use any format, for example video or json.

Note: in ALF, you cannot have two data files with the same object and attribute (i.e. the same dataset type).
For example, if you have `tones.frequencies.npy`, you cannot also have `tones.frequencies.tsv`.

Objects and attributes should be in Haskell case for example `sparseNoise.xyPos` but supports 
acronyms, e.g. `RFMapStim.intervals`, `ROIMotionEnergy.position`.  Underscores, hyphens and spaces are 
not supported, except with 'times', 'timestamps' and 'intervals', which have a special meaning:

```
trials.goCue_times
```

An example of full file path would be:
```
lab_name/Subjects/mouse_001/2021-05-27/001/RFMapStim.intervals
```
### Special cases on attributes

Each file contains information about particular attribute of the object.
For example `spikes.times.npy` indicates the times of spikes and `spikes.clusters.npy` indicates their cluster assignments.
You could have another file `spikes.amplitudes.npy` to convey their amplitudes.

The important thing is that **every file describing an object has the same number of rows** (i.e. the 1st dimension of an npy file, number of frames in a video file, etc). 
You can therefore think of the files for an object as together defining a table, with column headings given by the attribute in the file names, and values given by the file contents.

ALF objects can represent anything. But three types of object are special:

#### Event series

If there is a file with attribute `times`, (i.e. filename `obj.times.ext`),
it indicates that this object is an event series.
The `times` file contains a numerical array containing times of the events in seconds,
relative to a universal timescale common to all files.
Other attributes of the events are stored in different files.
If you want to represent times relative to another timescale,
do this by appending to `timescale` after an underscore (e.g. `spikes.times_ephysClock.npy`).
By convention, any other file with attribute that ends in `_times` is understood to be a time in universal seconds;
for example `trials.reward_times.npy`.
An attribute ending with `_times_timescale` is by convention a time in that timescale.

#### Interval series

If there is a file with attribute `intervals`, (i.e. filename `tones.intervals.npy`), 
it should have two columns, indicating the start and end times of each interval relative to the universal timescale. 
Again, other attributes of the events can be stored in different files (e.g. `tones.frequencies.npy`. 
Event times relative to other timescales can be represented by a file with attribute `intervals_timescale`. 
Again, any other attributes of the form `trials.cue_intervals.npy` are by convention measured in universal seconds.

#### Continuous timeseries

If there is a file with attribute `timestamps`, it indicates the object is a continuous timeseries. 
The timestamps file represents information required to synchronize the timeseries to the universal timebase, 
even if they were unevenly sampled. There are 2 possibilities:
-	The `timestamps` file contains a single column containing time of every sample within the timescale.
-	The `timestamps` file contains two rows. Each row of the `timestamps` file represents a synchronization point, with the first column giving the sample number (counting from 0), and the second column giving the corresponding time in universal seconds. The times corresponding to all samples are then found by linear interpolation. Note that the `timestamps` file is an exception to the rule that all files representing a continuous timeseries object must have one row per sample, as it will often have substantially less. Note that an evenly-sampled recording should have just two timestamps, giving the times of the first and last sample.  

### File types
ALF can deal with any sort of file, as long as it has a concept of a number of rows (or primary dimension). 
The type of file is recognized by its extension. Preferred choices:

.npy: numpy array file. This is recommended over flat binary since datatype and shape is stored in the file. If you want to name the columns, use a metadata file. If you have an array of 3 or more dimensions, the first dimension counts as the number of rows. To access npy files from MATLAB use [this](https://github.com/kwikteam/npy-matlab).

.tsv: tab-delimited text file. This is recommended over comma-separated files since text fields often have commas in. All rows should have the same number of columns. The first row contains tab-separated names for each column.

.bin: flat binary file. It's better to use .npy for storing binary data but some recording systems save in flat binary. Rather than convert them, you can ALFize a flat binary file by adding a metadata file, which specifies the number of columns (as the size of the "columns" array) and the binary datatype as a top-level key "dtype", using numpy naming conventions.


## Optional components
There are other optional parts to the file path that are used to convey other information.

### Collections
Within a session folder the data may be placed in any number of sub-folders, each one is referred to as a 
collection and these may be used to sort identical datasets by device or preprocessing software.  For 
example spikes collected on two different probes maybe in different numbered probe collections:
```
mouse_001/2021-05-27/001/probe00/spikes.times.npy
mouse_001/2021-05-27/001/probe01/spikes.times.npy
```

Perhaps for analysis the spikes were sorted using two different spike sorters, one with Kilosort, the 
other with Yass; this would be represented by a collection folder `ks2.1/` and `yass` respectively:
```
mouse_001/2021-05-27/001/probe00/ks2.1/spikes.times.npy
mouse_001/2021-05-27/001/probe01/yass/spikes.times.npy
```

### Revisions
If the data require pre-processing in a different manner, a revision folder may be used so that the 
original data is not overwritten.  This can be used as a form of versioning and should be a dated 
folder surrounded by pound signs, e.g.
```
mouse_001/2021-05-27/001/#2021-06-01#/spikes.times.npy
```

Any files in a given revision folder are assumed to be of the same version.

Unlike collections these can be searched in lexicographical order such that a users can load a revision 
before or after a certain date.  If multiple revisions exist for a given date, letters may be appended 
to preserve ordering:
```
mouse_001/2021-05-27/001/#2021-06-01#/spikes.times.npy
mouse_001/2021-05-27/001/#2021-06-01a#/spikes.times.npy
mouse_001/2021-05-27/001/#2021-06-01b#/spikes.times.npy
```

### Namespace
For datasets that are not intended to be standard in the community, a namespace may be added to the 
start of the filename.  This must be surrounded by underscores:
```
_ibl_trials.intervals.npy
_ss_gratingID.laserOn.npy
```
For example, in `_ibl_trials.intervals.npy`, the pattern `_ibl_` is referred to as a namespace, 
and is used to indicate that this dataset is specific to the IBL.

### Timescale
Datasets containing timestamp data are expected to be in the same common timescale (usually seconds from
experiment start).  For datasets in a different timescale, the clock name should be appended to the 
attribute part with an underscore:

```
spikes.times_ephysClock.npy
trials.intervals_bpod.ssv
```

### Extension
The extension should be self-explanatory.  Although they are optional in the ALF spec, it's preferable 
to include the format in the filename, and to use formats that are well supported in MATLAB and Python:

```
spikes.times.npy
spikes.times.csv
spikes.times.mat
```

### Extra
Any number of extra parts, separated by periods, can be added after the attribute.  Examples include UUIDs
for ensuring the filename is unique or parts for splitting datasets into parts.  NB: The text after the final
period is expected to be the file extension.
```
trials.intervals.9198edcd-e8a4-4e8a-994f-d68a2e300380.npy
2p.raw.part01.tiff
2p.raw.part02.tiff
```

### Relations
Alf objects can be related through their attributes. If the attribute name of one file matches the object name of a 
second, then the first file is guaranteed to contain integers referring to the rows of the second. For example, 
`spikes.clusters.npy` would contain integer references to the rows of `clusters.brain_location.json` and 
`clusters.probes.npy`; and `clusters.probes.npy` would contain integer references to `probes.insertion.json`.


## Glossary

### Dataset name
A filename with at least an object and attribute.  Some examples of valid ALF datasets:

```
spikes.times
spikes.times.npy
_ibl_trials.goCue_times_bpodClock.csv
```

### Dataset type
In Alyx datasets are grouped by a type.  Datasets should belong to exactly one dataset type.  The 
group is determined by a filename pattern.  Dataset types group datasets with the same content but 
different formats, etc. and include a description of the dataset.  For example, the following datasets
belong to the '*spikes.times*' dataset type:
```
spikes.times
_spikeglx_spikes.times_ephysClock.npy
spikes.times.9198edcd-e8a4-4e8a-994f-d68a2e300380.npy
spikes.times.cbin
``` 

### Session path
The part of the path that includes the subject name, date and number.  Optionally a lab name may also 
be part of the session path:

```
mouse_001/2021-05-27/001
cortexlab/Subjects/mouse_001/2021-05-27/1
```

### Relative path
Everything that comes after the session path.  In other words the filename and optional collections
and revision folders:

```
alf/probe00/spikes.times.npy
trials.intervals.npy
#2021-06-01#/trials.intervals.npy
```

### ALF path
The full file path, including the session path and relative path, e.g.
```
cortexlab/Subjects/mouse_001/2021-05-27/1/alf/probe00/spikes.times.npy
```
