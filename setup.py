#!/usr/bin/env python
from distutils.core import setup, Command
from unittest import TextTestRunner, TestLoader, TestSuite
from glob import glob
from os.path import splitext, basename, join as pjoin, walk
import os, sys
try:
    from pylint import lint
    PyLinter
except:
    pass

"""
Build, clean and test the WMCore package.
"""

class TestCommand(Command):
    """
    Handle setup.py test with this class - walk through the directory structure 
    and build up a list of tests, then build a test suite and execute it.
    
    TODO: Pull database URL's from environment, and skip tests where database 
    URL is not present (e.g. for a slave without Oracle connection)
    """
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in test/python/WMCore_t, and runs them.
        '''
        testfiles = [ ]
        
        # Add the test and src directory to the python path
        testspypath = '/'.join([self._dir, 'test/python/'])
        srcpypath = '/'.join([self._dir, 'src/python/']) 
        sys.path.append(testspypath)
        sys.path.append(srcpypath)
        
        # Walk the directory tree
        for dirpath, dirnames, filenames in os.walk('./test/python/WMCore_t'):
            # skipping CVS directories and their contents
            pathelements = dirpath.split('/')
            if not 'CVS' in pathelements:
                # to build up a list of file names which contain tests
                for file in filenames:
                    if file not in ['__init__.py']:
                        if file.endswith('_t.py'):
                            testmodpath = pathelements[3:]
                            testmodpath.append(file.replace('.py',''))
                            testfiles.append('.'.join(testmodpath))
                            
        testsuite = TestSuite()
        for test in testfiles:
            try:
                testsuite.addTest(TestLoader().loadTestsFromName(test))
            except Exception, e:
                print "Could not load %s test - fix it!\n %s" % (test, e)
        print "Running %s tests" % testsuite.countTestCases()
        
        t = TextTestRunner(verbosity = 1)
        result = t.run(testsuite)
        if not result.wasSuccessful():
            sys.exit("Tests unsuccessful. There were %s failures and %s errors"\
                      % (len(result.failures), len(result.errors)))
        
        
class CleanCommand(Command):
    """
    Clean up (delete) compiled files
    """
    user_options = [ ]

    def initialize_options(self):
        self._clean_me = [ ]
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith('.pyc'):
                    self._clean_me.append(pjoin(root, f))

    def finalize_options(self):
        pass

    def run(self):
        for clean_me in self._clean_me:
            try:
                os.unlink(clean_me)
            except:
                pass
            
class LintCommand(Command):
    """
    Lint all files in the src tree
    
    TODO: better format the test results, get some global result, make output 
    more buildbot friendly.    
    """
    
    user_options = [ ]
    
    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass
    
    def run(self):
        '''
        Find the code and run lint on it
        '''
        files = [ ]
        
        srcpypath = '/'.join([self._dir, 'src/python/'])
        sys.path.append(srcpypath) 
        
        # Walk the directory tree
        for dirpath, dirnames, filenames in os.walk('./src/python/'):
            # skipping CVS directories and their contents
            pathelements = dirpath.split('/')
            result = []
            if not 'CVS' in pathelements:
                # to build up a list of file names which contain tests
                for file in filenames:
                    if file.endswith('.py'):
                        filepath = '/'.join([dirpath, file]) 
                        files.append(filepath)
                        # run individual tests as follows
                        try:
                            lint.Run(['--rcfile=standards/.pylintrc', 
                                      '--output-format=parseable', 
                                      '-r n',
                                      filepath])
                        except SystemExit:
                            pass
                        except Exception, e:
                            print "Couldn't lint %s\n%s %s" % (file, e, type(e))
                            result.append((file, -100))
        # Could run a global test as:
        #input = ['--rcfile=standards/.pylintrc']
        #input.extend(files)
        #lint.Run(input)    
                    
def getPackages(package_dirs = []):
    packages = []
    for dir in package_dirs:
        for dirpath, dirnames, filenames in os.walk('./%s' % dir):
            # Exclude things here
            if dirpath not in ['./src/python/', './src/python/IMProv']: 
                pathelements = dirpath.split('/')
                if not 'CVS' in pathelements:
                    path = pathelements[3:]
                    packages.append('.'.join(path))
    return packages

package_dir = {'WMCore': 'src/python/WMCore',
               'WMComponent' : 'src/python/WMComponent',
               'WMQuality' : 'src/python/WMQuality'}

setup (name = 'wmcore',
       version = '1.0',
       cmdclass = { 'test': TestCommand, 
                   'clean': CleanCommand, 
                   'lint': LintCommand },
       package_dir = package_dir,
       packages = getPackages(package_dir.values()),)

