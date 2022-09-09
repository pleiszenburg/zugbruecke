# How to contribute to *zugbruecke*

Thank you for considering contributing to `zugbruecke`! **Contributions are highly welcomed!**

## Reporting issues

Issues are tracked on [Gitbub](https://github.com/pleiszenburg/zugbruecke/issues).

- Read the section on [bugs](docs/bugs.rst) in `zugbruecke`'s documentation.
- Describe what you expected to happen.
- If possible, include a [minimal, complete, and verifiable example](https://stackoverflow.com/help/mcve) to help identify the issue. This also helps check that the issue is not with your own code.
- Describe what actually happened. Include the full traceback if there was an exception.
- Enable logging at the highest level (100) and add the log if possible.
- If logging does not seem to work, let `zugbruecke` write its logs into files.
- List your operating system, *CPython*, *Wine*, `zugbruecke` and `wenv` versions. If possible, check if this issue is already fixed in the repository (development branch).

## Project philosophy

A few rules, describing how this project is being developed:

- `zugbruecke` is a drop-in replacement for `ctypes`.
- Whatever works with `ctypes` under *Windows* / *Wine* is supposed to work with `zugbruecke` under *Unix*.
- Keep interference with users' code at a minimum. I.e. do not make users write plenty of `if`-statements for handling platform-specific behavior. The `memsync` protocol, which is just ignored by `ctypes` on *Windows* / *Wine*, is a good example of how to implement no-interfering platform-specific behavior.
- `zugbruecke` is supposed to throw the exact same exceptions as `ctypes` does.
- Tests have to work equally with `ctypes` under Wine (`wenv`) and with `zugbruecke` under *Unix*. Have a look at the implementation of `make test` for clarification.
- If something does not work with `ctypes` under *Windows* / *Wine*, `zugbruecke` is not expected to do it either. In this case, submit a patch to "upstream" *CPython* instead first. Exceptions can be made if extra features are required for platform interoperability, like for instance converting paths from Unix to Windows format or vice versa.
- Code maintainability comes first (until further notice), speed second. Speed does not hurt, though, and a lot of code could use some improvements.
- Security has not been a primary concern so far, but it could use a lot of improvement.
- Unimplemented `ctypes` routines and classes are offered as stubs.
- Stuff related to managing *Wine* and *CPython* for Windows (on top of *Wine*) mainly belongs into the closely related [wenv project](https://github.com/pleiszenburg/wenv).

## Submitting patches

- Include tests if your patch is supposed to solve a bug or add a missing feature, and explain clearly under which circumstances the bug happens or what was missing. Make sure the test fails with `zugbruecke` without your patch, while it must work with `ctypes` on *Wine*.
- No, there is no line limit. Let your editor wrap the lines for you, if you want.
- Add as many comments as you can - code-readability matters.
- The `master` branch is supposed to be stable - request merges into the `develop` branch instead. Branch from `develop` when working on something.
- Commits are preferred to be signed (GPG). Seriously, sign your code.

**Looking for work?** Check `zugbruecke`'s [open issues](https://github.com/pleiszenburg/zugbruecke/issues). The closely related `wenv` project also happens to have [separate open issues](https://github.com/pleiszenburg/wenv/issues).

**Not sure where to go or what to do?** Get in touch via the project's [mailing list](https://groups.io/g/zugbruecke-dev) of [chat room](https://matrix.to/#/#zugbruecke:matrix.org)!

## First time setup for developers

- Make sure you have *Wine* >= 6.x and *CPython* 3.x installed.
- Make sure you have the *mingw* cross compiler installed for compiling the *Windows* test DLLs.
- Download and install the [latest version of git](https://git-scm.com/downloads).
- Configure git with your [username](https://help.github.com/articles/setting-your-username-in-git/) and [email](https://help.github.com/articles/setting-your-email-in-git/):

```bash
git config --global user.name 'your name'
git config --global user.email 'your email'
```

- Make sure you have a [GitHub account](https://github.com/join).
- Fork `zugbruecke` to your GitHub account by clicking the [Fork](https://github.com/pleiszenburg/zugbruecke#fork-destination-box) button.
- [Clone](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository) your GitHub fork locally:

```bash
git clone git@github.com:{username}/zugbruecke
cd zugbruecke
```

- Add the main repository as a remote:

```bash
git remote add upstream https://github.com/pleiszenburg/zugbruecke
git fetch upstream
```

- Set your main branch (probably ``develop``) to track upstream using

```bash
git branch --set-upstream-to=upstream/develop
```

- Create a CPython (3) virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

- Install `zugbruecke` in editable mode with development dependencies. This step will take a while - there is a lot of stuff happening on the *Wine* side of things.

```bash
make install
```

- Run the test suite and confirm that the development environment is fully functional:

```bash
make test
```

- You may also want to check of the documentation is building:

```bash
make docs
```

## Useful helpers

Have a look at the `wenv python`, `wenv pip` and `wenv pytest` commands as well as `wenv help`, `wenv init`, `wenv clean` and `wenv init_coverage`. They actually work as one would expect ;) If you want, you can also write executable scripts and add `#!/usr/bin/env _wenv_python` at their top. Check `import os; os.name`, it will return `nt`. Check the section on the [Wine Python environment](docs/source/wineenv.rst) in the documentation.
