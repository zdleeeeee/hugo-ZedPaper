# ZedPaper

ZedPaper is a responsive Hugo blog theme substantially adapted from [PaperMod](https://github.com/adityatelange/hugo-PaperMod). It is available under the MIT License.

> [!WARNING]
> ZedPaper is under active development. The theme's structure, configuration
> keys, and default styles may change without notice between commits. Pin to a
> specific commit if you need stability, and expect breaking changes when you
> update.

Enable it in your Hugo configuration:

```toml
theme = 'ZedPaper'
```

## Install

Inside the folder of your Hugo site `MySite`, run:

```bash
git submodule add --depth=1 https://github.com/zdleeeeee/hugo-ZedPaper.git themes/ZedPaper
git submodule update --init --recursive # needed when you reclone your repo (submodules may not get cloned automatically)
```

## Pull Update from Official ZedPaper Repo

Inside the folder of your Hugo site `MySite`, run:

```bash
git submodule update --remote --merge
git add themes/ZedPaper
git commit -m "Update ZedPaper"
git push origin main
```

## Example

See an example at: [Zed's Blog](https://zdleeeeee.github.io/) .