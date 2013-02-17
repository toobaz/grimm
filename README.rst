Grimm
=====

Grimm is a program for manipulating statistic and econometric data, analogously
to Gretl, STATA...

It's in a very early stage of development, but to get an idea of how it looks you can just
download it and run "./grimm". Then, paste into the scripts editing window the
following::

  open_csv( "/usr/share/pyshared/pandas/tests/data/iris.csv" )
  ols( PetalWidth, SepalWidth )
  scatter( PetalWidth, SepalWidth )

and click the "Run" button just above.

You will need `pandas <http://pandas.pydata.org/>`_,
`matplotlib <http://matplotlib.org>`_ and a recent (0.4.2 is not enough) version
of `statsmodels <http://statsmodels.sourceforge.net>`_.

Goals
-----

- to be scriptable in python;

- to have a nice and intuitive GUI (with a multiwindows mode like Gretl, and a
  single window mode as Stata among which to choose);

- to have perfect integration between GUI, scripts and interactive shell: not
  all commands/options will necessarily be exposed in the GUI, but everything
  which is exposed in the GUI will be "scriptable", and it will be as easy as
  possible to do so (i.e. commands "given" through the GUI will appear in the
  shell's history);

- to never reinvent the wheel, but rather build an abstract enough skeleton
  so as to make it as quick as possible to support new functionalities from
  statsmodels/pandas;

- to allow handling multiple datasets together,

- to ease personalization/expansion, while guaranteeing consistency,

- to make replicability and integration in the academic workflow trivial: it
  should require only a minimal effort to make a script produce all the graphs,
  tables and number ready to be used in a LaTeX document.
