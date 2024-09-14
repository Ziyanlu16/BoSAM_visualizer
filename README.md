# A NIfTI (nii.gz) 3D Visualizer using VTK and Qt5

### Run with Python

1.  Create a virtual environment. Mac can use virtualenv or conda. Windows must use conda.
2.  Install the dependencies (PyQt5, vtk, and sip) `pip install PyQt5 vtk`
3.  Start the program `python ./visualizer/bone_3d.py -i "./sample_data/images/colon.nii.gz" -m "./sample_data/labels/colonl.nii.gz"`

### Download data remotely from our server

1. Use command line `cd remote_download`
2. Connect to the server `python main.py`
3. Enter the password and you can download the data.

### Generate PyInstaller Binaries
**Note**: Must modify the paths in .spec file to match your project directory
* Mac: `pyinstaller Theia_Mac.spec`
* Windows: `pyinstaller Theia_Windows.spec`