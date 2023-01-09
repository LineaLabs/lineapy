# Recommended Practices

## Organize each PR with relevant changes

To maintain a linear/cleaner project history, the project was set up to apply “squashing” when merging a PR.
That is, if a PR contains more than one commit, GitHub will combine them into a single commit where the summary
equals the PR title (followed by the PR number) and the description consists of commit messages for all squashed
commits (in date order). Hence, we ask you to organize each PR with related changes only so that it can represent
a single unit of meaningful change.
