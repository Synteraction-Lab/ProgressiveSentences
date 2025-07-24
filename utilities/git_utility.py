import pygit2


def get_git_branch():
    try:
        # Open the repository located at the current directory
        repo = pygit2.Repository('.')
        # Get the name of the current branch
        branch_name = repo.head.shorthand
        return branch_name
    except Exception as e:
        print("Exception occurred:", str(e))
        return None


if __name__ == "__main__":
    branch_name = get_git_branch()
    if branch_name:
        print("Current Git branch:", branch_name)
    else:
        print("Failed to retrieve the Git branch name.")
