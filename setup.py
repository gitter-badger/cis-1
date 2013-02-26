from setuptools import setup, find_packages, Command
from pkg_resources import require, DistributionNotFound, VersionConflict
from distutils.spawn import spawn, find_executable
import sys, os, os.path

# Extension classes and functions to add custom command
#======================================================


class check_dep(Command):
    """
    Command to check that the required dependencies are installed on the system
    """
    description = "Checks that the required dependencies are installed on the system"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        deps = ["matplotlib>=1.2.0","pyke","cartopy","Shapely","netcdf4",
                "numpy","scipy","nose","iris"]
        for dep in deps:
            try:
                require(dep)
                print dep + " ...[ok]"
            except (DistributionNotFound, VersionConflict):
                print dep + "... MISSING!" 

class gen_doc(Command):
    """
    Command to generate the API reference using epydoc
    """
    description = "Generates the API reference using epydoc"
    user_options = []

    def initialize_options(self):
        require("epydoc")

    def finalize_options(self):
        pass

    def run(self):
        #raise NotImplementedError, "not implemented yet"  

        if not find_executable('epydoc'):
            print "Could not find epydoc on system"
            return  

        # create output directory if does not exists
        output_dir = "doc/api"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        from subprocess import call
        call(["epydoc", "--html", "--no-sourcecode", "-o", output_dir, "*"])

        import webbrowser
        webbrowser.open(os.path.join(output_dir,"index.html"))


# Metadata description
#=====================

setup(
    name='cis',
    version='0.1',
    description='Climate Inter-comparison Suite',
    author=' ',
    author_email=' ',
    url='http://proj.badc.rl.ac.uk/cedaservices/wiki/JASMIN/CommunityIntercomparisonSuite',

    packages=find_packages(),
    package_data={'':['logging.conf']},

    scripts = ['bin/cis'],
    
    cmdclass={"gendoc": gen_doc, "checkdep":check_dep}
)


