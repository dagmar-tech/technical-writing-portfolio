# Releasing a Versioned Phrasebook Package

## Purpose and Audience

This tutorial guides content engineers and maintainers through preparing and releasing a versioned content package, from validation and file preparation to Git submission and QA approval.

**Note on the scenario:** Phrasebook is a fictional product created for this portfolio sample. Product terminology, tool names, file formats, ticket IDs, naming rules, and repository structures are illustrative. The tutorial demonstrates a generalized release workflow and is not intended to document any company's internal procedure.

## Overview

Phrasebook is a fictional travel-phrase app. Its content team maintains two kinds of resources:

- **Glossaries:** Lists of terms and their translations for a particular language.
- **Phrase sets:** Ready-made phrases for a topic, such as checking out of a hotel. A phrase set imports one or more glossaries.

A release covers resource preparation, change summaries, validation, file export and preparation, Git version control, and quality assurance (QA).

The examples use illustrative ticket IDs and version numbers.

## Prerequisites

Before starting, ensure you have access to:

- **Command line:** A Linux environment with Bash and the `unzip` utility. Python 3 is needed for the optional XML syntax check described in [Section 3.3](#33-add-the-xml-extension).
- **Git:** Access to the `phrasebook-content` repository and permission to create branches and pull requests.
- **Issue tracking system:** Access to the release ticket and its QA feedback.
- **Content editor:** Access to the fictional editor used to maintain, validate, and export resources.

## Conventions Used in This Tutorial

The following conventions belong to the fictional Phrasebook scenario.

| Item | Convention |
|---|---|
| Release ticket | `REL-208` |
| Target app version | `4.7.0` |
| Resource version | `<app version>-r<revision>`, for example `4.7.0-r12` |
| Resource names | `<locale>-<kind>-<topic>`, using lowercase letters, digits, and hyphens |
| Example resource names | `en-glossary-core`, `de-phrases-checkout` |
| Exported files | `<resource name>.gpack`, with each archive containing one extensionless XML file named after the resource |
| Version metadata | Stored in the `version` attribute of the XML root element, not in the filename |
| Repository | `phrasebook-content` |
| Repository structure | `content/<locale>/<glossary or phrases>/<resource name>.xml` |
| Default branch | `main` |

The revision number increases by one when a resource's content changes in a release. If the content has not changed, its revision number remains unchanged.

Resource names never contain dots. This convention allows the file-renaming command in [Section 3.3](#33-add-the-xml-extension) to distinguish extensionless resource files from files that already have extensions.

## 1. Prepare the Release

### 1.1 Review the Release Ticket

The QA lead creates the release ticket and specifies the target app version. The ticket is the central place for release-related communication and QA feedback.

For this example, the ticket ID is `REL-208`, and the target app version is `4.7.0`.

Before proceeding, confirm that the ticket identifies the correct app version.

### 1.2 Update Resource Versions

Open each resource in the content editor and set its version according to the conventions described above.

For example, `4.7.0-r12` means app version `4.7.0`, revision 12.

All resources in the same release share the app version, but each resource has its own revision number. Increase the revision by one when the resource's content changes in the release; otherwise, leave the revision unchanged.

The version information is stored in the resource content and is included in the exported resource. It is not part of the exported filename.

### 1.3 Prepare the Change Summary

For each resource, enter a summary of the changes in the **Change summary** field in the content editor.

Review the resource for deprecated terms—terms removed from active use but retained for older app versions—and list them in the summary.

## 2. Validate the Resources

### 2.1 Validate the Glossaries

Open each glossary and run the content editor's validation checks.

Resolve all errors and warnings before continuing.

**Escalation rule:** If you cannot resolve an error or warning, stop the release process and report the issue in the release ticket's comments as soon as possible. Include the relevant error messages and explain what you have tried so far. Do not proceed until the issue has been resolved or the next steps have been agreed with the relevant team.

### 2.2 Export the Glossaries for Import

Phrase sets use terms from glossaries, so the glossaries must be imported into the phrase sets before those phrase sets can be tested.

Use **Batch Export** to export the glossaries required for the release.

These exports are used for the import in the next step; they are not the release files. The release files are produced in [Section 3](#3-export-and-prepare-the-resource-files).

### 2.3 Import the Glossaries into the Phrase Sets

Use **Batch Import** to import the exported glossaries into the phrase sets that use them. This makes the required glossary content available for running autotests.

### 2.4 Validate the Phrase Sets and Run Automated Tests

Validate each phrase set, then run the automated test suite for the phrase sets.

The required result is **100%, with no errors or warnings**.

If errors or warnings occur, investigate and correct the underlying issues, then repeat validation and testing.

If you cannot resolve an issue or achieve the required result, follow the [escalation rule in Section 2.1](#21-validate-the-glossaries). Include the test results and relevant error messages in the release ticket's comments.

## 3. Export and Prepare the Resource Files

### 3.1 Export Each Resource

Export every resource included in the release, including glossaries and phrase sets, using the content editor's **Export** command.

The exported filename matches the resource name, with the `.gpack` extension. For example, `en-glossary-core` is exported as `en-glossary-core.gpack`.

The resource version is stored in the exported resource content, not in the filename.

### 3.2 Extract the Exported Files

After exporting the resources, save all `.gpack` files to a dedicated working directory on your local machine. The following commands assume you are working in this directory.

The exported `.gpack` files are ZIP archives containing extensionless XML files named after their resources.

To inspect an archive before extraction:

```bash
unzip -l en-glossary-core.gpack
```

To extract one archive:

```bash
unzip en-glossary-core.gpack
```

To extract all `.gpack` archives in the current directory:

```bash
shopt -s nullglob
archives=( *.gpack )

if ((${#archives[@]} == 0)); then
    echo "No .gpack archives found." >&2
else
    for file in "${archives[@]}"; do
        unzip "$file"
    done
fi
```

This Bash command finds all `.gpack` archives in the current directory and extracts each one.

**Important:** Inspect the archive contents before extracting multiple archives into the same directory. If different archives contain files with identical names, extraction may overwrite files or prompt you to resolve conflicts.

Extract archives with duplicate filenames into separate directories instead:

```bash
unzip en-glossary-core.gpack -d extracted_a
unzip de-phrases-checkout.gpack -d extracted_b
```

Check the filenames in each extracted directory before copying files into the repository. This helps prevent an existing resource file from being overwritten by another file with the same name.

### 3.3 Add the `.xml` Extension

The extracted resource files have no file extension. From the working directory containing the extracted resource files, append `.xml` to each extensionless regular file:

```bash
for file in *; do
    if [ -f "$file" ] && [[ "$file" != *.* ]]; then
        mv -- "$file" "$file.xml"
    fi
done
```

The command:

- Iterates over directory entries.
- Selects regular files whose names contain no dot.
- Appends `.xml` to each matching filename.
- Leaves files that already have extensions unchanged.

For example, `en-glossary-core` becomes `en-glossary-core.xml`, and `de-phrases-checkout` becomes `de-phrases-checkout.xml`.

**Important:** Run this command only in a directory containing the extracted resource files. It assumes that every extensionless regular file in that directory is a resource file that should receive the `.xml` extension.

Because resource names never contain dots, the command can distinguish extensionless resource files from archives such as `.gpack` files.

If a file with the target `.xml` name already exists, the command replaces it. This can occur when re-exporting a resource after QA feedback. Confirm that you are in the correct working directory before running the command.

If you extracted archives into separate directories to avoid filename conflicts, rename the files in their respective directories before copying them to the repository.

Verify the results:

```bash
ls -1
```

The listing should show one `.xml` file per exported resource alongside the `.gpack` archives, with no remaining extensionless resource files.

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

This checks XML syntax, not whether the content is semantically correct or compatible with a particular application.

## 4. Commit the Files to Git

### 4.1 Update the Local Repository

Navigate to the local `phrasebook-content` repository.

Fetch the latest remote changes and update the local `main` branch:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
```

The `--ff-only` option prevents Git from creating a merge commit when updating the local branch.

If the pull fails because the local branch and remote branch have diverged, consult [Section 6](#6-troubleshooting) before proceeding.

### 4.2 Create a Release Branch

Create a new branch using the release ticket ID as its name:

```bash
git switch -c REL-208
```

### 4.3 Add the XML Files

Identify the destination directories in the repository before copying the prepared XML files.

Resource files are stored under:

```text
content/<locale>/<glossary or phrases>/<resource name>.xml
```

You can confirm the existing structure by listing tracked XML files:

```bash
git ls-files '*.xml'
```

This command lists tracked XML files, including files in nested directories. Find comparable resources and follow the same directory structure.

If the correct location is unclear, consult the repository documentation or maintainer before proceeding.

Copy the prepared XML files into their corresponding locations. Run the following commands with the repository as your working directory, replacing the source path with the actual location of your extracted files:

```bash
cp /path/to/extracted/en-glossary-core.xml content/en/glossary/
cp /path/to/extracted/de-phrases-checkout.xml content/de/phrases/
```

**Note:** The source paths are placeholders. The destination paths illustrate the fictional repository structure defined above.

#### Check and Stage the Changes

Check the working tree to confirm which files have been added or modified:

```bash
git status
```

Stage the intended resource files, using their paths relative to the repository root:

```bash
git add content/en/glossary/en-glossary-core.xml \
        content/de/phrases/de-phrases-checkout.xml
```

Review the staged changes before committing:

```bash
git diff --cached --stat
git diff --cached
```

The first command summarizes the staged changes. The second displays their contents.

Confirm that the correct XML files are staged and that the changes are as expected. If a file was staged by mistake, unstage it with:

```bash
git restore --staged <path>
```

### 4.4 Commit the Changes

Use the fictional commit-message convention:

`<ticket ID>: Content release <app version>`

For example:

```bash
git commit -m 'REL-208: Content release 4.7.0'
```

Replace the example ticket ID and app version with the values for the actual release.

### 4.5 Push the Branch and Open a Pull Request

Push the release branch to the remote repository:

```bash
git push -u origin REL-208
```

Open a pull request against the `main` branch. Include the release ticket ID and a summary of the changes.

Before submitting, confirm that the correct XML files are included and that the changes are ready for QA review.

## 5. QA and Release Approval

After the pull request is submitted, the QA team imports the XML files into a test environment and runs the required tests.

### If QA Identifies Issues

1. Review the feedback recorded in the release ticket's comments.
2. Investigate the reported problems and identify the affected resources or files.
3. If a resource must be changed, make the correction in the content editor and rerun the applicable validation checks and automated tests.
4. Re-export the updated resource.
5. Extract the exported `.gpack` file, add the `.xml` extension to the extracted file, and copy it to the appropriate repository location.
6. Stage the updated XML file with `git add`, then review the staged changes with `git diff --cached --stat` and `git diff --cached`.
7. Commit the fix using the ticket ID followed by a short description. For example:

   ```bash
   git commit -m 'REL-208: Fix missing term in en-glossary-core'
   ```

8. Push the updated release branch to `origin` and request QA retesting.

If the correction involves only a repository file and does not require changing the resource in the content editor, repeat only the applicable steps.

If you cannot resolve a reported problem, follow the [escalation rule in Section 2.1](#21-validate-the-glossaries).

QA feedback and follow-up communication remain recorded in the same release ticket. Pushing corrections to the existing release branch updates its pull request, provided that the project's workflow continues to use that branch.

### If QA Approves the Release

Once QA confirms that the files meet the release requirements, merge the pull request according to the project's established workflow.

## 6. Troubleshooting

| Problem | Suggested action |
|---|---|
| Validation reports errors or warnings that you cannot resolve | Follow the [escalation rule in Section 2.1](#21-validate-the-glossaries). |
| No `.gpack` archives are found | Run `pwd` to confirm the current working directory, then `find . -maxdepth 1 -type f -name '*.gpack' -print` to list matching archives. If none are found, move to the directory where you saved the exported files. |
| Extracted files have no extensions | This is expected. Run the extension-renaming command in [Section 3.3](#33-add-the-xml-extension) from the directory containing the extracted resource files. |
| A resource file was not renamed | The command skips names that contain a dot. Run `ls -1` to find the file, check its name against the naming convention, and rename it manually if needed. |
| Expected XML files are missing | Run `unzip -l file.gpack` to inspect an archive's contents, then `ls -1 *.xml` in the extraction directory to see which XML files were produced. Check the source and destination paths used when copying the files. |
| Two archives contain files with duplicate names | Inspect both archives with `unzip -l file.gpack`. Extract them into separate directories using `unzip file.gpack -d <dir>`, then verify the filenames before copying the files into the repository. |
| An XML syntax check fails | Inspect the reported filename and parsing error. Correct the resource in the content editor and re-export it rather than editing the exported XML by hand. |
| The correct repository destination is unclear | Run `git ls-files '*.xml'` to list tracked XML files, including nested paths. Use existing resources with the same locale and kind to identify the destination. Consult the repository documentation or maintainer if the location remains unclear. |
| Git reports unexpected changes | Run `git status` to list changed and untracked files. If a file was staged accidentally, run `git restore --staged <path>` to unstage it. If an existing file contains unexpected edits, inspect them with `git diff <path>` before committing. |
| `git commit` reports `no changes added to commit` | No changes are staged. Run `git add <paths>` for the intended files, then check them with `git diff --cached --stat` before committing. |
| `git pull --ff-only` fails | The local and remote branches may have diverged. Run `git status`, fetch the latest remote information with `git fetch origin`, and run `git log --oneline origin/main..main` to inspect commits present on local `main` but not on `origin/main`. Follow the project's integration procedure or consult the repository maintainer before reconciling divergent history. |
| The shell reports `[[: not found` | The script uses Bash syntax. Run it in Bash rather than `sh`, for example by saving it as a `.sh` file and invoking `bash script.sh`. |

## 7. Final Checklist

Before submitting the release for QA, confirm that:

- [ ] The release ticket identifies the correct app version.
- [ ] All resources have the correct version numbers and revisions.
- [ ] Each resource's Change summary is complete and lists any deprecated terms.
- [ ] Glossary validation, phrase-set validation, and automated tests meet the release requirements, with no errors or warnings.
- [ ] The glossaries have been exported and imported into the corresponding phrase sets.
- [ ] The exported resource files have been extracted, renamed with the `.xml` extension, and copied into the correct repository locations.
- [ ] The intended XML files are staged, and the staged changes have been reviewed.
- [ ] The release branch and commit message follow the conventions in this tutorial.
- [ ] The pull request contains the intended changes and is ready for QA review.

**After QA approval:** Merge the pull request according to the project's established workflow.

## Verification

The Bash extraction and renaming commands were tested on Ubuntu 24.04.1 LTS using Bash 5.2.21(1)-release (x86_64-pc-linux-gnu) and synthetic ZIP archives. The test XML files were checked for well-formedness using Python's XML parser.

The Git file-discovery, staging, diff-review, and commit commands were tested using Git 2.53.0 in a local repository with one new and one modified XML file.

These tests verify the command behaviour described above. The fictional `.gpack` naming convention and repository layout illustrate how the commands can be used in a generic content-release workflow; they do not demonstrate compatibility with any real platform. Pushing a branch and opening a pull request were not part of these tests.

## References

The following are placeholders for supporting documentation. They are not live links to any internal documents.

- **Resource Revision Guidelines**: fictional reference placeholder.
- **Deprecated Terms**: fictional reference placeholder.
- **Validating Glossaries**: fictional reference placeholder.
- **Batch Export**: fictional reference placeholder.
- **Batch Import**: fictional reference placeholder.
- **Running Phrase-Set Autotests**: fictional reference placeholder.
- **Resource Export Guidelines**: fictional reference placeholder.
