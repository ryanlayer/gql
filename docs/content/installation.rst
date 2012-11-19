############
Installation
############


--------------
Pre-requisites
--------------

1. `bedtools <http://code.google.com/p/bedtools/>`_::

	=== OSX (using Homebrew) ===
	brew install bedtools

2. `pybedtools <http://packages.python.org/pybedtools/>`_::

	easy_install pybedtools
	


--------------
Installing GQL
--------------

To install you should download the latest source code from GitHub, either by going to::

    http://github.com/ryanlayer/gql

and clicking on "Downloads", or by cloning the git repository with::

    $ git clone https://github.com/ryanlayer/gql.git

Once you have the source code, run::

    $ cd gql
    $ sudo python setup.py install

to install it. If you don't have permission to install it in the default directory, you can simply build the source in-place and use the package from the git repository::

    $  python setup.py build_ext --inplace
