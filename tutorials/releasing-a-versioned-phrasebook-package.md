# Releasing a versioned Phrasebook package

## Purpose and scope

This tutorial shows content engineers how to prepare a versioned content release, validate resources, prepare files, submit changes through Git, and respond to QA feedback.

**Portfolio note:** Phrasebook is a fictional travel-phrase app created for this tutorial. Its product terminology, tools, file formats, ticket IDs, naming rules, and repository paths are illustrative examples, not details from a real product or any company's internal process.

## Overview

The Phrasebook app contains two resource types:

- **Glossaries:** Terms and their translations for a language.
- **Phrase sets:** Topic-based phrases, such as checking out of a hotel. Phrase sets import one or more glossaries.

The release process covers resource preparation, validation and testing, file export, Git version control, and quality assurance (QA).

## Contents

- [Prerequisites](#prerequisites)
- [1. Prepare the release](#1-prepare-the-release)
- [2. Validate the resources](#2-validate-the-resources)
- [3. Export and prepare the files](#3-export-and-prepare-the-files)
- [4. Submit the files through Git](#4-submit-the-files-through-git)
- [5. Complete QA](#5-complete-qa)
- [6. Troubleshooting](#6-troubleshooting)
- [7. Final checklist](#7-final-checklist)
- [Verification and limitations](#verification-and-limitations)

## Prerequisites

You need:

- A Linux environment with Bash and `unzip`; Python 3 is required for the optional XML syntax check.
- Access to the fictional content editor and release ticket.
- Access to the `phrasebook-content` Git repository, with permission to create branches and pull requests.

## Conventions

These conventions apply to the fictional example.

| Item | Convention |
|---|---|
| Release ticket | `REL-208` |
| App version | `4.7.0` |
| Resource version | `<app version>-r<revision>`, for example, `4.7.0-r12` |
| Resource name | `<locale>-<kind>-<topic>`, using lowercase letters, digits, and hyphens |
| Example names | `en-glossary-core`, `de-phrases-checkout` |
| Export format | `<resource name>.gpack`, containing one extensionless XML file named after the resource |
| Version metadata | The XML root element's `version` attribute, not the filename |
| Repository | `phrasebook-content` |
| File layout | `content/<locale>/<glossary or phrases>/<resource name>.xml` |
| Default branch | `main` |

All resources in a release use the same app version. Each resource has its own revision. Increase the revision by one when that resource's content changes; otherwise, keep it unchanged.

Resource names contain no dots. This lets the renaming command distinguish extensionless resource files from files that already have extensions.

## 1. Prepare the release

### 1.1 Confirm the ticket and versions

Check that the release ticket specifies the correct app version. For this example, the ticket is `REL-208` and the app version is `4.7.0`.

In the content editor, set each resource's version. For example, `4.7.0-r12` means app version `4.7.0`, revision 12. The resource content stores the version, which is included in the export. The filename does not contain the version.

### 1.2 Add change summaries

For each resource, complete the **Change summary** field in the content editor. Include any deprecated terms, meaning terms no longer used in new content but retained for older app versions.

## 2. Validate the resources

### 2.1 Validate glossaries

Run the content editor's validation checks for each glossary and resolve all errors and warnings.

**If you cannot resolve an issue:** Stop and report it in the release ticket. Include the error messages and what you tried. Do not continue until the issue is resolved or the relevant team agrees on next steps.

### 2.2 Import glossaries and test phrase sets

1. **Export** the glossaries required by the phrase sets. These exports are for importing into phrase sets; they are not the final release files.
2. **Import** each glossary into the phrase sets that use it.
3. Validate each phrase set and run its automated tests.

The required pass rate is **100%, with no errors or warnings**. If a check fails, investigate and fix the underlying issue, then repeat validation and testing. If you cannot resolve it, follow the escalation procedure in [Section 2.1](#21-validate-glossaries) and add the test results to the ticket.

## 3. Export and prepare the files

### 3.1 Export resources

Export every resource in the release from the content editor, including glossaries and phrase sets. Each export is named `<resource name>.gpack`; for example, `en-glossary-core.gpack`. The resource version remains in the exported content, not the filename.

Save the `.gpack` files in a dedicated working directory. The commands below assume that directory is your current directory.

### 3.2 Extract the archives

A `.gpack` file is a ZIP archive containing an extensionless XML file named after the resource. Inspect an archive with:

```bash
unzip -l en-glossary-core.gpack
```

Extract one archive:

```bash
unzip en-glossary-core.gpack
```

To extract all archives in the current directory:

```bash
shopt -s nullglob
archives=( *.gpack )

if ((${#archives[@]} == 0)); then
    echo "No .gpack archives found." >&2
else
    for file in "${archives[@]}"; do
        unzip "$file" || exit 1
    done
fi
```

**Avoid filename conflicts:** If two archives contain a file with the same name and you extract both into the same directory, `unzip` normally asks before overwriting the existing file. If you confirm, the later extraction can replace the earlier file. Options such as `-o` suppress the prompt and overwrite existing files. Inspect the archives first and extract conflicting files into separate directories:

```bash
unzip en-glossary-core.gpack -d extracted_a
unzip de-phrases-checkout.gpack -d extracted_b
```

Verify filenames before copying files into the repository.

### 3.3 Add the `.xml` extension

Run this Bash command in a directory containing only the extracted resource files you intend to rename:

```bash
for file in *; do
    if [ -f "$file" ] && [[ "$file" != *.* ]]; then
        if [ -e "$file.xml" ]; then
            echo "Target already exists: $file.xml" >&2
            exit 1
        fi
        mv -- "$file" "$file.xml"
    fi
done
```

The command appends `.xml` to regular files whose names contain no dot. It stops if the target filename already exists, preventing accidental overwrites. If you extracted archives into separate directories, rename the files in those directories.

Check the filenames:

```bash
ls -1
```

Confirm that each resource has the expected `.xml` filename before copying it into the repository.

### 3.4 Check XML syntax (optional)

To check whether the XML files are well-formed, run:

```bash
python3 - <<'PY'
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

files = sorted(Path(".").glob("*.xml"))
if not files:
    sys.exit("No XML files found.")

failed = False
for path in files:
    try:
        ET.parse(path)
        print(f"{path}: valid XML")
    except ET.ParseError as exc:
        print(f"{path}: invalid XML: {exc}")
        failed = True

if failed:
    sys.exit(1)
PY
```

This checks XML syntax only. It does not verify content correctness or compatibility with an application.

## 4. Submit the files through Git

### 4.1 Update the local repository

Navigate to the local `phrasebook-content` repository.

Fetch the latest remote changes and update the local `main` branch:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

`--ff-only` prevents Git from creating a merge commit. If the pull fails because the branches have diverged, stop and follow your team's integration procedure or consult the repository maintainer; do not force the histories together.

### 4.2 Create a release branch

Use the release ticket ID as the branch name:

```bash
git switch -c REL-208
```

### 4.3 Copy the prepared files

The repository uses this layout:

```text
content/<locale>/<glossary or phrases>/<resource name>.xml
```

List tracked XML files to find comparable resources and confirm the directory structure:

```bash
git ls-files '*.xml'
```

Copy the prepared XML files into their corresponding locations. Run the following commands with the repository as your working directory, replacing the source path with the actual location of your extracted files:

```bash
cp /path/to/extracted/en-glossary-core.xml content/en/glossary/
cp /path/to/extracted/de-phrases-checkout.xml content/de/phrases/
```

The source paths and destination layout are illustrative. If a destination is unclear, consult the repository documentation or maintainer.

### 4.4 Review and stage the changes

Check the working tree:

```bash
git status
```

Stage only the intended files:

```bash
git add content/en/glossary/en-glossary-core.xml \
        content/de/phrases/de-phrases-checkout.xml
```

Review the staged changes before committing. The first command summarizes the staged changes. The second displays their contents:

```bash
git diff --cached --stat
git diff --cached
```

Confirm that the correct files and content are staged. To unstage a file added by mistake, replace `FILE_PATH` with the path of the file you want to unstage:

```bash
git restore --staged FILE_PATH
```

### 4.5 Commit, push, and open a pull request

Use this fictional commit-message format:

`<ticket ID>: Content release <app version>`

For example:

```bash
git commit -m 'REL-208: Content release 4.7.0'
git push -u origin REL-208
```

Open a pull request against `main`. Include the release ticket ID and a concise change summary, and confirm that the intended XML files are included.

## 5. Complete QA

The QA team imports the files into a test environment and runs the required tests.

### If QA reports issues

1. Review the feedback in the release ticket.
2. Identify the affected resources or files.
3. If resource content needs to change, correct it in the content editor and rerun the relevant validation and automated tests.
4. Re-export the updated resource, extract it, add the `.xml` extension, and copy it to the correct repository location.
5. Stage and review the change. Replace `FILE_PATH` with the path of the file you want to stage:

   ```bash
   git add FILE_PATH
   git diff --cached --stat
   git diff --cached
   ```

6. Commit and push the fix to the existing release branch. For example:

   ```bash
   git commit -m 'REL-208: Fix missing term in en-glossary-core'
   git push
   ```

7. Request QA retesting.

If the correction affects only a repository file, repeat only the applicable steps. If you cannot resolve the issue, follow the escalation procedure in [Section 2.1](#21-validate-glossaries). QA feedback remains in the same release ticket, and pushing to the existing branch updates its pull request.

### If QA approves the release

Merge the pull request according to the project's established workflow.

## 6. Troubleshooting

| Problem | Action |
|---|---|
| Validation errors or warnings cannot be resolved | Stop and follow the escalation procedure in [Section 2.1](#21-validate-glossaries). |
| No `.gpack` files are found | Run `pwd` and `find . -maxdepth 1 -type f -name '*.gpack' -print`. Move to the directory where you saved the exports if needed. |
| Expected extracted files are missing | Inspect the archive with `unzip -l file.gpack`; check the extraction directory and source/destination paths. |
| Two archives contain files with the same name | Extract them into separate directories and verify filenames before copying. |
| A file was not renamed | The command skips names containing a dot. Check the filename and rename it manually if appropriate. |
| XML syntax check fails | Review the reported file and parsing error. Correct the resource in the content editor and re-export it rather than editing the exported XML by hand. |
| Repository destination is unclear | Run `git ls-files '*.xml'` and compare resources with the same locale and type; ask the maintainer if needed. |
| Unexpected Git changes appear | Run `git status` and inspect a file with `git diff -- FILE_PATH` before staging or committing. Replace `FILE_PATH` with the file path. |
| `git commit` says no changes are staged | Stage the intended paths with `git add`, then review with `git diff --cached --stat`. |
| `git pull --ff-only` fails | Check `git status` and `git log --oneline origin/main..main`. Follow the team's integration procedure or ask the maintainer before reconciling divergent history. |
| Shell reports `[[: not found` | Run the command in Bash, not `sh`. |

## 7. Final checklist

Before submitting for QA, confirm that:

- [ ] The ticket and app version are correct.
- [ ] Resource versions, revisions, and change summaries are correct.
- [ ] Glossaries and phrase sets pass validation, and automated tests meet the release requirement.
- [ ] Required glossaries have been imported into phrase sets.
- [ ] Exported files have been extracted, renamed, and copied to the correct repository locations.
- [ ] Only the intended files are staged, and the staged diff has been reviewed.
- [ ] The branch, commit message, and pull request follow the conventions above.

After QA approval, merge the pull request according to the project's workflow.

## Verification and limitations

The Bash extraction and renaming commands were tested on Ubuntu 24.04.1 LTS using Bash 5.2.21 and synthetic ZIP archives. The sample XML files were checked for well-formedness with Python's XML parser. Git file discovery, staging, diff review, and commit commands were tested with Git 2.53.0 in a local repository containing one new and one modified XML file.

These tests verify the command behavior described above; they do not demonstrate compatibility with a real product. The `.gpack` format and repository structure are fictional examples. Pushing a branch and opening a pull request were not tested.
