# How to release zugbruecke

1. Merge all relevant changes into branch `develop` - this is where development and pre-release testing happens.

2. In branch `develop`, run tests and examples and check that the documentation builds without errors.

```bash
make test
```

3. In branch `develop`, add missing changes to `CHANGES.md` and commit.

4. Push branch `develop` to GitHub.

5. Wait for feedback from CI.

6. Change to branch `master`.

7. Merge branch `develop` into branch `master` (comment `f"{version:s} release"`).

8. Push branch `master` to GitHub.

9. Tag branch `master` with `f"v{version:s}"`.

```bash
git tag "v0.0.1"
```

10. Push the tag to Github.

```bash
git push origin --tags
```

11. Build and sign packages.

```bash
make release
```

12. Upload package to `pypi`.

```bash
make upload
```

13. Change to branch `develop`.

14. In branch `develop`, bump the package version in `src/zugbruecke/__init__.py` by changing the `__version__` string.

15. In `CHANGES.md`, indicate that a new development cycle has started.

16. Commit to branch `develop`.

17. Push branch `develop` to GitHub.
