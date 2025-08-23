## Std management of libraries

ED_ is a dummy library structure.

In general, libraries will be included as submodules added as subfolders of lib using the command, for instance

```
git submodule add https://github.com/edolis/ED_JSO.git lib/git_ED_JSON
```
remember a commit is required before compilation
```
git commit -m "Added submodule git_ED_JSON"
```

## Library development
the library will have to be generated in a separate folder and put under its own git versioning
    - copy the structure and contents of ED_ to a folder
    - initiate git:

    ```
    git init

    git add .
    git commit -m "Setup commit"
    ```

For development, add it as a submodule of the main code project as described before.

### Attention
in this setup, discipline in commits is required to avoid parallel edit take place and merge is required.
If the situation cannot be avoided, at least use branching of the repository so that merging is more supported (*to be verified*)
