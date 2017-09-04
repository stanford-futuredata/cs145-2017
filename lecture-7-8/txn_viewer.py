from IPython.core.display import display_html, HTML, display_javascript, Javascript
import json
import numpy as np
import inspect
import re
from collections import defaultdict
from copy import deepcopy

class TransactionManager:
  """
  Class for maintaining a set of n_threads + 1 states
  Allows these states to be read and written to by threads, the latter via supplied functions
  Commits are also modeled explicitly
  Visualization of a supplied set of txns in the txn viewer
  """
  def __init__(self, n_threads, initial_main_vals=None):
    self.n_threads = n_threads

    # The state for each variable is stored as a row
    # where indices correspond to thread number, RAM is FIRST element
    self._state = defaultdict(lambda : [0]*(self.n_threads + 1))

    # Set initial values in global / RAM
    if initial_main_vals:
      for var, val in initial_main_vals.iteritems():
        self._state[var][0] = val

    # Start with an initial state
    self._log = [{
      'thread': -1,
      'operation': 'initial',
      'state': dict(deepcopy(self._state))
    }]

  def commit(self, thread):
    """Commit the actions since the last commit"""
    # TODO: implement actual functionality!
    self._log.append({
      'thread': thread,
      'operation': 'COMMIT',
      'state': dict(deepcopy(self._state))
    })

  def abort(self, thread):
    """Abort the actions since the last commit"""
    # TODO: implement actual functionality!
    self._log.append({
      'thread': thread,
      'operation': 'ABORT',
      'state': dict(deepcopy(self._state))
    })

  def read(self, thread, var):
    """Read var from disk / global into thread local state"""
    self._state[var][thread+1] = self._state[var][0]
    self._log.append({
      'thread': thread,
      'operation': 'READ(%s)' % var,
      'state': dict(deepcopy(self._state))
    })
    return self._state[var][thread+1]

  def write(self, thread, var, val):
    self.write_fn(thread, var, value=val)

  def write_fn(self, thread, var, value=None, f=None):
    if value and not hasattr(value, '__call__'):
      val = value
      val_string = str(value)
    elif f and hasattr(f, '__call__'):
      val = f(self._state[var][thread+1])
      val_string = lambda_function_repr(f)
    else:
      raise Exception('f or value must be specified.')
    old = self._state[var][0]
    self._state[var][0] = val
    self._state[var][thread+1] = val  # Also set local value
    self._log.append({
      'thread': thread,
      'operation': 'WRITE(%s, %s)' % (var, val_string),
      'var': var,
      'old': old,
      'new': val,
      'state': dict(deepcopy(self._state))
    })

  def print_log(self):
    for line in self._log:
      print line

  def display(self, chart_num=0, configs_in={}):
    """Display the TXN viewer based on full current log"""

    # dump input txns to jsonfor transfer to js
    with open('txnLog.json', 'wb') as f:
      json.dump(self._log, f)

    # merge default configs
    config = {
      'chartNum': chart_num,
      'numThreads': self.n_threads
    }
    config.update(configs_in)
    js = ''.join('var %s = %s\n' % (k,v) for k,v in config.iteritems())

    # JS
    js += open('txnViewer.js', 'rb').read()
    js_libs = [
      '//d3js.org/d3.v3.min.js', 
      'https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js',
      'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js'
    ]

    # HTML
    html_scripts = [
      '<link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/themes/smoothness/jquery-ui.css">'
    ]
    html="""
    <head>{0}</head>
    <h3>TXN VIEWER</h3>
    <table style="border: none; border-collapse: collapse;">
      <tr style="border: none;">
        <td style="border: none;">
          <div id="top-spacer-{1}"></div>
          <div id="chart-{1}"></div>
          <div id="slider-{1}"></div>
        </td>
        <td style="vertical-align:top; border: none;">
          <table id="vals-{1}"></table>
        </td>
      </tr>
      <tr style="border: none;">
        <td colspan="2" style="border: none;"><h4>The Log</h4></td>
      </tr>
      <tr><td colspan="2"><div id="log-{1}"></td></tr>
    </table>
    """.format(''.join(html_scripts), chart_num)

    # Display in IPython notebook
    display_html(HTML(data=html))
    display_javascript(Javascript(data=js, lib=js_libs))


def lambda_function_repr(f): 
  try:
    return re.search(r'lambda.*?:(.*?)(,|\)$)', inspect.getsource(f).strip()).group(1).strip()
  except AttributeError:
    return '?'
