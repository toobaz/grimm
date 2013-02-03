Grimm is a program for manipulating statistic and econometric data, analogously
to Gretl, STATA...

Its goals are:

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

- to ease personalization/expansion.
