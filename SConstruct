import os

# TODO: hard-coded python verison!
Help("""
Build stuff:
    scons

Docs:  (requires doxygen)
    scons doc

Install stuff to:  bin/ include/ lib/
    scons --prefix=DIR install
# I use:
    scons --prefix=$HOME/.usr/ install
""")

### destination
AddOption('--prefix',
	dest='prefix',
	type='string',
	nargs=1,
	action='store',
	metavar='DIR',
	help='installation prefix')
env = Environment(
	ENV = os.environ,
	PREFIX = GetOption('prefix'),
)

#print env.Dump()


env.Append(
	CPPFLAGS=Split("-O3 -FPIC -funroll-loops"),
#	CPPFLAGS=Split("-g -fbounds-check -Wall -Wextra"),
	CPPPATH=[
		"/usr/include/python2.6",
		],
)

### configure
has_swig = True
has_doxygen = True
if (not env.GetOption('clean')) and (not env.GetOption('help')):
	### test for swig
	config = Configure(env)
	#
	status = config.CheckCXXHeader('Python.h')
	if not status:
		print("Need Python.h")
		has_swig = False
	#
	status = config.CheckLib('python2.6')
	if not status:
		print("Need python2.6")
		has_swig = False
	#
	status = WhereIs('swig')
	if not status:
		print("Need swig")
		has_swig = False
	#
	### test for doc
	status = WhereIs('doxygen')
	if not status:
		print("Need doxygen")
		has_doxygen = False
	#
	#
	env = config.Finish()
	


### shared artifastring files
# the \# means "top level directory"
env['artifastring_lib_files'] = Split("""
	violin_string.cpp
	violin_instrument.cpp	
	monowav.cpp
	""")


### setup for installing
env.Alias('install', '$PREFIX')

Export('env')

def process_dir(dirname):
	sconscript_filename = dirname + os.sep + "SConscript"
	build_dirname = 'build' + os.sep + dirname
	SConscript(sconscript_filename, build_dir=build_dirname, duplicate=0)
	Clean(sconscript_filename, build_dirname)

process_dir('src')
if (has_swig) and (('swig' in COMMAND_LINE_TARGETS)
		   or ('all' in COMMAND_LINE_TARGETS)):
	process_dir('swig')
if (has_doxygen) and ('doc' in COMMAND_LINE_TARGETS):
	process_dir('doc')

Clean('.', 'build')

