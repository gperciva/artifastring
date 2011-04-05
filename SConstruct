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

dirs = """src swig doc"""

env = Environment()

### destination
AddOption('--prefix',
	dest='prefix',
	type='string',
	nargs=1,
	action='store',
	metavar='DIR',
	help='installation prefix')
env = Environment(PREFIX = GetOption('prefix'))

#print env.Dump()


env.Append(
	CPPFLAGS=Split("-O3 -FPIC -funroll-loops"),
	CPPPATH=[
		"/usr/include/python2.6",
		],
)

### test for swig
swig = True
config = Configure(env)
status = config.CheckCXXHeader('Python.h')
if not status:
	print("Need Python.h")
	swig = False
status = config.CheckLib('python2.6')
if not status:
	print("Need python2.6")
	swig = False
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

for dirname in Split(dirs):
	if dirname == "swig" and not swig:
		print "Skipping over swig build"
		continue
	if dirname == "doc" and not 'doc' in COMMAND_LINE_TARGETS:
		continue
#	if dirname == "actions" and not 'unit' in COMMAND_LINE_TARGETS:
#		continue
	sconscript_filename = dirname + os.sep + "SConscript"
	build_dirname = 'build' + os.sep + dirname
	SConscript(sconscript_filename, build_dir=build_dirname, duplicate=0)
	Clean(sconscript_filename, build_dirname)

Clean('.', 'build')

