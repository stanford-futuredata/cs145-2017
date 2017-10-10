# A  = set(["name", "category"]) # These are the attribute set.
# fds = [ (set(["name"]),"color"),
#         (set(["category"]), "department"),
#         (set(["color", "category"]), "price") ]

def to_set(x):
  """Convert input int, string, list, tuple, set -> set"""
  if type(x) == set:
    return x
  elif type(x) in [list, set]:
    return set(x)
  elif type(x) in [str, int]:
    return set([x])
  else:
    raise Exception("Unrecognized type.")

def fd_to_str((lhs,rhs)): return ",".join(to_set(lhs)) + " -> " + ",".join(to_set(rhs))

def fds_to_str(fds): return "\n\t".join(map(fd_to_str, fds))

def set_to_str(x): return "{" + ",".join(x) + "}"

def fd_applies_to(fd, x): 
  lhs, rhs = map(to_set, fd)
  return lhs.issubset(x)

def print_setup(A, fds):
  print("Attributes = " + set_to_str(A))
  print("FDs = \t" + fds_to_str(fds))

"""Does the FD apply"""
def fd_applies(x, (lhs,rhs)): return to_set(lhs).issubset(x)

def compute_closure(x, fds, verbose=False):
    bChanged = True        # We will repeat until there are no changes.
    x_ret    = x.copy()    # Make a copy of the input to hold x^{+}
    while bChanged:
        bChanged = False   # Must change on each iteration
        for fd in fds:     # loop through all the FDs.
            (lhs, rhs) = map(to_set, fd) # recall: lhs -> rhs
            if fd_applies_to(fd, x_ret) and not rhs.issubset(x_ret):
                x_ret = x_ret.union(rhs)
                if verbose:
                    print("Using FD " + fd_to_str(fd))
                    print("\t Updated x to " + set_to_str(x_ret))
                bChanged = True
    return x_ret

def is_fd_implied(fds, lhs, rhs, verbose=False):
    """Check if lhs -> rhs is implied by the given set of fds"""
    xp = compute_closure(lhs,fds,verbose=verbose)
    if verbose: print(set_to_str(lhs) +"+ = "+ set_to_str(xp))
    return to_set(rhs).issubset(xp)

def is_superkey(A,B,fds, verbose=False):
    """Check if A is a super key in B according to the fds"""
    return is_fd_implied(fds, A, B)

import itertools
def is_key(A,B,fds,verbose=False):
    """Check if A is a key in B wrt to fds"""
    m=len(A)
    subsets = set(itertools.combinations(A, m-1))
    return is_superkey(A,B,fds) and all(not is_superkey(set(SA),B,fds) for SA in subsets)

#
# Key example from lecture
#
def key_example():
    xmC=set(["A","B"])
    xmB=set(["A","C"])
    xmA=set(["B","C"])
    B  =set(["A","B","C"])

    fd1=(xmC,"C"); fd2=(xmB,"B"); fd3=(xmA,"A")
    fds=[fd1,fd2,fd3]

    return is_key(xmA,B,fds) and is_key(xmB,B,fds) and is_key(xmC,B,fds)


from IPython.core.display import display_html, HTML
def to_html_table(res, style=None):
    html = '<table' + (' style="' + style + '"' if style else '') + '><tr><th>'
    html += '</th><th>'.join(res.keys) + '</th></tr><tr><td>'
    html += '</td></tr><tr><td>'.join(['</td><td>'.join([str(cell) for cell in row]) for row in list(res)])
    return html + '</tr></table>'
def display_side_by_side(l, r):
    s = "display: inline-block;"
    html = to_html_table(l, style=s) + ' ' + to_html_table(r, style=s)
    display_html(HTML(data=html))
