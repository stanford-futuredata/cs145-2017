from collections import namedtuple, OrderedDict
from copy import copy
import numpy as np
from IPython.core.display import display_html, HTML, display_javascript, Javascript
import json
import random

class BufferMemoryException(Exception):
  pass

class PageNotFoundException(Exception):
  pass

class FileNotFoundException(Exception):
  pass

class Page:
  def __init__(self, fid, pid, size, data=None):
    self.file_id = fid
    self.id = pid
    self.size = size
    if data is None:
      self._data = [None]*size
    else:
      self.set_all(data)
    self._i = 0

  def size(self, count_empty=False):
    return len(filter(lambda e : e or count_empty, self._data))
  
  def get(self, i):
    if i < self.size:
      return self._data[i]
    else:
      raise IndexError

  def pop(self):
    # TODO FINISH THIS!!!
    x = self._data[self._i]
    self._data[self._i] = None
    self._i += 1
    return x

  def peek(self):
    # TODO: Finish this!
    return self._data[self._i]

  def is_empty(self):
    return len([d for d in self._data if d is not None]) == 0

  def set(self, i, val):
    if i < self.size:
      self._data[i] = val
    else:
      raise IndexError

  def set_all(self, data):
    if len(data) != self.size:
      raise Exception("Data and page size do not match")
    else:
      self._data = data

  def copy(self):
    return Page(self.file_id, self.id, self.size, data=copy(self._data))

  def get_data_copy(self):
    return copy(self._data)

  def __iter__(self):
    return iter(self._data)

  def next(self):
    if self._i < self.size:
      self._i += 1
      return self.get(self._i-1)
    else:
      raise StopIteration()

  def __str__(self):
    return "<Page(file_id=%s, id=%s, data=%s)>" % (self.file_id, self.id, self.data)

  def __repr__(self):
    return self.__str__()

class FileIterator:
  """
  Simple class for iterating through a file and reading successive elements of pages
  By default, the FileIterator only uses a single page (frame) of the buffer,
  And either gets the next element in the page or releases it and reads in a new one from disk
  """
  def __init__(self, b, file_id):
    self.buffer = b
    self.file_id = file_id
    self.file_size = len(self.buffer.get_file(file_id))
    self.P = self.buffer.page_size
    self._page = None
    self._p = -1  # The page index
    self._e = self.P - 1  # The element index
    self._current_value = None

  def _next_page(self):
    """Release the current page & get next non-null page, stopping iteration if EOF reached"""
    if self._page:
      self.buffer.release(self._page)
    if self._p < self.file_size - 1:
      self._p += 1
      self._page = self.buffer.read(self.file_id, self._p)
      if self._page is None:
        self._next_page()
    else:
      self._p = -1
      self._e = self.P - 1
      raise StopIteration

  def next(self):
    """
    Get next *element* of the pages in the file
    Handles reading / flushing pages so that at most one page is in the buffer
    """

    # Iterate the element counter and get next page if at end of current one
    self._e += 1
    if self._e == self.P:
      self._e = 0
      self._next_page()
    
    # Get the next element
    x = self._page.get(self._e)

    # Skip None elements by recursing
    if x is None:
      x = self.next()
    self._current_value = x
    return x

  def get_next(self):
    """Returns None instead of StopIteration exception if EOF reached"""
    try:
      return self.next()
    except StopIteration:
      return None

  def erase_current(self):
    """
    Deletes the current element from page, still storing it in FileIterator
    Mostly for animations
    """
    self._page.set(self._e, None)
    self.buffer.log_buffer_data_diffs()

  def peek(self):
    """Returns the current value in the stream without advancing it"""
    return self._current_value

  def __iter__(self):
    return self

class FileWriter:
  """
  A simple class for writing to a file
  By default the FileWriter only takes up a single page (frame) in the buffer,
  flushing to disk when full
  """
  def __init__(self, b, file_id):
    self.buffer = b
    self.file_id = file_id
    self.P = self.buffer.page_size
    self._page = None
    self._i = 0  # The page index
    self.pages_written = 0

  def append(self, x):
    """Adds an element to the next free slot in a current or new page"""

    # Load new page, then set next element
    if self._page is None:
      self._page = self.buffer.new_page(self.file_id)
      self._i = 0
    self._page.set(self._i, x)
    self._i += 1

    # Also log for animation
    self.buffer.log_buffer_data_diffs()

    # If page is full, flush here
    if self._i == self.P:
      self.buffer.flush(self._page)
      self.pages_written += 1
      self._page = None

  def close(self):
    """Closes the writer"""
    if self._page is not None:
      self.buffer.flush(self._page)
      self.pages_written += 1

class Buffer:
  def __init__(self, page_size=4, buffer_size=4, sequential_cost=1.0, buffer_queue_indicator=None):
    self.buffer_size = buffer_size
    self.page_size = page_size

    # Display tooltip over e.g. LRU, MRU
    self.buffer_queue_indicator = buffer_queue_indicator

    # The buffer is a hash table of pages, of fixed size
    self._buffer = [None]*self.buffer_size
    self._buffer_order = []
    self._buffer_map = {}

    # The disk is a list of files, which are lists of pages
    self._disk = []

    # Keep track of the last read / write fid,pid for sequential discount
    self._last_id = None
    self._sequential_cost = sequential_cost

    # The log records read & write operations between disk, buffer and main (name??)
    self._io_count = {
      'bufferReads': 0,
      'bufferWrites': 0,
      'diskReads': 0,
      'diskWrites': 0
    }
    self._log = []

    # for d3 animations
    self._chart_num = 0
    self._pages_start_state = []
    self._diff_log_start = 0
    self._buffer_stale = [None]*self.buffer_size
  
  def buffer_is_full(self):
    return len(filter(lambda x : x is None, self._buffer)) == 0

  def get_empty_buffer_slot(self):
    for i in range(len(self._buffer)):
      if self._buffer[i] is None:
        return i
    else:
      raise BufferMemoryException

  def get_empty_disk_slot(self):
    i = -1
    for i in range(len(self._disk)):
      if self._disk[i] is None:
        self._disk[i] = []
        return i
    self._disk.append([])
    return i + 1 

  def get_file_size(self, file_id, count_empty=False):
    return len(filter(lambda p : p or count_empty, self._disk[file_id]))

  def _update_log(self, op, page, buffer_idx, old_location, new_location, keep_old, file_id=None, show=True, tooltip_content=None):
    fid = page.file_id if page else file_id
    pid = page.id if page else None
    page_data = page.get_data_copy() if page else None
    self._log.append({
      "operation": op,
      "oldLocation": old_location,
      "newLocation": new_location,
      "file": fid,
      "page": pid,
      "bufferIndex": buffer_idx,
      "pageData": page_data,
      "keepOld": keep_old,
      "ioCount": copy(self._io_count),
      "show": show,
      "tooltipContent": tooltip_content
    })

  def print_log(self):
    for l in self._log:
      print '%s : id=(%s,%s) : %s -> %s [bi=%s]' % (l['operation'], l['file'], l['page'], l['oldLocation'], l['newLocation'], l['bufferIndex'])

  def get_buffer_page(self, idx):
    """Returns page & buffer index of specific page by buffer order"""
    if type(idx) == int:
      if idx >= self.buffer_size:
        raise BufferMemoryException
    else:
      if idx == 'LRU':
        j = 0
      elif idx == 'MRU':
        j = -1
      else:
        raise Exception("Unrecognized index type.")
      if len(self._buffer_order) > 0:
        i = self._buffer_order[j]
      else:
        return None, None
    return self._buffer[i], i

  def update_buffer_queue_indicator(self, remove_idx=None, add_idx=None):
    """
    Updates the buffer order queue = tracks order in which pages were put in buffer
    Sends tooltip updates to log for a separate tooltip to indicate e.g. LRU/MRU
    """
    if remove_idx is not None:
      self._buffer_order = filter(lambda i : i != remove_idx, self._buffer_order)
    if add_idx is not None:
      self._buffer_order.append(add_idx)
    if self.buffer_queue_indicator:
      page, buffer_idx = self.get_buffer_page(self.buffer_queue_indicator)
      self._update_log('TOOLTIP-2', page, buffer_idx, 'BUFFER', 'BUFFER', False, tooltip_content=self.buffer_queue_indicator)

  def read(self, fid, pid):
    """
    Attempts to read page from buffer, else tries to load a copy of the page from disk
    Throws exceptions if page not in buffer and buffer is full or page not found on disk
    """
    id = (fid, pid)
    self.log_buffer_data_diffs()

    # Not in buffer and buffer full!
    if id not in self._buffer_map and self.buffer_is_full():
      raise BufferMemoryException

    # File and/or page not found!
    elif fid >= len(self._disk) or pid >= len(self._disk[fid]):
      raise PageNotFoundException
    
    else:
      # If not already in buffer, read from disk to buffer
      # Find an empty slot in the buffer and insert copy of page from disk
      if id not in self._buffer_map:
        if self._last_id == (id[0], id[1]-1):
          self._io_count['diskReads'] += self._sequential_cost
        else:
          self._io_count['diskReads'] += 1
        i = self.get_empty_buffer_slot()
        page = self._disk[fid][pid].copy()
        self._buffer[i] = page
        self._buffer_map[id] = i
        self._update_log('READ FROM DISK', page, i, 'DISK', 'BUFFER', True)

      # log for sequential discounting
      self._last_id = id

      # Perform & record read *from* buffer, adjust buffer use order
      i = self._buffer_map[id]
      self.update_buffer_queue_indicator(remove_idx=i, add_idx=i)
      self._io_count['bufferReads'] += 1
      page = self._buffer[i]
      self._update_log('Read from Buffer', page, i, 'BUFFER', 'BUFFER', False)
      return page

  def new_page(self, fid):
    """
    Creates a new page, in buffer only, returning the page
    """
    # Buffer full!
    if self.buffer_is_full():
      raise BufferMemoryException

    # New page must be assigned to a file, and this file must already exist on disk!
    elif fid >= len(self._disk):
      raise FileNotFoundException

    # Create in buffer- log this (mainly for animation)
    else:

      # Get the next index for the file, append an empty placeholder in the file on disk
      # TODO: replace this method, have them do manually?
      pid = len(self._disk[fid])
      self._disk[fid].append(None)

      # Place a new page in the buffer
      page = Page(fid, pid, self.page_size)
      i = self.get_empty_buffer_slot()
      self._buffer[i] = page
      self._buffer_stale[i] = page.copy()
      self._buffer_map[(fid, pid)] = i
      self.update_buffer_queue_indicator(add_idx=i)
      self._update_log('Write to Buffer', page, i, None, 'BUFFER', False)
      return page

  def release(self, page):
    """
    Releases page from buffer without flushing to disk, clearing the buffer frame
    """
    self.log_buffer_data_diffs()
    id = (page.file_id, page.id)

    # Must be in buffer!
    if id not in self._buffer_map:
      raise PageNotFoundException

    # Release from buffer without flushing to disk
    else:
      i = self._buffer_map.pop(id)
      self.update_buffer_queue_indicator(remove_idx=i)
      self._update_log('RELEASE', page, i, 'BUFFER', None, False)
      self._buffer[i] = None

  def flush(self, page):
    """
    Writes the page to buffer, then flushes the page in buffer to disk, clearing it from buffer
    """
    self.log_buffer_data_diffs()
    fid = page.file_id
    pid = page.id
    id = (fid, pid)

    # Must be in buffer!
    if id not in self._buffer_map:
      raise PageNotFoundException

    # Must have a file to write to!
    elif page.file_id >= len(self._disk):
      raise FileNotFoundException

    # Flush to disk: remove from buffer, buffer map, place in disk
    else:
      if self._last_id == (id[0], id[1]-1):
        self._io_count['diskWrites'] += self._sequential_cost
      else:
        self._io_count['diskWrites'] += 1
      self._update_log('FLUSH TO DISK', page, self._buffer_map[id], 'BUFFER', 'DISK', False)
      i = self._buffer_map.pop(id)
      self._disk[fid][pid] = self._buffer[i]
      self._buffer[i] = None
      self.update_buffer_queue_indicator(remove_idx=i)

      # log for sequential discounting
      self._last_id = id

  def get_file(self, fid):
    """
    Gets a file from disk, which is just a list of page ids
    """
    if fid >= len(self._disk):
      raise FileNotFoundException
    else:
      return range(len(self._disk[fid]))

  def get_file_len(self, fid):
    return len(self.get_file(fid))

  def new_file(self):
    """
    Creates a new file on disk, returns the file id
    """
    file_id = self.get_empty_disk_slot()
    self._update_log('NEWFILE', None, None, None, None, False, file_id=file_id)
    return file_id

  def delete_file(self, file_id):
    self._disk[file_id] = None
    self._update_log('DELETEFILE', None, None, None, None, False, file_id=file_id)

  def log_buffer_data_diffs(self):
    """
    The user can modify the data in the buffer directly
    We want to have a record of these updates though for logging & animation
    """
    for i,page in enumerate(self._buffer):
      if page is not None:
        # Note: only show + log IO count if an actual data change vs. initialization
        diff = self._buffer_stale[i] and not np.array_equal(page.get_data_copy(), self._buffer_stale[i].get_data_copy())
        if self._buffer_stale[i] is None or diff:
          self._update_log('WRITE (Buffer)', page, i, 'BUFFER', 'BUFFER', False, show=False)
          self._buffer_stale[i] = page.copy()
          if diff:
            self._io_count['bufferWrites'] += 1

  def display(self, speed=1000, from_start=False, reset_io=False, buffer_num=0):
    """
    Display an animation, based on a starting state & the logged diff
    Once this is called, the starting state & log mark are advanced
    """
    self.log_buffer_data_diffs()

    # Create a new html pane with unique id
    chart_id = '%s-%s' % (buffer_num, self._chart_num)
    html = """
    <table>
      <tr><th><i>IO Counts</i></th><th>R</th><th>W</th></tr>
      <tr>
        <td><i>To/from Buffer</i></td>
        <td id="chart-{0}-bufferReads">0</td>
        <td id="chart-{0}-bufferWrites">0</td>
      </tr>
      <tr>
        <td><b>To/from Disk</b></td>
        <td id="chart-{0}-diskReads">0</td>
        <td id="chart-{0}-diskWrites">0</td>
      </tr>
    </table>
    <br />
    <div class="tooltip" id="chart-{0}-tooltip" style="position:absolute; z-index:100; color:white; background:black; opacity:0.7; padding:3px; border-radius:5px; display:none;">TOOLTIP!</div>
    <div class="tooltip" id="chart-{0}-tooltip-2" style="position:absolute; z-index:100; color:white; background:black; opacity:0.7; padding:3px; border-radius:5px; display:none;">TOOLTIP!</div>
    <div id="chart-{0}"></div>
    """.format(chart_id)

    # Dump log to json file
    with open('pagesLog.json', 'wb') as f:
      json.dump(self._log, f)

    # Create animation in js/d3
    js_configs = {
      'DURATION': speed,
      'chartNum': chart_id,
      'numBufferPages': self.buffer_size,
      'pageSize': self.page_size,
      'numDiskPages': 5,
      'logStart': self._diff_log_start if not from_start else 0
    }
    js = js_file_with_configs('compModel.js', js_configs)
    js_libs = [
      'https://d3js.org/d3.v3.min.js',
      'https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js',
      'https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js'
    ]
    display_html(HTML(data=html))
    display_javascript(Javascript(data=js, lib=js_libs))
    self._chart_num += 1
    
    # Advance current animation state in log
    self.display_set_mark(reset_io=reset_io)
    
  def display_set_mark(self, reset_io=True):
    """
    Set mark so that next display command starts animation at this point
    Also reset IO counter
    """
    self._diff_log_start = len(self._log)
    if reset_io:
      for k in self._io_count.iterkeys():
        self._io_count[k] = 0

def js_file_with_configs(fpath, configs):
  """
  Take in a js filepath and a dictionary of configs to be passed in as global vars
  """
  js = ''
  for k,v in configs.iteritems():
    if type(v) == str:
      js += 'var %s = "%s"\n' % (k,v)
    elif type(v) in [int, float]:
      js += 'var %s = %s\n' % (k,v)
  js += open(fpath, 'rb').read()
  return js

def new_rand_file(b, r, l, sorted=False):
  vals = random.sample(range(r), l)
  if sorted:
    vals.sort()
  fid = b.new_file()
  fw = FileWriter(b, fid)
  for v in vals:
    fw.append(v)
  fw.close()
  return fid
