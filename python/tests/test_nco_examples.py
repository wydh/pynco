import unittest, os, tempfile, sys, glob
from stat import *
from nco import *
import numpy as np
import pylab as pl

# Now run tests for examples in nco documentation
class NcoExamplesTest(unittest.TestCase):

    def test_ncks_hdf2nc(self):
        """
        1.6 netCDF2/3/4 and HDF4/5 Support
        Converting HDF4 files to netCDF: Since NCO reads HDF4 files natively,
        it is now easy to convert HDF4 files to netCDF files directly, e.g.,

        ncks        fl.hdf fl.nc # Convert HDF4->netCDF4 (NCO 4.4.0+, netCDF 4.3.1+)
        ncks --hdf4 fl.hdf fl.nc # Convert HDF4->netCDF4 (NCO 4.3.7-4.3.9)
        """
        nco = Nco(debug=True)
        nco.ncks(input='foo.hdf', ouput='foo.nc')
        nco.ncks(input='foo.hdf', ouput='foo.nc', hdf4=True)

    def test_ncks_hdf2nc3(self):
        """
        1.6 netCDF2/3/4 and HDF4/5 Support
        Obtaining a netCDF3 file from an HDF4 is now easy, even though the HDF4 file
        may contain netCDF4 atomic types (e.g., unsigned bytes, 64-bit integers):

        ncks -3 fl.hdf fl.nc      # HDF4->netCDF3 (NCO 4.4.0+, netCDF 4.3.1+)
        ncks -7 -L 1 fl.hdf fl.nc # HDF4->netCDF4 (NCO 4.4.0+, netCDF 4.3.1+)
        ncks --hdf4 -3 fl.hdf fl.nc # HDF4->netCDF3 (netCDF 4.3.0-)
        ncks --hdf4 -7 fl.hdf fl.nc # HDF4->netCDF4 classic (netCDF 4.3.0-)
        """
        nco = Nco(debug=True)
        nco.ncks(input='foo.hdf', ouput='foo.nc', options='-3')
        nco.ncks(input='foo.hdf', ouput='foo.nc', options='-7 -L 1')
        nco.ncks(input='foo.hdf', ouput='foo.nc', options='-3', hdf4=True)
        nco.ncks(input='foo.hdf', ouput='foo.nc', options='-7', hdf4=True)

    def test_temp_output_files(self):
        """
        2.3 Temporary Output Files
        ncks in.nc out.nc # Default: create out.pid.tmp.nc then move to out.nc
        ncks --wrt_tmp_fl in.nc out.nc # Same as default
        ncks --no_tmp_fl in.nc out.nc # Create out.nc directly on disk
        ncks --no_tmp_fl in.nc in.nc # ERROR-prone! Overwrite in.nc with itself
        ncks --create_ram --no_tmp_fl in.nc in.nc # Create in RAM, write to disk
        ncks --open_ram --no_tmp_fl in.nc in.nc # Read into RAM, write to disk
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', output='out.nc')
        nco.ncks(input='in.nc', output='out.nc', wrt_tmp_fl=True)
        nco.ncks(input='in.nc', output='out.nc', no_tmp_fl=True)
        nco.ncks(input='in.nc', output='in.nc', no_tmp_fl=True, create_ram=True)
        nco.ncks(input='in.nc', output='in.nc', no_tmp_fl=True, open_ram=True)

    def test_ncks_append_variables(self):
        """
        2.4 Appending Variables
        The simplest way to create the union of two files is

        ncks -A fl_1.nc fl_2.nc
        """
        nco = Nco(debug=True)
        nco.ncks(input='fl_1.nc', output='fl_2.nc', options='-A')
        nco.ncks(input='fl_1.nc', output='fl_2.nc', append=True)
        nco.ncks(input='fl_1.nc', output='fl_2.nc', apn=True)
        nco.ncks(input='fl_1.nc', output='fl_2.nc')

    def test_add_record_dimension(self):
        """
        2.6.1 Concatenators ncrcat and ncecat
        """
        nco = Nco(debug=True)
        outfiles = []
        for idx in xrange(1, 11):
            infile = 'x_{:2}.nc'.format()
            outfile = 'foo_{:2}.nc'.format()
            nco.ncpdq(input=infile, output=outfile, arrange='x,time')
            outfiles.append(outfile)
        nco.ncrcat(input=outfiles, output='out.nc')
        nco.ncpdq(input='out.nc', output='out.nc', arrange='time,x')

    def test_openMP_threading(self):
        pass

    def test_command_line_options(self):
        """
        3.4 Command Line Options

        ncks -D 3 in.nc        # Short option
        ncks --dbg_lvl=3 in.nc # Long option, preferred form
        ncks --dbg_lvl 3 in.nc # Long option, alternate form
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', options='-D 3')
        nco.ncks(input='in.nc', options='--dbg_lvl=3')
        nco.ncks(input='in.nc', options='--dbg_lvl 3')
        nco.ncks(input='in.nc', dbg_lvl=3)

    def test_specifying_input_files(self):
        """
        3.5 Specifying Input Files

        ncra 85.nc 86.nc 87.nc 88.nc 89.nc 8589.nc
        ncra 8[56789].nc 8589.nc
        ncra -p input-path 85.nc 86.nc 87.nc 88.nc 89.nc 8589.nc
        ncra -n 5,2,1 85.nc 8589.nc
        """
        inputs = ['85.nc', '86.nc', '87.nc', '88.nc', '89.nc']
        nco = Nco(debug=True)
        nco.ncra(input=inputs, ouptut='8589.nc')
        nco.ncra(input='8[56789].nc', ouptut='8589.nc')
        nco.ncra(input=inputs, ouptut='8589.nc', path='/path/to/files')
        nco.ncra(input=inputs, ouptut='8589.nc', nintap='5,2,1')

    def test_determining_file_format(self):
        """
        3.9.2 Determining File Format

        ncks -M foo_3c.nc
        ncks -M foo_364.nc
        ncks -M foo_4c.nc
        ncks -M foo_4.nc
        ncks -D 2 -M hdf.hdf
        ncks -D 2 -M http://thredds-test.ucar.edu/thredds/dodsC/testdods/in.nc
        ncks -D 2 -M foo_4.nc
        """
        nco = Nco(debug=True)
        nco.ncks(input='foo_3c.nc', options='-M')
        nco.ncks(input='foo_364.nc', options='-M')
        nco.ncks(input='foo_4c.nc', options='-M')
        nco.ncks(input='hdf.hdf', options='-D 2 -M')
        nco.ncks(input='http://thredds-test.ucar.edu/thredds/dodsC/testdods/in.nc', options='-D 2 -M')
        nco.ncks(input='foo_4.nc', options='-D 2 -M')

    def test_file_conversion(self):
        """
        3.9.2 Determining File Format

        ncks --fl_fmt=classic in.nc foo_3c.nc # netCDF3 classic
        ncks --fl_fmt=64bit in.nc foo_364.nc # netCDF3 64bit
        ncks --fl_fmt=netcdf4_classic in.nc foo_4c.nc # netCDF4 classic
        ncks --fl_fmt=netcdf4 in.nc foo_4.nc # netCDF4
        ncks -3 in.nc foo_3c.nc # netCDF3 classic
        ncks --3 in.nc foo_3c.nc # netCDF3 classic
        ncks -6 in.nc foo_364.nc # netCDF3 64bit
        ncks --64 in.nc foo_364.nc # netCDF3 64bit
        ncks -4 in.nc foo_4.nc # netCDF4
        ncks --4 in.nc foo_4.nc # netCDF4
        ncks -7 in.nc foo_4c.nc # netCDF4 classic
        ncks --7 in.nc foo_4c.nc # netCDF4 classic

        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', output='foo_3c.nc', fl_fmt='classic')
        nco.ncks(input='in.nc', output='foo_364.nc', fl_fmt='64bit')
        nco.ncks(input='in.nc', output='foo_4c.nc', fl_fmt='netcdf4_classic')
        nco.ncks(input='in.nc', output='foo_4.nc', fl_fmt='netcdf4')
        nco.ncks(input='in.nc', output='foo_3c.nc', options='-3')
        nco.ncks(input='in.nc', output='foo_3c.nc', options='--3')
        nco.ncks(input='in.nc', output='foo_364c.nc', options='-6')
        nco.ncks(input='in.nc', output='foo_364c.nc', options='--64')
        nco.ncks(input='in.nc', output='foo_4.nc', options='-4')
        nco.ncks(input='in.nc', output='foo_4.nc', options='--4')
        nco.ncks(input='in.nc', output='foo_4c.nc', options='-7')
        nco.ncks(input='in.nc', output='foo_4c.nc', options='--7')

    def test_autoconversion(self):
        """
        3.9.4 Autoconversion

        # Convert file with netCDF4 atomic types
        ncks -3 in.nc4 out.nc3
        # Convert file with multiple record dimensions + netCDF4 atomic types
        ncks -3 --fix_rec_dmn=all in.nc4 out.nc3
        # Convert file with groups, multiple record dimensions + netCDF4 atomic types
        ncks -3 -G : --fix_rec_dmn=all in.nc4 out.nc3
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc4', output='out.nc3', options='-3')
        nco.ncks(input='in.nc4', output='out.nc3', fix_rec_dmn='all', options='-3')
        nco.ncks(input='in.nc4', output='out.nc3', fix_rec_dmn='all', options='-3 -G :')

    def test_subsetting(self):
        """
        3.11 Subsetting Files

        """
       pass

    def test_c_and_fortran_index_conventions(self):
        """
        3.14 C and Fortran Index conventions
        ncra -d time,5,7 85.nc 85_JJA.nc
        ncra -F -d time,6,8 85.nc 85_JJA.nc
        """
        nco = Nco(debug=True)
        nco.ncra(input='85.nc', output='85_JJA.nc', dimension='time,5,7')
        nco.ncra(input='85.nc', output='85_JJA.nc', fortran=True, dimension='time,6,8')

    def test_hyperslabs(self):
        """
        3.15 Hyperslabs

        # First and second indices of lon dimension
        ncks -F -d lon,1,2 in.nc out.nc
        # Second and third indices of lon dimension
        ncks -d lon,1,2 in.nc out.nc
        # All longitude values between 1 and 2 degrees
        ncks -d lon,1.0,2.0 in.nc out.nc
        # All longitude values between 1 and 2 degrees
        ncks -F -d lon,1.0,2.0 in.nc out.nc
        # Every other longitude value between 0 and 90 degrees
        ncks -F -d lon,0.0,90.0,2 in.nc out.nc
        # Last two indices of lon dimension
        ncks -F -d lon,1,-2 in.nc out.nc
        # Third-to-last to last index of lon dimension
        ncks -F -d lon,-3,-1 in.nc out.nc
        # Third-to-last to last index of lon dimension
        ncks -F -d lon,-3, in.nc out.nc
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,1,2')
        nco.ncks(input='in.nc', output='out.nc', dimension='lon,1,2')
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,1.0,2.0')
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,0.0,90.0,2')
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,1,-2')
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,-3,-1')
        nco.ncks(input='in.nc', output='out.nc', fortran=True, dimension='lon,-3')

    def test_stride(self):
        """
        3.16 Stride

        ncks -d time,2,,12 8501_8912.nc 8589_03.nc
        ncra -F -d time,3,,12 85.nc 86.nc 87.nc 88.nc 89.nc 8589_03.nc
        ncrcat -F -d time,3,,12 85.nc 86.nc 87.nc 88.nc 89.nc 8503_8903.nc
        """
        infiles = ['85.nc', '86.nc', '87.nc', '88.nc', '89.nc',]
        nco = Nco(debug=True)
        nco.ncks(input='8501_8912.nc', output='8589_03.nc', dimension='time,2,,12')
        nco.ncra(input=infiles, output='8589_03.nc', dimension='time,3,,12', fortran=True)
        nco.ncrcat(input=infiles, output='8503_8903.nc', dimension='time,3,,12', fortran=True)

    def test_record_appending(self):
        """
        3.17 Record Appending

        ncrcat -O fl_1.nc fl_2.nc fl_3.nc
        ncrcat --rec_apn fl_1.nc fl_2.nc
        ncrcat --rec_apn --no_tmp_fl fl_1.nc fl_2.nc
        """
        nco = Nco(debug=True)
        nco.ncrcat(input=['fl_1.nc', 'fl_2.nc'], output='fl_2.nc', options='-O')
        nco.ncrcat(input='fl_1.nc', output='fl_2.nc', rec_apn=True)
        nco.ncrcat(input='fl_1.nc', output='fl_2.nc', rec_apn=True, no_tmp_fl=True)

    def test_duration(self):
        """
        3.18 Duration

        # Step 1: Compute climatological summertime mean
        ncra -O -F -d time,6,,12,3 -n 150,4,1 1850.nc clm_JJA.nc

        # Step 1: Archive all 150 summertime means in one file
        ncra --mro -O -F -d time,6,,12,3 -n 150,4,1 1850.nc 1850_2009_JJA.nc
        ncra --mro -O -d time,,,12,12 -n 150,4,1 1850.nc 1850_2009.nc
        """
        nco = Nco(debug=True)
        nco.ncra(input='1850.nc', output='clm_JJA.nc',
                 overwrite=True, mro=True, fortran=True,
                 dimension='time,6,,12,3', nintap='150,4,1')
        nco.ncra(input='1850.nc', output='1850_2009_JJA.nc',
                 overwrite=True, mro=True, fortran=True,
                 dimension='time,6,,12,3', nintap='150,4,1'))
        nco.ncra(input='1850.nc', output='1850_2009.nc',
                 overwrite=True, mro=True, dimension='time,,,12,12',
                 nintap='150,4,1'))

    def test_multislabs(self):
        """
        3.19 Multislabs

        ncks -d lon,10.,20. -d lon,80.,90. in.nc out.nc
        ncks -d lon,10.,15. -d lon,15.,20. -d lon,80.,90. in.nc out.nc
        ncks -d lon,0,4 -d lon,2,9,2 in.nc out.nc
        ncks -d species,0,1 -d species,5 -d lon,0,4 -d lon,2,9,2 in.nc out.nc
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', output='out.nc', options='-d lon,10.,20. -d lon,80.,90.')
        nco.ncks(input='in.nc', output='out.nc', options='-d lon,0,4 -d lon,2,9,2')
        # Note: we're using the options keyword here because python wont except two dimension keywords

    def test_wrapped_coordinates(self):
        """
        3.20 Wrapped Coordinates
        ncks -d lon,340.,50. in.nc out.nc
        ncks -d lon,340.,50. -d lat,10.,35. in.nc out.nc
        """
        nco = Nco(debug=True)
        nco.ncks(input='in.nc', output='out.nc', dimension='lon,340.,50.')
        nco.ncks(input='in.nc', output='out.nc', options='-d lon,340.,50. -d lat,10.,35.')

if __name__ == '__main__':
    unittest.main()