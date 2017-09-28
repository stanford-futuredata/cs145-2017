# CS145 Setup Instructions

## Step 1: Installing Jupyter Notebook

### _Recommended:_ Installation via Anaconda
We recommend that you install via Anaconda:

1. Download & install Anaconda for Python 2.7 [here](https://www.continuum.io/downloads)
2. Run `jupyter notebook` to confirm that the installation worked!


### Installation via `pip`
You can also install via the Python package manager `pip`:

1. First, make sure you have installed:
	* [Python 2.7](https://www.python.org/about/gettingstarted/)
	* [pip](https://pip.pypa.io/en/stable/installing/)

1. Make sure you have upgraded `pip` to the latest version:
	
	```
	pip install --user --upgrade pip
	```

2. Intall Jupyter notebook:
	
	```
	pip install --user --upgrade jupyter
	```

_Note that if you have `sudo` permissions, you can install system-wide by prepending `sudo` to the above commands, and removing `--user`; sometimes this will resolve certain installation issues._

**_Note: If you have any install issues, see our Troubleshooting Guide below!_**


## Step 2: Installing Other Dependencies

### Git
Git is a version control system which we use to store the various course materials; you can install by following instructions [here](https://git-scm.com/downloads)

### IPython-SQL
`ipython-sql` allows you to use SQL queries nicely inside jupyter notebooks; install using pip:

```
pip install --user --upgrade ipython-sql
```


## Step 3: Getting Started!

### Getting the latest course materials
You can always access the latest course materials on the course website, however you can also get them all at once, and keep them synced, by using git.  To get started with this method, run:

```
git clone https://github.com/stanford-futuredata/cs145-2017.git
```

Now you should have all the materials in a `cs145-2017` folder; to get the latest versions, just run:

```
git pull
```

### Running stuff
In the directory where the relevant course materials are (if you followed the above step, this will be in the `cs145-2017` directory), run:

```
jupyter notebook
```

# Troubleshooting Guide
 
If you're having trouble installing IPython notebook, look through the following fixes & try ones that seem potentially relevant.  If none of the below work then post your issue on Piazza!
 
Remember, we don't "officially" support Windows, but the CA staff will do their best to help with Windows install issues!

### Anaconda doesn't have jupyter:

You can try additionally running:

```
conda install jupyter
```
 
### "Missing module" error:
One way to debug if you get error messages of the form "No module named XXX" is to try installing XXX.  If you've gotten this far using pip, you can try using it in the same way to install these missing modules (for example module "XXX"):

```
pip install --user --upgrade XXX 
```

If this doesn't work, you can try looking online for how to install the missing module most easily on your specific system
 
### Re-installing pip: 
If you installed pip via a package manager, and are having issues- or are just having issues in general- try re-installing / upgrading pip (via the instructions linked in Step 1 of the install post) first!
 
### Python 2.7:
Ideally you are using this version- make sure you are not using Python 3!
 
### On running as sudo:
If you have sudo access, and want to run the install commands as sudo, leave the `--user` flag out!
 
### Distribute error:
If you get an error referencing the "Distribute" library and/or 'maximum recursion depth exceeded', you could try running

```
pip install --upgrade distribute
```
 
### "Command jupyter not found":
A lot of issues arise when jupyter & other dependencies get installed correctly, but then the OS doesn't know where to find them.  When you type in a command such as `jupyter notebook`, your system looks for the "jupyter" executable in all of the directories listed in your `PATH` environment variable.  You may need to add the directory where you installed jupyter or pip to your `PATH` variable...
 
For example, if you successfully installed jupyter but it's complaining that the command is not found, try adding `~/Library/Python/2.XXX/bin` and `~/bin` to your path.

If `XXX` = your version of python, probably 2.7 i.e. on Mac OS / linux, in your `~/.bash_profile` or `~/.bashrc`, add the line:

```
export PATH=${PATH}:~/Library/Python/2.XXX/bin:~/bin
```

Then after running that, you should be able to execute the command `which jupyter` and have it show you where jupyter is located.

**Note: you need to quit and restart your terminal in order for these changes to take effect!**
